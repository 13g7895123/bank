"""
報表生成模組

從下載的銀行財報 PDF 中提取「資產品質」表格資料，
並輸出為 Excel 報表格式。

支援兩種解析模式：
1. 表格模式 (pdfplumber extract_tables) - 適用於標準表格格式
2. 文字模式 (純文字解析) - 適用於特殊排版的 PDF
"""

import os
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import pandas as pd
import pdfplumber


@dataclass
class AssetQualityRow:
    """資產品質資料列"""
    year: str                    # 資料年度（民國年）
    quarter: str                 # 季度
    subject: str                 # 業務別項目
    overdue_amount: float        # 逾期放款金額（仟元）
    total_loan: float            # 放款總額（仟元）
    overdue_ratio: float         # 逾放比率
    bank_name: str               # 銀行名稱


# 8 個業務別項目對應表
SUBJECT_MAPPING = {
    "企業金融_擔保": "01_企業金融_擔保",
    "企業金融_無擔保": "02_企業金融_無擔保",
    "消費金融_住宅抵押貸款": "03_消費金融_住宅抵押貸款",
    "消費金融_現金卡": "04_消費金融_現金卡",
    "消費金融_小額純信用貸款": "05_消費金融_小額純信用貸款",
    "消費金融_其他_擔保": "06_消費金融_其他_擔保",
    "消費金融_其他_無擔保": "07_消費金融_其他_無擔保",
    "合計": "08_合計",
}


