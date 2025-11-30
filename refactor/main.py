"""
銀行財報自動化系統 - 主程式

整合財報下載與報表生成功能。

使用方式:
    # 下載並生成報表（預設 114Q1）
    python main.py
    
    # 指定年度季度
    python main.py 114Q1
    
    # 只下載
    python main.py 114Q1 --download-only
    
    # 只生成報表
    python main.py 114Q1 --report-only
    
    # 指定銀行
    python main.py 114Q1 --banks 合作金庫 玉山 台新
"""

import argparse
import asyncio
import sys
from pathlib import Path

# 將 refactor 目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent))

from downloader import BankDownloader
from report_generator import generate_report


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
        help="指定要處理的銀行名稱（部分匹配）"
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


async def run_download(year_quarter: str, banks: list = None, headless: bool = True):
    """執行下載任務"""
    downloader = BankDownloader(headless=headless)
    
    print(f"\n{'='*60}")
    print(f"開始下載 {year_quarter} 財報")
    print(f"{'='*60}")
    
    if banks:
        # 下載指定銀行
        results = await downloader.download_selected(year_quarter, banks)
    else:
        # 下載所有銀行
        results = await downloader.download_all(year_quarter)
    
    return results


def run_report(year_quarter: str):
    """執行報表生成"""
    base_dir = Path(__file__).parent  # refactor 目錄
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


async def main():
    """主程式"""
    args = parse_args()
    
    year_quarter = args.year_quarter
    headless = args.headless and not args.show_browser
    
    print(f"\n銀行財報自動化系統")
    print(f"年度季度: {year_quarter}")
    print(f"無頭模式: {headless}")
    
    if args.banks:
        print(f"指定銀行: {', '.join(args.banks)}")
    
    # 執行下載
    if not args.report_only:
        results = await run_download(year_quarter, args.banks, headless)
        
        # 統計結果
        success = sum(1 for r in results.values() if r.get("status") == "success")
        failed = len(results) - success
        print(f"\n下載統計: 成功 {success}, 失敗 {failed}")
    
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
