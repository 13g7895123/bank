#!/usr/bin/env python3
"""
測試腳本：測試所有銀行財報下載功能
"""
import os
import sys
import pandas as pd
import time
from datetime import datetime

# 設定測試參數
YEAR = 114
QUARTER = 3

# 建立資料夾
os.makedirs(f"data/{YEAR}Q{QUARTER}", exist_ok=True)

# 載入銀行清單
lst = pd.read_excel("bank.xlsx")

# 結果統計
results = {
    "success": [],
    "failed": [],
    "skipped": []
}

print(f"\n{'='*60}")
print(f"銀行財報下載測試 - {YEAR}Q{QUARTER}")
print(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}\n")

# 導入下載函數
from get_Data import downloadData

# 測試每家銀行
for i in range(len(lst)):
    value = lst.iat[i, 1]  # 序號
    name = lst.iat[i, 2]   # 銀行名稱
    url = lst.iat[i, 5]    # 網址
    
    print(f"\n[{i+1}/{len(lst)}] 測試：{name} (序號:{value})")
    print(f"    網址：{url}")
    
    try:
        start_time = time.time()
        result = downloadData(name, value, YEAR, QUARTER)
        elapsed = time.time() - start_time
        
        if result == 1:
            print(f"    ✅ 成功 (耗時 {elapsed:.2f} 秒)")
            results["success"].append({"序號": value, "銀行": name, "狀態": "成功", "耗時": f"{elapsed:.2f}s"})
        elif result == 2:
            print(f"    ⏭️ 已存在，跳過")
            results["skipped"].append({"序號": value, "銀行": name, "狀態": "已存在"})
        elif result == -1:
            print(f"    ❌ 失敗：尚無該季度資料")
            results["failed"].append({"序號": value, "銀行": name, "狀態": "尚無資料", "網址": url})
        else:
            print(f"    ❌ 失敗：未知錯誤 (回傳值: {result})")
            results["failed"].append({"序號": value, "銀行": name, "狀態": f"未知錯誤({result})", "網址": url})
            
    except Exception as e:
        print(f"    ❌ 例外錯誤：{str(e)[:100]}")
        results["failed"].append({"序號": value, "銀行": name, "狀態": f"例外: {str(e)[:50]}", "網址": url})

# 輸出統計結果
print(f"\n{'='*60}")
print("測試結果統計")
print(f"{'='*60}")
print(f"✅ 成功：{len(results['success'])} 家")
print(f"⏭️ 已存在：{len(results['skipped'])} 家")
print(f"❌ 失敗：{len(results['failed'])} 家")
print(f"總計：{len(lst)} 家")

if results["success"]:
    print(f"\n--- 成功清單 ---")
    for item in results["success"]:
        print(f"  {item['序號']}. {item['銀行']} ({item['耗時']})")

if results["failed"]:
    print(f"\n--- 失敗清單 ---")
    for item in results["failed"]:
        print(f"  {item['序號']}. {item['銀行']}")
        print(f"     狀態：{item['狀態']}")
        print(f"     網址：{item['網址']}")

# 儲存結果到檔案
with open(f"test_result_{YEAR}Q{QUARTER}.txt", "w", encoding="utf-8") as f:
    f.write(f"銀行財報下載測試結果 - {YEAR}Q{QUARTER}\n")
    f.write(f"測試時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"{'='*60}\n\n")
    f.write(f"成功：{len(results['success'])} 家\n")
    f.write(f"已存在：{len(results['skipped'])} 家\n")
    f.write(f"失敗：{len(results['failed'])} 家\n\n")
    
    if results["failed"]:
        f.write("失敗清單：\n")
        for item in results["failed"]:
            f.write(f"  {item['序號']}. {item['銀行']}\n")
            f.write(f"     狀態：{item['狀態']}\n")
            f.write(f"     網址：{item['網址']}\n\n")

print(f"\n結果已儲存至 test_result_{YEAR}Q{QUARTER}.txt")
