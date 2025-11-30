"""
文字處理工具
"""
import re


def normalize_text(text: str) -> str:
    """
    正規化文字，移除空格和換行
    
    用於處理 PDF 中 "企 業\n金 融" 等格式問題
    
    Args:
        text: 原始文字
        
    Returns:
        正規化後的文字
    """
    if text is None:
        return ""
    return str(text).replace(" ", "").replace("\n", "").replace("　", "").strip()


def parse_number(value) -> float:
    """
    解析數字字串，移除千分位逗號和貨幣符號
    
    Args:
        value: 數字字串或數值
        
    Returns:
        浮點數，解析失敗時返回 0.0
    """
    if value is None:
        return 0.0
    
    val_str = str(value).strip()
    
    # 處理空值和破折號
    if val_str in ['-', '', '－', '-%', '-', '- %', '- ％', 'None', 'nan']:
        return 0.0
    
    # 移除各種符號
    cleaned = val_str.replace(',', '').replace(' ', '')
    cleaned = cleaned.replace('$', '').replace('＄', '')
    cleaned = cleaned.replace('%', '').replace('％', '')
    cleaned = cleaned.replace('(', '-').replace(')', '')  # 處理負數格式
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_ratio(value) -> float:
    """
    解析比率字串
    
    Args:
        value: 比率字串（可能包含 % 符號）
        
    Returns:
        浮點數，解析失敗時返回 0.0
    """
    if value is None:
        return 0.0
    
    val_str = str(value).strip()
    
    if val_str in ['-', '', '－', '-%', '-', '- %', '- ％', 'None', 'nan']:
        return 0.0
    
    cleaned = val_str.replace('%', '').replace('％', '').replace(',', '')
    cleaned = cleaned.replace('$', '').replace('＄', '').replace(' ', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_keywords(text: str, keywords: list) -> list:
    """
    從文字中提取關鍵字
    
    Args:
        text: 要搜尋的文字
        keywords: 關鍵字列表
        
    Returns:
        找到的關鍵字列表
    """
    found = []
    normalized = normalize_text(text)
    for keyword in keywords:
        if normalize_text(keyword) in normalized:
            found.append(keyword)
    return found