def parse_number(value: str) -> float:
    """
    解析數字字串，移除千分位逗號和貨幣符號。
    如果是 '-' 或空值則返回 0。
    """
    if value is None:
        return 0.0
    val_str = str(value).strip()
    if val_str in ['-', '', '－', '-%', '-', '- %', '- ％']:
        return 0.0
    # 移除空白、千分位逗號、貨幣符號
    cleaned = val_str.replace(',', '').replace(' ', '')
    cleaned = cleaned.replace('$', '').replace('＄', '')
    cleaned = cleaned.replace('%', '').replace('％', '')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_ratio(value: str) -> float:
    """
    解析比率字串。
    如果是 '-' 或空值則返回 0。
    """
    if value is None:
        return 0.0
    val_str = str(value).strip()
    if val_str in ['-', '', '－', '-%', '-', '- %', '- ％']:
        return 0.0
    cleaned = val_str.replace('%', '').replace('％', '').replace(',', '')
    cleaned = cleaned.replace('$', '').replace('＄', '').replace(' ', '')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_year_quarter(date_str: str) -> tuple[str, str]:
    """
    從日期字串提取年度和季度。
    例如: "114年03月31日" -> ("114", "Q1")
    """
    # 匹配各種日期格式
    patterns = [
        r'(\d+)年(\d+)月',           # 114年03月
        r'(\d+)\.(\d+)\.\d+',        # 114.3.31
        r'(\d+)\s*年\s*(\d+)\s*月',  # 114 年 3 月
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            year = match.group(1)
            month = int(match.group(2))
            # 根據月份判斷季度
            if month <= 3:
                quarter = "Q1"
            elif month <= 6:
                quarter = "Q2"
            elif month <= 9:
                quarter = "Q3"
            else:
                quarter = "Q4"
            return year, quarter
    return "", ""


def extract_year_quarter_from_filename(filename: str) -> tuple[str, str]:
    """從檔名提取年度和季度"""
    match = re.search(r'(\d+)Q(\d+)', filename)
    if match:
        return match.group(1), f"Q{match.group(2)}"
    return "", ""


def find_asset_quality_pages(pdf: pdfplumber.PDF) -> list[tuple]:
    """
    找到所有包含「資產品質」的頁面，按相關性排序。
    """
    candidates = []
    
    for page in pdf.pages:
        text = page.extract_text() or ""
        if "資產品質" not in text:
            continue
            
        # 檢查是否有表格
        tables = page.extract_tables()
        has_table = len(tables) > 0
        
        # 計算匹配分數
        score = 0
        if "逾期放款" in text:
            score += 10
        if "企業金融" in text or "消費金融" in text:
            score += 5
        if "放款業務合計" in text or "合計" in text:
            score += 5
        if "擔保" in text and "無擔保" in text:
            score += 5
        if has_table:
            score += 20
        
        candidates.append((score, page, has_table))
    
    # 按分數排序
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [(page, has_table) for _, page, has_table in candidates]


def extract_from_table(table: list, year: str, quarter: str, bank_name: str) -> list[AssetQualityRow]:
    """從表格資料提取資產品質資訊"""
    results = []
    current_category = ""
    
    for row in table:
        if not row or len(row) < 6:
            continue
        
        # 清理欄位
        col0 = (str(row[0]) if row[0] else "").replace('\n', '').strip()
        col1 = (str(row[1]) if len(row) > 1 and row[1] else "").replace('\n', '').strip()
        col2 = (str(row[2]) if len(row) > 2 and row[2] else "").replace('\n', '').strip()
        
        # 數值欄位（當期資料）
        overdue_amount = row[3] if len(row) > 3 else ""
        total_loan = row[4] if len(row) > 4 else ""
        overdue_ratio = row[5] if len(row) > 5 else ""
        
        subject = None
        
        # 判斷資料類型
        if "企業" in col0 and "金融" in col0:
            current_category = "企業金融"
            if "擔保" in col1 or "擔 保" in col1:
                subject = "企業金融_擔保"
        elif "消費" in col0 and "金融" in col0:
            current_category = "消費金融"
            if "住宅" in col1 or "抵押" in col1:
                subject = "消費金融_住宅抵押貸款"
        elif current_category == "企業金融" and ("無擔保" in col1 or "無 擔 保" in col1):
            subject = "企業金融_無擔保"
        elif "住宅" in col1 or "抵押" in col1:
            subject = "消費金融_住宅抵押貸款"
        elif "現金卡" in col1:
            subject = "消費金融_現金卡"
        elif "小額" in col1 or "純信用" in col1 or "信用貸款" in col1:
            subject = "消費金融_小額純信用貸款"
        elif "其他" in col1 or "其 他" in col1:
            if "擔保" in col2 or "擔 保" in col2:
                subject = "消費金融_其他_擔保"
            elif "無擔保" in col2 or "無 擔 保" in col2 or "無擔" in col2:
                subject = "消費金融_其他_無擔保"
        elif ("無擔保" in col2 or "無 擔 保" in col2) and current_category == "消費金融":
            subject = "消費金融_其他_無擔保"
        elif ("擔保" in col2 or "擔 保" in col2) and current_category == "消費金融" and "無" not in col2:
            subject = "消費金融_其他_擔保"
        elif "合計" in col0 or "放款業務合計" in col0:
            subject = "合計"
        
        if subject:
            results.append(AssetQualityRow(
                year=year,
                quarter=quarter,
                subject=SUBJECT_MAPPING.get(subject, subject),
                overdue_amount=parse_number(overdue_amount),
                total_loan=parse_number(total_loan),
                overdue_ratio=parse_ratio(overdue_ratio),
                bank_name=bank_name,
            ))
    
    return results


def extract_from_text(text: str, year: str, quarter: str, bank_name: str) -> list[AssetQualityRow]:
    """
    從純文字提取資產品質資訊（用於無法提取表格的 PDF）。
    這是備援方案，準確度較低。
    """
    results = []
    
    # 定義要尋找的項目和對應的正則表達式
    patterns = [
        ("企業金融_擔保", r"擔\s*保\s*[\$\s]*([\d,]+)\s+([\d,]+)\s+([\d.]+)\s*%?"),
        ("企業金融_無擔保", r"無\s*擔\s*保\s*[\$\s]*([\d,\-]+)\s+([\d,]+)\s+([\d.\-]+)\s*%?"),
        ("消費金融_住宅抵押貸款", r"住宅抵押貸款[^0-9]*[\$\s]*([\d,]+)\s+([\d,]+)\s+([\d.]+)\s*%?"),
        ("消費金融_現金卡", r"現金卡[^0-9]*[\$\s]*([\d,\-]+)\s+([\d,\-]+)\s+([\d.\-]+)\s*%?"),
        ("消費金融_小額純信用貸款", r"小額純?信用貸款[^0-9]*[\$\s]*([\d,]+)\s+([\d,]+)\s+([\d.]+)\s*%?"),
        ("合計", r"放款業務合計[^0-9]*[\$\s]*([\d,]+)\s+([\d,]+)\s+([\d.]+)\s*%?"),
    ]
    
    for subject, pattern in patterns:
        match = re.search(pattern, text)
        if match:
            results.append(AssetQualityRow(
                year=year,
                quarter=quarter,
                subject=SUBJECT_MAPPING.get(subject, subject),
                overdue_amount=parse_number(match.group(1)),
                total_loan=parse_number(match.group(2)),
                overdue_ratio=parse_ratio(match.group(3)),
                bank_name=bank_name,
            ))
    
    return results


def extract_asset_quality_data(pdf_path: str, bank_name: str) -> list[AssetQualityRow]:
    """
    從 PDF 提取資產品質資料。
    
    Args:
        pdf_path: PDF 檔案路徑
        bank_name: 銀行名稱
        
    Returns:
        資產品質資料列表（最多 8 筆資料）
    """
    results = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 找到相關頁面
            pages_info = find_asset_quality_pages(pdf)
            if not pages_info:
                print(f"[警告] {bank_name}: 找不到資產品質頁面")
                return results
            
            # 從檔名預先提取年度季度
            filename = os.path.basename(pdf_path)
            default_year, default_quarter = extract_year_quarter_from_filename(filename)
            
            # 嘗試從各頁面提取資料
            for page, has_table in pages_info:
                text = page.extract_text() or ""
                
                # 提取年度季度
                year, quarter = extract_year_quarter(text)
                if not year:
                    year, quarter = default_year, default_quarter
                
                if has_table:
                    # 表格模式
                    tables = page.extract_tables()
                    for table in tables:
                        if len(table) >= 5:  # 至少需要 5 列才是有效表格
                            rows = extract_from_table(table, year, quarter, bank_name)
                            if rows:
                                results.extend(rows)
                                break
                
                if not results:
                    # 文字模式（備援）
                    rows = extract_from_text(text, year, quarter, bank_name)
                    if rows:
                        results.extend(rows)
                
                # 如果已經有結果就不再繼續
                if results:
                    break
            
            # 去重（按 subject）
            seen = set()
            unique_results = []
            for row in results:
                if row.subject not in seen:
                    seen.add(row.subject)
                    unique_results.append(row)
            
            if not unique_results:
                print(f"[警告] {bank_name}: 無法解析資料（可能是特殊格式）")
            
            return unique_results
    
    except Exception as e:
        print(f"[錯誤] {bank_name}: 解析 PDF 失敗 - {e}")
        import traceback
        traceback.print_exc()
    
    return results


def generate_report(
    data_dir: str,
    output_path: str,
    year_quarter: str = None,
) -> pd.DataFrame:
    """
    生成資產品質報表。
    
    Args:
        data_dir: PDF 資料目錄（例如 data/114Q1）
        output_path: 輸出 Excel 檔案路徑
        year_quarter: 年度季度（例如 114Q1），如果為 None 則從目錄名稱推斷
        
    Returns:
        包含所有銀行資料的 DataFrame
    """
    data_path = Path(data_dir)
    
    # 從目錄名稱推斷年度季度
    if year_quarter is None:
        year_quarter = data_path.name
    
    all_data = []
    success_count = 0
    fail_count = 0
    
    # 掃描所有 PDF 檔案
    pdf_files = sorted(data_path.glob("*.pdf"))
    print(f"找到 {len(pdf_files)} 個 PDF 檔案")
    print("="*60)
    
    for pdf_file in pdf_files:
        # 從檔名提取銀行名稱
        # 格式: "3_合作金庫商業銀行_114Q1.pdf"
        filename = pdf_file.stem  # 移除 .pdf
        parts = filename.split('_')
        if len(parts) >= 2:
            bank_name = parts[1]
        else:
            bank_name = filename
        
        # 提取資料
        rows = extract_asset_quality_data(str(pdf_file), bank_name)
        if rows:
            all_data.extend(rows)
            print(f"✓ {bank_name}: {len(rows)} 筆資料")
            success_count += 1
        else:
            fail_count += 1
    
    print("="*60)
    print(f"成功: {success_count}, 失敗: {fail_count}")
    
    # 轉換為 DataFrame
    if all_data:
        df = pd.DataFrame([
            {
                "資料年度": row.year,
                "季度": row.quarter,
                "業務別項目": row.subject,
                "逾期放款金額(單位：仟元)": row.overdue_amount,
                "放款總額(單位：仟元)": row.total_loan,
                "逾放比率": row.overdue_ratio,
                "銀行名稱": row.bank_name,
            }
            for row in all_data
        ])
        
        # 排序
        df = df.sort_values(by=["銀行名稱", "業務別項目"]).reset_index(drop=True)
        
        # 確保輸出目錄存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 輸出為 Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"\n報表已輸出: {output_path}")
        print(f"共 {len(df)} 筆資料（{success_count} 家銀行）")
        
        return df
    else:
        print("沒有提取到任何資料")
        return pd.DataFrame()


def generate_single_bank_report(
    pdf_path: str,
    bank_name: str,
    output_path: str = None,
) -> pd.DataFrame:
    """
    為單一銀行生成報表（用於測試）。
    
    Args:
        pdf_path: PDF 檔案路徑
        bank_name: 銀行名稱
        output_path: 輸出 Excel 路徑（可選）
        
    Returns:
        該銀行的資產品質 DataFrame
    """
    rows = extract_asset_quality_data(pdf_path, bank_name)
    
    if rows:
        df = pd.DataFrame([
            {
                "資料年度": row.year,
                "季度": row.quarter,
                "業務別項目": row.subject,
                "逾期放款金額(單位：仟元)": row.overdue_amount,
                "放款總額(單位：仟元)": row.total_loan,
                "逾放比率": row.overdue_ratio,
                "銀行名稱": row.bank_name,
            }
            for row in rows
        ])
        
        if output_path:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            df.to_excel(output_path, index=False, engine='openpyxl')
            print(f"報表已輸出: {output_path}")
        
        return df
    
    return pd.DataFrame()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 指定 PDF 檔案測試
        pdf_path = sys.argv[1]
        bank_name = sys.argv[2] if len(sys.argv) > 2 else "測試銀行"
        df = generate_single_bank_report(pdf_path, bank_name)
        print(df.to_string())
    else:
        # 預設處理 data/114Q1 目錄
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / "data" / "114Q1"
        output_path = base_dir / "Output" / "114Q1_資產品質報表.xlsx"
        
        if data_dir.exists():
            df = generate_report(str(data_dir), str(output_path))
            if not df.empty:
                print("\n預覽（前 20 筆）:")
                print(df.head(20).to_string())
        else:
            print(f"資料目錄不存在: {data_dir}")
            print("用法: python report_generator.py [pdf_path] [bank_name]")
