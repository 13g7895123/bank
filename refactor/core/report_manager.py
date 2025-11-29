"""
報表管理器

統一管理 PDF 解析與報表生成邏輯。
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable
import warnings

import pandas as pd
import pdfplumber

from .models import (
    ParseStatus,
    ParseResult,
    AssetQualityRow,
    SUBJECT_MAPPING,
    SUBJECT_CATEGORIES,
)


class ReportManager:
    """
    報表管理器
    
    負責：
    1. 解析銀行財報 PDF
    2. 提取資產品質資料
    3. 生成 Excel 報表
    
    使用方式:
        manager = ReportManager()
        
        # 解析單一 PDF
        result = manager.parse_pdf('data/114Q1/31_玉山商業銀行_114Q1.pdf')
        
        # 生成報表
        df = manager.generate_report('data/114Q1', 'output/114Q1_report.xlsx')
    """
    
    def __init__(self):
        """初始化報表管理器"""
        # 抑制 pdfplumber 的警告
        warnings.filterwarnings('ignore', category=UserWarning)
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        正規化文字，移除空格和換行
        
        用於處理 PDF 中 "企 業\n金 融" 等格式問題
        """
        if text is None:
            return ""
        return str(text).replace(" ", "").replace("\n", "").replace("　", "").strip()
    
    @staticmethod
    def parse_number(value) -> float:
        """解析數字，移除千分位逗號和貨幣符號"""
        if value is None:
            return 0.0
        val_str = str(value).strip()
        if val_str in ['-', '', '－', '-%', '-', '- %', '- ％', 'None']:
            return 0.0
        cleaned = val_str.replace(',', '').replace(' ', '')
        cleaned = cleaned.replace('$', '').replace('＄', '')
        cleaned = cleaned.replace('%', '').replace('％', '')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    @staticmethod
    def parse_ratio(value) -> float:
        """解析比率"""
        if value is None:
            return 0.0
        val_str = str(value).strip()
        if val_str in ['-', '', '－', '-%', '-', '- %', '- ％', 'None']:
            return 0.0
        cleaned = val_str.replace('%', '').replace('％', '').replace(',', '')
        cleaned = cleaned.replace('$', '').replace('＄', '').replace(' ', '')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def find_asset_quality_pages(self, pdf: pdfplumber.PDF) -> List[tuple]:
        """
        找出包含「資產品質」的頁面
        
        Returns:
            List of (page, has_table) tuples
        """
        candidates = []
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            
            # 檢查是否包含資產品質相關關鍵字
            if "資產品質" in text or "逾期放款" in text:
                # 檢查是否包含表格資料特徵
                has_table = "企業金融" in text or "消費金融" in text
                tables = page.extract_tables()
                has_table = has_table or (tables and len(tables) > 0)
                candidates.append((i, page, has_table))
        
        # 優先返回有表格的頁面
        candidates.sort(key=lambda x: (not x[2], x[0]))
        return [(page, has_table) for _, page, has_table in candidates]
    
    def extract_from_table(
        self,
        table: list,
        year: str,
        quarter: str,
        bank_name: str,
    ) -> List[AssetQualityRow]:
        """從表格資料提取資產品質資訊"""
        results = []
        current_category = ""
        
        for row in table:
            if not row or len(row) < 6:
                continue
            
            # 正規化欄位文字
            col0 = self.normalize_text(row[0])
            col1 = self.normalize_text(row[1]) if len(row) > 1 else ""
            col2 = self.normalize_text(row[2]) if len(row) > 2 else ""
            
            # 數值欄位
            overdue_amount = row[3] if len(row) > 3 else ""
            total_loan = row[4] if len(row) > 4 else ""
            overdue_ratio = row[5] if len(row) > 5 else ""
            
            subject = None
            
            # 判斷資料類型
            if "企業金融" in col0:
                current_category = "企業金融"
                if "擔保" in col1 and "無" not in col1:
                    subject = "企業金融_擔保"
            elif "消費金融" in col0:
                current_category = "消費金融"
                if "住宅" in col1 or "抵押" in col1:
                    subject = "消費金融_住宅抵押貸款"
            elif current_category == "企業金融" and "無擔保" in col1:
                subject = "企業金融_無擔保"
            elif "住宅" in col1 or "抵押" in col1:
                subject = "消費金融_住宅抵押貸款"
            elif "現金卡" in col1:
                subject = "消費金融_現金卡"
            elif "小額" in col1 or "純信用" in col1 or "信用貸款" in col1:
                subject = "消費金融_小額純信用貸款"
            elif "其他" in col1:
                if "擔保" in col2 and "無" not in col2:
                    subject = "消費金融_其他_擔保"
                elif "無擔保" in col2:
                    subject = "消費金融_其他_無擔保"
            elif "無擔保" in col2 and current_category == "消費金融":
                subject = "消費金融_其他_無擔保"
            elif "擔保" in col2 and current_category == "消費金融" and "無" not in col2:
                subject = "消費金融_其他_擔保"
            elif "合計" in col0 or "放款業務合計" in col0:
                subject = "合計"
            
            if subject:
                results.append(AssetQualityRow(
                    year=year,
                    quarter=quarter,
                    subject=SUBJECT_MAPPING.get(subject, subject),
                    overdue_amount=self.parse_number(overdue_amount),
                    total_loan=self.parse_number(total_loan),
                    overdue_ratio=self.parse_ratio(overdue_ratio),
                    bank_name=bank_name,
                ))
        
        return results
    
    def extract_year_quarter_from_filename(self, filename: str) -> tuple:
        """從檔名提取年度季度"""
        import re
        match = re.search(r'(\d+)Q(\d)', filename)
        if match:
            return match.group(1), f"Q{match.group(2)}"
        return "", ""
    
    def parse_pdf(self, pdf_path: str, bank_name: str = "") -> ParseResult:
        """
        解析單一 PDF 檔案
        
        Args:
            pdf_path: PDF 檔案路徑
            bank_name: 銀行名稱（可從檔名推斷）
            
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
        
        # 從檔名推斷銀行名稱和年度季度
        if not bank_name:
            parts = path.stem.split('_')
            if len(parts) >= 2:
                bank_name = parts[1]
        
        year, quarter = self.extract_year_quarter_from_filename(path.name)
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # 找到資產品質頁面
                pages_info = self.find_asset_quality_pages(pdf)
                
                if not pages_info:
                    return ParseResult(
                        status=ParseStatus.FAILED,
                        message="找不到資產品質頁面",
                        bank_name=bank_name,
                        file_path=pdf_path,
                    )
                
                results = []
                
                # 嘗試從各頁面提取資料
                for page, has_table in pages_info:
                    if has_table:
                        tables = page.extract_tables()
                        for table in tables:
                            if len(table) >= 5:
                                rows = self.extract_from_table(table, year, quarter, bank_name)
                                if rows:
                                    results.extend(rows)
                                    break
                    
                    if results:
                        break
                
                # 去重
                seen = set()
                unique_results = []
                for row in results:
                    if row.subject not in seen:
                        seen.add(row.subject)
                        unique_results.append(row)
                
                if not unique_results:
                    return ParseResult(
                        status=ParseStatus.FAILED,
                        message="無法解析資料",
                        bank_name=bank_name,
                        file_path=pdf_path,
                    )
                
                status = ParseStatus.SUCCESS if len(unique_results) == 8 else ParseStatus.PARTIAL
                
                return ParseResult(
                    status=status,
                    rows=unique_results,
                    message=f"解析成功: {len(unique_results)}/8 類別",
                    bank_name=bank_name,
                    file_path=pdf_path,
                )
                
        except Exception as e:
            return ParseResult(
                status=ParseStatus.FAILED,
                message=f"解析錯誤: {str(e)}",
                bank_name=bank_name,
                file_path=pdf_path,
            )
    
    def generate_report(
        self,
        data_dir: str,
        output_path: str,
        year_quarter: str = None,
        progress_callback: Callable[[str, ParseResult], None] = None,
    ) -> Optional[pd.DataFrame]:
        """
        生成資產品質報表
        
        Args:
            data_dir: PDF 資料目錄
            output_path: 輸出 Excel 檔案路徑
            year_quarter: 年度季度（如 114Q1）
            progress_callback: 進度回調函數
            
        Returns:
            DataFrame 或 None
        """
        data_path = Path(data_dir)
        if not data_path.exists():
            print(f"[錯誤] 資料目錄不存在: {data_dir}")
            return None
        
        # 取得所有 PDF 檔案
        pdf_files = sorted(data_path.glob("*.pdf"))
        if not pdf_files:
            print(f"[錯誤] 找不到 PDF 檔案: {data_dir}")
            return None
        
        print(f"找到 {len(pdf_files)} 個 PDF 檔案")
        print("=" * 60)
        
        all_rows = []
        success_count = 0
        fail_count = 0
        
        for pdf_file in pdf_files:
            # 從檔名取得銀行名稱
            parts = pdf_file.stem.split('_')
            bank_name = parts[1] if len(parts) >= 2 else pdf_file.stem
            
            result = self.parse_pdf(str(pdf_file), bank_name)
            
            if progress_callback:
                progress_callback(bank_name, result)
            
            if result.is_success or result.status == ParseStatus.PARTIAL:
                all_rows.extend(result.rows)
                success_count += 1
                print(f"✓ {bank_name}: {result.category_count} 筆資料")
            else:
                fail_count += 1
                print(f"✗ {bank_name}: {result.message}")
        
        print("=" * 60)
        print(f"成功: {success_count}, 失敗: {fail_count}")
        
        if not all_rows:
            print("[錯誤] 無法提取任何資料")
            return None
        
        # 建立 DataFrame
        df = pd.DataFrame([row.to_dict() for row in all_rows])
        
        # 確保輸出目錄存在
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 輸出 Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        print(f"\n報表已輸出: {output_path}")
        print(f"共 {len(df)} 筆資料（{df['銀行名稱'].nunique()} 家銀行）")
        
        return df
    
    def get_parse_summary(self, results: Dict[str, ParseResult]) -> dict:
        """取得解析結果統計摘要"""
        summary = {
            'total': len(results),
            'success': 0,
            'partial': 0,
            'failed': 0,
            'total_rows': 0,
            'incomplete_banks': [],
        }
        
        for bank_name, result in results.items():
            if result.status == ParseStatus.SUCCESS:
                summary['success'] += 1
            elif result.status == ParseStatus.PARTIAL:
                summary['partial'] += 1
                summary['incomplete_banks'].append({
                    'name': bank_name,
                    'count': result.category_count,
                })
            else:
                summary['failed'] += 1
            
            summary['total_rows'] += result.category_count
        
        return summary
