"""
OCR 解析器

處理掃描式 PDF 的圖像辨識與資料提取。
使用 Tesseract OCR 進行繁體中文辨識。

需要安裝：
- tesseract: brew install tesseract tesseract-lang
- pytesseract: pip install pytesseract
- pdf2image: pip install pdf2image
- Poppler: brew install poppler (pdf2image 依賴)
"""
import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

try:
    import pytesseract
    from PIL import Image, ImageFilter, ImageEnhance
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    from pdf2image import convert_from_path
    HAS_PDF2IMAGE = True
except ImportError:
    HAS_PDF2IMAGE = False

from .models import AssetQualityRow, ParseResult, ParseStatus, SUBJECT_MAPPING


@dataclass
class OCRConfig:
    """OCR 設定"""
    language: str = "chi_tra+eng"  # 繁體中文 + 英文（處理數字）
    dpi: int = 400                 # 提高解析度
    psm: int = 6                   # Page segmentation mode (6 = uniform block of text)
    preprocess: bool = True        # 是否預處理圖片


class OCRParser:
    """
    OCR 解析器
    
    用於處理掃描式 PDF（無法直接提取文字的 PDF）。
    
    使用方式:
        parser = OCRParser()
        result = parser.parse_pdf('path/to/scanned.pdf', '銀行名稱')
    """
    
    def __init__(self, config: OCRConfig = None):
        """
        初始化 OCR 解析器
        
        Args:
            config: OCR 設定，預設使用繁體中文
        """
        self.config = config or OCRConfig()
        self._check_dependencies()
    
    def _check_dependencies(self):
        """檢查相依套件"""
        if not HAS_TESSERACT:
            raise ImportError(
                "需要安裝 pytesseract: pip install pytesseract\n"
                "以及 Tesseract OCR: brew install tesseract tesseract-lang"
            )
        if not HAS_PDF2IMAGE:
            raise ImportError(
                "需要安裝 pdf2image: pip install pdf2image\n"
                "以及 Poppler: brew install poppler"
            )
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        預處理圖片以提高 OCR 準確率
        
        Args:
            image: 原始圖片
            
        Returns:
            預處理後的圖片
        """
        # 轉為灰階
        if image.mode != 'L':
            image = image.convert('L')
        
        # 增強對比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # 銳化
        image = image.filter(ImageFilter.SHARPEN)
        
        return image
    
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        將 PDF 轉換為圖片
        
        Args:
            pdf_path: PDF 檔案路徑
            
        Returns:
            圖片列表
        """
        images = convert_from_path(pdf_path, dpi=self.config.dpi)
        
        if self.config.preprocess:
            images = [self.preprocess_image(img) for img in images]
        
        return images
    
    def image_to_text(self, image: Image.Image) -> str:
        """
        將圖片轉換為文字
        
        Args:
            image: PIL Image 物件
            
        Returns:
            OCR 辨識的文字
        """
        custom_config = f'--psm {self.config.psm} --oem 3'
        return pytesseract.image_to_string(
            image, 
            lang=self.config.language,
            config=custom_config
        )
    
    def find_asset_quality_page(self, images: List[Image.Image]) -> Tuple[int, str]:
        """
        找出包含資產品質資料的頁面
        
        Args:
            images: PDF 頁面圖片列表
            
        Returns:
            (頁碼, 文字內容) 或 (-1, "") 如果找不到
        """
        # 優先關鍵字（需要有這些才是資料頁，而非目錄頁）
        data_keywords = ["企業金融", "消費金融", "放款總額", "企業", "消費"]
        # 一般關鍵字
        general_keywords = ["資產品質", "逾期放款"]
        
        best_page = -1
        best_text = ""
        best_score = 0
        
        for i, image in enumerate(images):
            text = self.image_to_text(image)
            
            # 計算分數
            score = 0
            for kw in data_keywords:
                if kw in text:
                    score += 2
            for kw in general_keywords:
                if kw in text:
                    score += 1
            
            # 需要至少包含一個資料關鍵字
            has_data_keyword = any(kw in text for kw in data_keywords)
            
            if has_data_keyword and score > best_score:
                best_score = score
                best_page = i
                best_text = text
        
        return best_page, best_text
    
    def extract_data_from_text(
        self,
        text: str,
        year: str,
        quarter: str,
        bank_name: str,
    ) -> List[AssetQualityRow]:
        """
        從 OCR 文字中提取資產品質資料
        
        Args:
            text: OCR 辨識的文字
            year: 年度
            quarter: 季度
            bank_name: 銀行名稱
            
        Returns:
            資產品質資料列表
        """
        results = []
        seen_subjects = set()
        
        # 清理 OCR 文字中的雜訊
        text = self._clean_ocr_text(text)
        
        # 逐行解析
        lines = text.split('\n')
        
        for line in lines:
            row = self._parse_line(line, year, quarter, bank_name)
            if row and row.subject not in seen_subjects:
                # 只保留第一筆（通常是當期資料）
                seen_subjects.add(row.subject)
                results.append(row)
        
        return results
    
    def _clean_ocr_text(self, text: str) -> str:
        """清理 OCR 文字中的雜訊"""
        # 移除多餘空格但保留換行
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # 移除連續空格
            line = re.sub(r'\s+', ' ', line).strip()
            # 移除常見 OCR 錯誤字元
            line = line.replace('"', '').replace('「', '').replace('」', '')
            line = line.replace('『', '').replace('』', '')
            if line:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)
    
    def _extract_numbers_from_line(self, line: str) -> List[float]:
        """從一行中提取所有數字"""
        # 移除干擾字元
        line = line.replace('|', ' ').replace(':', ' ').replace('和', '')
        line = line.replace('語', '').replace('有', '').replace('上', '')
        
        # 找出所有數字（包含逗號和小數點）
        numbers = []
        for match in re.finditer(r'[\d,]+\.?\d*', line):
            num_str = match.group().replace(',', '')
            if num_str and num_str != '.':
                try:
                    num = float(num_str)
                    numbers.append(num)
                except ValueError:
                    continue
        
        return numbers
    
    def _parse_line(
        self,
        line: str,
        year: str,
        quarter: str,
        bank_name: str,
    ) -> Optional[AssetQualityRow]:
        """解析單行資料"""
        
        # 正規化行（移除空格以便關鍵字比對）
        line_normalized = line.replace(' ', '').replace('　', '')
        
        # 定義各類別的關鍵字（支援 OCR 錯誤變體）
        category_keywords = {
            "企業金融_擔保": [
                ("企業金融", "擔保"),
                ("企業", "擔保"),
                ("企", "擔保"),
                ("金融", "擔保"),
            ],
            "企業金融_無擔保": [
                ("企業金融", "無擔保"),
                ("企業", "無擔保"),
                ("無擔保",),  # 在企業金融區塊內
            ],
            "消費金融_住宅抵押貸款": [
                ("住宅抵押",),
                ("住宅", "抵押"),
                ("抵押貸款",),
            ],
            "消費金融_現金卡": [
                ("現金卡",),
            ],
            "消費金融_小額純信用貸款": [
                ("小額純信用",),
                ("小額", "信用"),
                ("純信用貸款",),
            ],
            "消費金融_其他_擔保": [
                ("其他", "擔保"),
            ],
            "消費金融_其他_無擔保": [
                ("其他", "無擔保"),
            ],
            "合計": [
                ("放款業務合計",),
                ("合計",),
            ],
        }
        
        # 檢查每個類別
        matched_category = None
        for category, keyword_groups in category_keywords.items():
            for keywords in keyword_groups:
                if all(kw in line_normalized for kw in keywords):
                    # 特殊處理：區分「其他_擔保」和「其他_無擔保」
                    if category == "消費金融_其他_擔保" and "無擔保" in line_normalized:
                        continue
                    # 特殊處理：區分「企業金融_擔保」和「企業金融_無擔保」
                    if category == "企業金融_擔保" and "無擔保" in line_normalized:
                        continue
                    matched_category = category
                    break
            if matched_category:
                break
        
        if not matched_category:
            return None
        
        # 提取數字
        numbers = self._extract_numbers_from_line(line)
        
        # 需要至少 3 個數字：逾期金額、總額、比率
        if len(numbers) < 3:
            return None
        
        # 通常格式是：逾期金額、總額、比率、...
        # 找出合理的數值組合
        overdue = None
        total = None
        ratio = None
        
        for i, num in enumerate(numbers):
            # 比率通常是小數（< 100）
            if num < 100 and ratio is None:
                # 可能是比率
                if i >= 2:  # 比率通常在第 3 個位置之後
                    ratio = num
                    # 回頭找逾期和總額
                    if i >= 2:
                        overdue = numbers[i-2] if i >= 2 else numbers[0]
                        total = numbers[i-1] if i >= 1 else numbers[1]
                    break
        
        # 備用方案：按順序取
        if overdue is None and len(numbers) >= 3:
            # 找最大的數字作為總額
            total_idx = max(range(len(numbers)), key=lambda i: numbers[i])
            total = numbers[total_idx]
            
            # 逾期金額通常在總額之前
            if total_idx > 0:
                overdue = numbers[total_idx - 1]
            else:
                overdue = numbers[0]
            
            # 比率通常在總額之後，且 < 100
            for i in range(total_idx + 1, len(numbers)):
                if numbers[i] < 100:
                    ratio = numbers[i]
                    break
            
            if ratio is None:
                ratio = 0.0
        
        if overdue is None or total is None:
            return None
        
        # 合理性檢查
        if total <= 0:
            return None
        if ratio is not None and ratio > 100:
            ratio = 0.0
        
        return AssetQualityRow(
            year=year,
            quarter=quarter,
            subject=SUBJECT_MAPPING.get(matched_category, matched_category),
            overdue_amount=overdue,
            total_loan=total,
            overdue_ratio=ratio if ratio else 0.0,
            bank_name=bank_name,
        )
    
    def parse_pdf(self, pdf_path: str, bank_name: str = "") -> ParseResult:
        """
        解析掃描式 PDF
        
        Args:
            pdf_path: PDF 檔案路徑
            bank_name: 銀行名稱
            
        Returns:
            ParseResult: 解析結果
        """
        path = Path(pdf_path)
        
        if not path.exists():
            return ParseResult(
                status=ParseStatus.NO_FILE,
                message=f"檔案不存在: {pdf_path}",
                file_path=pdf_path,
            )
        
        # 從檔名推斷資訊
        if not bank_name:
            parts = path.stem.split('_')
            if len(parts) >= 2:
                bank_name = parts[1]
        
        # 從檔名提取年度季度
        match = re.search(r'(\d+)Q(\d)', path.name)
        year = match.group(1) if match else ""
        quarter = f"Q{match.group(2)}" if match else ""
        
        try:
            print(f"[OCR] 轉換 PDF 為圖片...")
            images = self.pdf_to_images(pdf_path)
            print(f"[OCR] 共 {len(images)} 頁")
            
            print(f"[OCR] 搜尋資產品質頁面...")
            page_idx, text = self.find_asset_quality_page(images)
            
            if page_idx < 0:
                return ParseResult(
                    status=ParseStatus.FAILED,
                    message="找不到資產品質頁面",
                    bank_name=bank_name,
                    file_path=pdf_path,
                )
            
            print(f"[OCR] 找到資產品質頁面: 第 {page_idx + 1} 頁")
            
            # 提取資料
            rows = self.extract_data_from_text(text, year, quarter, bank_name)
            
            if not rows:
                return ParseResult(
                    status=ParseStatus.FAILED,
                    message="無法從 OCR 文字提取資料",
                    bank_name=bank_name,
                    file_path=pdf_path,
                )
            
            status = ParseStatus.SUCCESS if len(rows) == 8 else ParseStatus.PARTIAL
            
            return ParseResult(
                status=status,
                rows=rows,
                message=f"OCR 解析成功: {len(rows)}/8 類別",
                bank_name=bank_name,
                file_path=pdf_path,
            )
            
        except Exception as e:
            return ParseResult(
                status=ParseStatus.FAILED,
                message=f"OCR 解析錯誤: {str(e)}",
                bank_name=bank_name,
                file_path=pdf_path,
            )


def is_scanned_pdf(pdf_path: str) -> bool:
    """
    檢查 PDF 是否為掃描式（無法直接提取文字）
    
    Args:
        pdf_path: PDF 檔案路徑
        
    Returns:
        True 如果是掃描式 PDF
    """
    try:
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            # 檢查前 5 頁
            text_found = False
            for i in range(min(5, len(pdf.pages))):
                text = pdf.pages[i].extract_text() or ""
                # 如果某頁有超過 200 字元的文字，就認為不是掃描式
                if len(text.strip()) > 200:
                    # 再檢查是否包含關鍵數據字元
                    if any(char.isdigit() for char in text):
                        text_found = True
                        break
            
            return not text_found
        
    except Exception:
        return True
