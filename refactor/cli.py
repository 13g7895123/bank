#!/usr/bin/env python3
"""
銀行財報自動化系統 - 互動式命令列介面

提供使用者友善的選單式操作介面，整合財報下載與報表生成功能。

使用方式:
    python cli.py
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

# 將目前目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent))

from downloader import BankDownloader, BANK_CODES, BANK_DOWNLOADERS
from banks.base import DownloadStatus
from report_generator import generate_report


# ============================================================
# Logging 設定
# ============================================================

def setup_logging() -> logging.Logger:
    """設定 logging"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"cli_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger = logging.getLogger("bank_cli")
    logger.setLevel(logging.DEBUG)
    
    # 避免重複加入 handler
    if not logger.handlers:
        # 檔案 handler（記錄所有層級）
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

# 初始化 logger
logger = setup_logging()


# ============================================================
# 常數定義
# ============================================================

class Color:
    """終端機顏色代碼"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


class MenuOption(Enum):
    """主選單選項"""
    DOWNLOAD = "1"
    REPORT = "2"
    EXIT = "0"


# ============================================================
# 輔助函數
# ============================================================

def clear_screen():
    """清除螢幕"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """印出標題區塊"""
    width = 60
    print(f"\n{Color.CYAN}{'=' * width}")
    print(f"{title:^{width}}")
    print(f"{'=' * width}{Color.RESET}\n")


def print_success(msg: str):
    """印出成功訊息"""
    print(f"{Color.GREEN}✓ {msg}{Color.RESET}")


def print_error(msg: str):
    """印出錯誤訊息"""
    print(f"{Color.RED}✗ {msg}{Color.RESET}")


def print_warning(msg: str):
    """印出警告訊息"""
    print(f"{Color.YELLOW}⚠ {msg}{Color.RESET}")


def print_info(msg: str):
    """印出資訊訊息"""
    print(f"{Color.BLUE}ℹ {msg}{Color.RESET}")


def get_input(prompt: str) -> str:
    """取得使用者輸入"""
    try:
        return input(f"{Color.BOLD}{prompt}{Color.RESET}").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n")
        return ""


def parse_year_quarter(input_str: str) -> Tuple[Optional[int], Optional[int]]:
    """
    解析年度季度字串
    
    Args:
        input_str: 輸入字串，如 "114Q1" 或 "114 Q1"
        
    Returns:
        (year, quarter) 元組，解析失敗則回傳 (None, None)
    """
    import re
    input_str = input_str.upper().replace(" ", "")
    match = re.match(r"(\d+)Q(\d)", input_str)
    if match:
        year = int(match.group(1))
        quarter = int(match.group(2))
        if 1 <= quarter <= 4:
            return year, quarter
    return None, None


def get_base_dir() -> Path:
    """取得 refactor 專案根目錄"""
    return Path(__file__).parent


def get_data_dir() -> Path:
    """取得資料目錄"""
    return get_base_dir() / "data"


def get_output_dir() -> Path:
    """取得輸出目錄"""
    return get_base_dir() / "Output"


# ============================================================
# 選單顯示
# ============================================================

def show_main_menu():
    """顯示主選單"""
    print_header("銀行財報自動化系統 (Refactor 版)")
    print("請選擇功能：\n")
    print(f"  {Color.CYAN}[1]{Color.RESET} 下載財報")
    print(f"  {Color.CYAN}[2]{Color.RESET} 製作報表")
    print(f"  {Color.CYAN}[0]{Color.RESET} 離開程式")
    print()


def show_download_menu():
    """顯示下載選單"""
    print_header("下載財報")
    print("請選擇下載方式：\n")
    print(f"  {Color.CYAN}[1]{Color.RESET}   下載單一銀行")
    print(f"  {Color.CYAN}[ALL]{Color.RESET} 下載全部銀行")
    print(f"  {Color.CYAN}[0]{Color.RESET}   返回主選單")
    print()


def show_bank_list():
    """顯示銀行清單"""
    print(f"\n{Color.CYAN}支援的銀行清單：{Color.RESET}")
    print("-" * 50)
    
    # 分成三欄顯示
    banks = list(BANK_CODES.items())
    cols = 3
    rows = (len(banks) + cols - 1) // cols
    
    for i in range(rows):
        row_str = ""
        for j in range(cols):
            idx = i + j * rows
            if idx < len(banks):
                code, name = banks[idx]
                row_str += f"  [{code:02d}] {name:<12}"
        print(row_str)
    
    print("-" * 50)
    print()


# ============================================================
# 下載功能
# ============================================================

def download_single_bank(year: int, quarter: int) -> bool:
    """
    下載單一銀行財報
    
    Args:
        year: 民國年
        quarter: 季度
        
    Returns:
        是否成功
    """
    show_bank_list()
    
    bank_input = get_input("請輸入銀行代碼或名稱（部分名稱亦可）：")
    if not bank_input:
        return False
    
    # 嘗試以代碼查詢
    try:
        bank_code = int(bank_input)
        if bank_code in BANK_CODES:
            bank_name = BANK_CODES[bank_code]
        else:
            print_error(f"找不到銀行代碼: {bank_code}")
            logger.warning(f"找不到銀行代碼: {bank_code}")
            return False
    except ValueError:
        # 以名稱查詢（模糊比對）
        bank_name = None
        for name in BANK_DOWNLOADERS.keys():
            if bank_input in name:
                bank_name = name
                break
        
        if not bank_name:
            print_error(f"找不到銀行: {bank_input}")
            logger.warning(f"找不到銀行: {bank_input}")
            return False
    
    print_info(f"正在下載 {bank_name} {year}Q{quarter} 財報...")
    logger.info(f"開始下載: {bank_name} {year}Q{quarter}")
    
    try:
        downloader = BankDownloader(data_dir=str(get_data_dir()))
        result = asyncio.run(downloader.download(bank_name, year, quarter))
        
        if result.status == DownloadStatus.SUCCESS:
            print_success(f"下載成功: {result.file_path}")
            logger.info(f"下載成功: {bank_name} -> {result.file_path}")
            return True
        elif result.status == DownloadStatus.ALREADY_EXISTS:
            print_warning(f"檔案已存在: {result.file_path}")
            logger.info(f"檔案已存在: {bank_name}")
            return True
        else:
            print_error(f"下載失敗: {result.message}")
            logger.error(f"下載失敗: {bank_name} - {result.message}")
            return False
    except Exception as e:
        print_error(f"下載錯誤: {str(e)}")
        logger.exception(f"下載異常: {bank_name}")
        return False


async def _download_all_banks_async(
    downloader: BankDownloader, 
    year: int, 
    quarter: int,
    max_concurrent: int = 5
) -> Tuple[int, int, list]:
    """
    非同步並行下載所有銀行（內部函數）
    
    Args:
        downloader: BankDownloader 實例
        year: 民國年
        quarter: 季度
        max_concurrent: 最大並行數量
    """
    success_count = 0
    fail_count = 0
    failed_banks = []
    results_lock = asyncio.Lock()
    
    total = len(BANK_DOWNLOADERS)
    completed = 0
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_one(bank_name: str):
        nonlocal success_count, fail_count, completed
        
        async with semaphore:
            try:
                result = await downloader.download(bank_name, year, quarter)
                
                async with results_lock:
                    completed += 1
                    if result.status == DownloadStatus.SUCCESS:
                        print(f"[{completed:02d}/{total}] {bank_name}... {Color.GREEN}成功{Color.RESET}")
                        logger.info(f"下載成功: {bank_name}")
                        success_count += 1
                    elif result.status == DownloadStatus.ALREADY_EXISTS:
                        print(f"[{completed:02d}/{total}] {bank_name}... {Color.YELLOW}已存在{Color.RESET}")
                        logger.info(f"檔案已存在: {bank_name}")
                        success_count += 1
                    else:
                        print(f"[{completed:02d}/{total}] {bank_name}... {Color.RED}失敗{Color.RESET} - {result.message}")
                        logger.error(f"下載失敗: {bank_name} - {result.message}")
                        fail_count += 1
                        failed_banks.append(bank_name)
            except Exception as e:
                async with results_lock:
                    completed += 1
                    print(f"[{completed:02d}/{total}] {bank_name}... {Color.RED}錯誤{Color.RESET} - {str(e)}")
                    logger.exception(f"下載異常: {bank_name}")
                    fail_count += 1
                    failed_banks.append(bank_name)
    
    # 建立所有下載任務並並行執行
    tasks = [download_one(bank_name) for bank_name in BANK_DOWNLOADERS.keys()]
    await asyncio.gather(*tasks)
    
    return success_count, fail_count, failed_banks


def download_all_banks(year: int, quarter: int, max_concurrent: int = 5) -> Tuple[int, int]:
    """
    下載所有銀行財報（多工並行）
    
    Args:
        year: 民國年
        quarter: 季度
        max_concurrent: 最大並行數量（預設 5）
        
    Returns:
        (成功數, 失敗數)
    """
    print_info(f"開始下載所有銀行 {year}Q{quarter} 財報（並行數: {max_concurrent}）...")
    logger.info(f"開始批次下載: {year}Q{quarter}, 並行數: {max_concurrent}")
    print("-" * 50)
    
    downloader = BankDownloader(data_dir=str(get_data_dir()))
    
    # 使用非同步函數執行並行下載
    success_count, fail_count, failed_banks = asyncio.run(
        _download_all_banks_async(downloader, year, quarter, max_concurrent)
    )
    
    print("-" * 50)
    print_info(f"下載完成！成功: {success_count}, 失敗: {fail_count}")
    logger.info(f"批次下載完成: 成功 {success_count}, 失敗 {fail_count}")
    
    if failed_banks:
        print_warning("以下銀行下載失敗：")
        for bank in failed_banks:
            print(f"  - {bank}")
        logger.warning(f"下載失敗的銀行: {failed_banks}")
    
    return success_count, fail_count


def handle_download():
    """處理下載功能"""
    # 輸入年度季度
    year_quarter = get_input("請輸入欲下載的季度 (例如 114Q1)：")
    year, quarter = parse_year_quarter(year_quarter)
    
    if year is None:
        print_error("無效的季度格式，請使用如 114Q1 的格式")
        logger.warning(f"無效的季度格式: {year_quarter}")
        return
    
    show_download_menu()
    choice = get_input("請選擇：").upper()
    
    if choice == "1":
        download_single_bank(year, quarter)
    elif choice == "ALL":
        download_all_banks(year, quarter, max_concurrent=10)  # 預設並行 10
    elif choice == "0":
        return
    else:
        print_error("無效的選擇")


# ============================================================
# 報表功能
# ============================================================

def handle_report():
    """處理報表製作功能"""
    print_header("製作報表")
    
    # 顯示可用的資料目錄
    data_dir = get_data_dir()
    if data_dir.exists():
        available = sorted([d.name for d in data_dir.iterdir() if d.is_dir() and "Q" in d.name])
        if available:
            print(f"可用的資料目錄: {', '.join(available)}")
        else:
            print_warning("尚無可用的資料目錄")
    print()
    
    # 輸入年度季度
    year_quarter = get_input("請輸入欲製作報表的季度 (例如 114Q1)：")
    year, quarter = parse_year_quarter(year_quarter)
    
    if year is None:
        print_error("無效的季度格式，請使用如 114Q1 的格式")
        return
    
    year_quarter_str = f"{year}Q{quarter}"
    source_dir = data_dir / year_quarter_str
    
    if not source_dir.exists():
        print_error(f"資料目錄不存在: {source_dir}")
        print_info("請先執行下載功能")
        return
    
    # 計算 PDF 數量
    pdf_count = len(list(source_dir.glob("*.pdf")))
    if pdf_count == 0:
        print_error(f"資料目錄中沒有 PDF 檔案: {source_dir}")
        return
    
    print_info(f"找到 {pdf_count} 個 PDF 檔案")
    print_info("開始解析並生成報表...")
    print("-" * 50)
    
    # 生成報表
    output_dir = get_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{year_quarter_str}_資產品質報表.xlsx"
    
    df = generate_report(str(source_dir), str(output_path), year_quarter_str)
    
    if df is not None and not df.empty:
        print("-" * 50)
        print_success(f"報表已生成: {output_path}")
        print_info(f"共 {len(df)} 筆資料")
    else:
        print_error("報表生成失敗或無資料")


# ============================================================
# 主程式
# ============================================================

def main():
    """主程式入口"""
    while True:
        try:
            show_main_menu()
            choice = get_input("請選擇功能：")
            
            if choice == MenuOption.DOWNLOAD.value:
                handle_download()
            elif choice == MenuOption.REPORT.value:
                handle_report()
            elif choice == MenuOption.EXIT.value:
                print_info("感謝使用，再見！")
                break
            else:
                print_error("無效的選擇，請重新輸入")
            
            # 暫停讓使用者看結果
            print()
            get_input("按 Enter 繼續...")
            
        except KeyboardInterrupt:
            print("\n")
            print_info("使用者中斷，程式結束")
            break
        except Exception as e:
            print_error(f"發生錯誤: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
