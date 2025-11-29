#!/usr/bin/env python3
"""
測試所有銀行財報下載功能 (Playwright 重構版)
"""
import os
import sys
from datetime import datetime

# 加入父目錄到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from refactor.downloader import BankDownloader, BANK_CODES
from refactor.banks.base import DownloadStatus


def test_all_banks(year: int = 114, quarter: int = 1):
    """測試所有銀行"""
    
    print(f"\n{'='*60}")
    print(f"銀行財報下載測試 (Playwright 重構版) - {year}Q{quarter}")
    print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 初始化下載器
    downloader = BankDownloader(data_dir="data")
    
    # 結果統計
    results = {
        "success": [],
        "already_exists": [],
        "no_data": [],
        "error": []
    }
    
    # 測試每家銀行
    total = len(BANK_CODES)
    for i, (code, name) in enumerate(BANK_CODES.items(), 1):
        print(f"\n[{i}/{total}] 測試：{name} (代碼:{code})")
        
        try:
            result = downloader.download(name, year, quarter)
            
            if result.status == DownloadStatus.SUCCESS:
                print(f"    ✅ 成功: {result.file_path}")
                results["success"].append({"代碼": code, "銀行": name, "檔案": result.file_path})
                
            elif result.status == DownloadStatus.ALREADY_EXISTS:
                print(f"    ⏭️ 已存在: {result.file_path}")
                results["already_exists"].append({"代碼": code, "銀行": name})
                
            elif result.status == DownloadStatus.NO_DATA:
                print(f"    ⚠️ 尚無資料: {result.message}")
                results["no_data"].append({"代碼": code, "銀行": name, "訊息": result.message})
                
            else:
                print(f"    ❌ 錯誤: {result.message}")
                results["error"].append({"代碼": code, "銀行": name, "訊息": result.message})
                
        except Exception as e:
            print(f"    ❌ 例外錯誤: {str(e)[:100]}")
            results["error"].append({"代碼": code, "銀行": name, "訊息": str(e)[:100]})
    
    # 輸出統計結果
    print(f"\n{'='*60}")
    print("測試結果統計")
    print(f"{'='*60}")
    print(f"✅ 成功下載：{len(results['success'])} 家")
    print(f"⏭️ 已存在：{len(results['already_exists'])} 家")
    print(f"⚠️ 尚無資料：{len(results['no_data'])} 家")
    print(f"❌ 錯誤：{len(results['error'])} 家")
    print(f"總計：{total} 家")
    
    # 詳細結果
    if results["success"]:
        print(f"\n--- 成功下載 ---")
        for item in results["success"]:
            print(f"  {item['代碼']}. {item['銀行']}")
    
    if results["no_data"]:
        print(f"\n--- 尚無資料 ---")
        for item in results["no_data"]:
            print(f"  {item['代碼']}. {item['銀行']}: {item['訊息']}")
    
    if results["error"]:
        print(f"\n--- 錯誤 ---")
        for item in results["error"]:
            print(f"  {item['代碼']}. {item['銀行']}: {item['訊息']}")
    
    # 儲存結果
    result_file = f"test_result_playwright_{year}Q{quarter}.txt"
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(f"銀行財報下載測試結果 (Playwright) - {year}Q{quarter}\n")
        f.write(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"成功：{len(results['success'])} 家\n")
        f.write(f"已存在：{len(results['already_exists'])} 家\n")
        f.write(f"尚無資料：{len(results['no_data'])} 家\n")
        f.write(f"錯誤：{len(results['error'])} 家\n\n")
        
        if results["error"]:
            f.write("錯誤清單：\n")
            for item in results["error"]:
                f.write(f"  {item['代碼']}. {item['銀行']}: {item['訊息']}\n")
    
    print(f"\n結果已儲存至 {result_file}")
    
    return results


def test_single_bank(bank_name: str, year: int = 114, quarter: int = 1):
    """測試單一銀行"""
    
    print(f"\n測試 {bank_name} - {year}Q{quarter}")
    print("-" * 40)
    
    downloader = BankDownloader(data_dir="data")
    result = downloader.download(bank_name, year, quarter)
    
    print(f"狀態: {result.status.name}")
    print(f"訊息: {result.message}")
    if result.file_path:
        print(f"檔案: {result.file_path}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="測試銀行財報下載功能")
    parser.add_argument("--year", "-y", type=int, default=114, help="民國年 (預設: 114)")
    parser.add_argument("--quarter", "-q", type=int, default=1, help="季度 (預設: 1)")
    parser.add_argument("--bank", "-b", type=str, help="指定銀行名稱 (測試單一銀行)")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有支援的銀行")
    
    args = parser.parse_args()
    
    if args.list:
        print("\n支援的銀行清單：")
        print("-" * 40)
        for code, name in BANK_CODES.items():
            print(f"  {code:2d}. {name}")
    elif args.bank:
        test_single_bank(args.bank, args.year, args.quarter)
    else:
        test_all_banks(args.year, args.quarter)
