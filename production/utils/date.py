"""
日期處理工具
"""
import re
from typing import Tuple, Optional


def parse_year_quarter(input_str: str) -> Tuple[Optional[int], Optional[int]]:
    """
    解析年度季度字串
    
    支援格式：
    - "114Q1" -> (114, 1)
    - "114 Q1" -> (114, 1)
    - "114q1" -> (114, 1)
    
    Args:
        input_str: 輸入字串
        
    Returns:
        (year, quarter) 元組，解析失敗則回傳 (None, None)
    """
    if not input_str:
        return None, None
    
    input_str = input_str.upper().replace(" ", "")
    match = re.match(r"(\d+)Q(\d)", input_str)
    
    if match:
        year = int(match.group(1))
        quarter = int(match.group(2))
        if 1 <= quarter <= 4:
            return year, quarter
    
    return None, None


def get_quarter_text(quarter: int, style: str = "chinese") -> str:
    """
    取得季度文字
    
    Args:
        quarter: 季度 (1-4)
        style: 文字風格
            - "chinese": 第一季、第二季...
            - "short": Q1、Q2...
            - "month": 3月、6月...
            
    Returns:
        季度文字
    """
    if style == "chinese":
        mapping = {1: "第一季", 2: "第二季", 3: "第三季", 4: "第四季"}
    elif style == "short":
        mapping = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"}
    elif style == "month":
        mapping = {1: "3月", 2: "6月", 3: "9月", 4: "12月"}
    else:
        mapping = {1: "第一季", 2: "第二季", 3: "第三季", 4: "第四季"}
    
    return mapping.get(quarter, "")


def extract_date_from_text(text: str) -> Tuple[str, str]:
    """
    從日期字串提取年度和季度
    
    支援格式：
    - "114年03月31日" -> ("114", "Q1")
    - "114.3.31" -> ("114", "Q1")
    
    Args:
        text: 日期字串
        
    Returns:
        (year, quarter_str) 元組
    """
    patterns = [
        r'(\d+)年(\d+)月',           # 114年03月
        r'(\d+)\.(\d+)\.\d+',        # 114.3.31
        r'(\d+)\s*年\s*(\d+)\s*月',  # 114 年 3 月
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            year = match.group(1)
            month = int(match.group(2))
            quarter = (month - 1) // 3 + 1
            return year, f"Q{quarter}"
    
    return "", ""


def format_year_quarter(year: int, quarter: int, style: str = "compact") -> str:
    """
    格式化年度季度
    
    Args:
        year: 民國年
        quarter: 季度 (1-4)
        style: 格式風格
            - "compact": 114Q1
            - "full": 114年第一季
            
    Returns:
        格式化字串
    """
    if style == "compact":
        return f"{year}Q{quarter}"
    elif style == "full":
        return f"{year}年{get_quarter_text(quarter)}"
    else:
        return f"{year}Q{quarter}"
