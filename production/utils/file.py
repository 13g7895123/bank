"""
檔案處理工具
"""
import os
from pathlib import Path
from typing import List, Optional


def ensure_dir(dir_path: str) -> Path:
    """
    確保目錄存在，若不存在則建立
    
    Args:
        dir_path: 目錄路徑
        
    Returns:
        Path 物件
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_path(
    data_dir: str,
    bank_code: int,
    bank_name: str,
    year: int,
    quarter: int,
) -> Path:
    """
    取得標準化的檔案路徑
    
    格式: {data_dir}/{year}Q{quarter}/{bank_code}_{bank_name}_{year}Q{quarter}.pdf
    
    Args:
        data_dir: 資料目錄
        bank_code: 銀行代碼
        bank_name: 銀行名稱
        year: 民國年
        quarter: 季度
        
    Returns:
        Path 物件
    """
    return Path(data_dir) / f"{year}Q{quarter}" / f"{bank_code}_{bank_name}_{year}Q{quarter}.pdf"


def list_pdf_files(data_dir: str, year_quarter: str = None) -> List[Path]:
    """
    列出資料目錄中的 PDF 檔案
    
    Args:
        data_dir: 資料目錄
        year_quarter: 年度季度（如 114Q1），若指定則只列出該目錄
        
    Returns:
        PDF 檔案路徑列表
    """
    base_path = Path(data_dir)
    
    if year_quarter:
        target_dir = base_path / year_quarter
        if target_dir.exists():
            return sorted(target_dir.glob("*.pdf"))
        return []
    
    # 列出所有子目錄中的 PDF
    pdf_files = []
    for subdir in sorted(base_path.iterdir()):
        if subdir.is_dir() and "Q" in subdir.name:
            pdf_files.extend(sorted(subdir.glob("*.pdf")))
    
    return pdf_files


def parse_filename(filename: str) -> dict:
    """
    解析標準化的檔案名稱
    
    格式: {bank_code}_{bank_name}_{year}Q{quarter}.pdf
    
    Args:
        filename: 檔案名稱
        
    Returns:
        包含 bank_code, bank_name, year, quarter 的字典
    """
    import re
    
    stem = Path(filename).stem
    
    # 嘗試解析標準格式
    match = re.match(r'(\d+)_(.+)_(\d+)Q(\d)', stem)
    if match:
        return {
            'bank_code': int(match.group(1)),
            'bank_name': match.group(2),
            'year': int(match.group(3)),
            'quarter': int(match.group(4)),
        }
    
    return {
        'bank_code': 0,
        'bank_name': stem,
        'year': 0,
        'quarter': 0,
    }


def get_available_quarters(data_dir: str) -> List[str]:
    """
    取得資料目錄中可用的年度季度列表
    
    Args:
        data_dir: 資料目錄
        
    Returns:
        年度季度列表（如 ['113Q4', '114Q1']）
    """
    base_path = Path(data_dir)
    if not base_path.exists():
        return []
    
    quarters = []
    for subdir in sorted(base_path.iterdir()):
        if subdir.is_dir() and "Q" in subdir.name:
            # 確認目錄中有 PDF 檔案
            if list(subdir.glob("*.pdf")):
                quarters.append(subdir.name)
    
    return quarters
