"""
銀行財報自動化系統 - 主程式（非同步版本）

整合財報下載與報表生成功能，支援並行下載。

使用方式:
    # 下載並生成報表（預設 114Q1）
    python main.py
    
    # 指定年度季度
    python main.py 114Q1
    
    # 只下載
    python main.py 114Q1 --download-only
    
    # 只生成報表
    python main.py 114Q1 --report-only
    
    # 指定銀行（支援代碼或名稱）
    python main.py 114Q1 --banks 1 2 3
    python main.py 114Q1 --banks 合作金庫 玉山 台新
    
    # 指定並行數量
    python main.py 114Q1 --parallel 3
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 將 refactor 目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent))

from downloader import BankDownloader, BANK_CODES
from report_generator import generate_report
from banks.base import DownloadStatus


def parse_args():
    """解析命令列參數"""
    parser = argparse.ArgumentParser(
        description="銀行財報自動化系統 - 下載財報並生成資產品質報表"
    )
    
    parser.add_argument(
        "year_quarter",
        nargs="?",
        default="114Q1",
        help="年度季度，格式如 114Q1（預設: 114Q1）"
    )
    
    parser.add_argument(
        "--download-only",
        action="store_true",
        help="只執行下載，不生成報表"
    )
    
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="只生成報表，不下載"
    )
    
    parser.add_argument(
        "--banks",
        nargs="+",
        help="指定要處理的銀行（代碼或名稱）"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        type=int,
        default=5,
        help="並行下載數量（預設: 5）"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="使用無頭模式（預設: True）"
    )
    
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="顯示瀏覽器視窗（覆蓋 --headless）"
    )
    
    return parser.parse_args()


def parse_year_quarter(year_quarter: str) -> tuple:
    """解析年度季度字串"""
    import re
    match = re.match(r'(\d+)Q(\d+)', year_quarter)
    if match:
        return int(match.group(1)), int(match.group(2))
    raise ValueError(f"無效的年度季度格式: {year_quarter}")


async def run_download(
    year: int, 
    quarter: int, 
    bank_codes: list = None, 
    max_concurrent: int = 5
) -> dict:
    """執行下載任務（非同步）"""
    base_dir = Path(__file__).parent
    data_dir = str(base_dir / "data")
    
    downloader = BankDownloader(data_dir=data_dir)
    
    print(f"\n{'='*60}")
    print(f"開始下載 {year}Q{quarter} 財報（並行數: {max_concurrent}）")
    print(f"{'='*60}")
    
    if bank_codes:
        # 下載指定銀行
        results = await downloader.download_by_codes(bank_codes, year, quarter, max_concurrent)
    else:
        # 下載所有銀行
        results = await downloader.download_all(year, quarter, max_concurrent)
    
    return results


def run_report(year_quarter: str):
    """執行報表生成"""
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data" / year_quarter
    output_path = base_dir / "Output" / f"{year_quarter}_資產品質報表.xlsx"
    
    print(f"\n{'='*60}")
    print(f"開始生成 {year_quarter} 報表")
    print(f"{'='*60}")
    
    if not data_dir.exists():
        print(f"[錯誤] 資料目錄不存在: {data_dir}")
        print("請先執行下載任務。")
        return None
    
    df = generate_report(str(data_dir), str(output_path))
    return df


def parse_bank_input(banks: list) -> list:
    """解析銀行輸入（支援代碼或名稱）"""
    bank_codes = []
    for item in banks:
        # 嘗試解析為數字
        try:
            code = int(item)
            if code in BANK_CODES:
                bank_codes.append(code)
            else:
                print(f"[警告] 不支援的銀行代碼: {code}")
        except ValueError:
            # 嘗試匹配銀行名稱
            found = False
            for code, name in BANK_CODES.items():
                if item in name or name in item:
                    bank_codes.append(code)
                    found = True
                    break
            if not found:
                print(f"[警告] 找不到匹配的銀行: {item}")
    
    return bank_codes


async def main():
    """主程式"""
    args = parse_args()
    
    year_quarter = args.year_quarter
    year, quarter = parse_year_quarter(year_quarter)
    
    print(f"\n銀行財報自動化系統（非同步版本）")
    print(f"年度季度: {year_quarter}")
    print(f"並行數量: {args.parallel}")
    
    bank_codes = None
    if args.banks:
        bank_codes = parse_bank_input(args.banks)
        if bank_codes:
            print(f"指定銀行: {[BANK_CODES[c] for c in bank_codes]}")
    
    # 執行下載
    if not args.report_only:
        results = await run_download(year, quarter, bank_codes, args.parallel)
        
        # 統計結果
        success = sum(1 for r in results.values() if r.status == DownloadStatus.SUCCESS)
        already = sum(1 for r in results.values() if r.status == DownloadStatus.ALREADY_EXISTS)
        failed = len(results) - success - already
        print(f"\n下載統計: 成功 {success}, 已存在 {already}, 失敗 {failed}")
    
    # 生成報表
    if not args.download_only:
        df = run_report(year_quarter)
        if df is not None and not df.empty:
            print(f"\n報表已生成，共 {len(df)} 筆資料")
    
    print(f"\n{'='*60}")
    print("處理完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
