"""
銀行下載失敗診斷工具

針對下載失敗的 22 家銀行：
1. 顯示其選取規則
2. 開啟網頁並截圖
3. 生成診斷報告
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# 確保可以導入模組
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright

# 失敗的銀行清單（代碼, 名稱, URL）
FAILED_BANKS = [
    (1, "臺灣銀行", "https://www.bot.com.tw/tw/"),
    (2, "臺灣土地銀行", "https://www.landbank.com.tw/Category/Items/財務業務資訊-財報"),
    (4, "第一商業銀行", "https://www.firstbank.com.tw/sites/fcb/Statutory"),
    (5, "華南商業銀行", "https://www.hnfhc.com.tw/HNFHC/ir/d.do"),
    (9, "國泰世華商業銀行", "https://www.cathaybk.com.tw/cathaybk/personal/about/news/announce/"),
    (11, "高雄銀行", "https://www.bok.com.tw/-107"),
    (12, "兆豐國際商業銀行", "https://www.megabank.com.tw//about/announcement/legal-disclosure/finance-report"),
    (13, "花旗（台灣）銀行", "https://www.citigroup.com/global/about-us/global-presence/zh-TW/taiwan/regulatory-disclosures"),
    (16, "臺灣中小企業銀行", "https://ir.tbb.com.tw/financial/quarterly-results"),
    (18, "台中商業銀行", "https://www.tcbbank.com.tw/Site/intro/finReport/finReport.aspx"),
    (20, "匯豐(台灣)商業銀行", "https://www.hsbc.com.tw/help/announcements/"),
    (22, "華泰商業銀行", "https://www.hwataibank.com.tw/public/public02-01/"),
    (23, "臺灣新光商業銀行", "https://www.skbank.com.tw/QFI"),
    (24, "陽信商業銀行", "https://www.sunnybank.com.tw/net/Page/Smenu/4"),
    (27, "聯邦商業銀行", "https://www.ubot.com.tw/investors"),
    (28, "遠東國際商業銀行", "https://www.feib.com.tw/detail?id=349"),
    (30, "永豐商業銀行", "https://bank.sinopac.com/sinopacBT/about/investor/financial-statement.html"),
    (32, "凱基商業銀行", "https://www.kgibank.com.tw/zh-tw/about-us/financial-summary"),
    (33, "星展(台灣)商業銀行", "https://www.dbs.com.tw/personal-zh/legal-disclaimers-and-announcements.page"),
    (38, "樂天國際商業銀行", "https://www.rakuten-bank.com.tw/portal/other/disclosure"),
    (40, "連線商業銀行", "https://corp.linebank.com.tw/zh-tw/company-financial"),
    (41, "將來商業銀行", "https://www.nextbank.com.tw/disclosures/download/52831e76d4000000d9ee07510ffac025"),
]

# 各銀行的選取規則說明
SELECTOR_RULES = {
    1: {
        "name": "臺灣銀行",
        "method": "尋找包含年度季度的 PDF 連結",
        "selector": "a[href*='.pdf']",
        "issue": "網頁有多層選單，需要先選擇年度和季度才能看到財報連結"
    },
    2: {
        "name": "臺灣土地銀行",
        "method": "在財務資訊頁面尋找 PDF 連結",
        "selector": "a[href*='.pdf'], a:has-text('下載')",
        "issue": "頁面使用動態載入，需要等待內容載入完成"
    },
    4: {
        "name": "第一商業銀行",
        "method": "在法定公告頁面尋找季報連結",
        "selector": "a[href*='114'][href*='Q1'], a:has-text('114年第1季')",
        "issue": "財報頁面結構已變更，原有選擇器可能失效"
    },
    5: {
        "name": "華南商業銀行",
        "method": "在投資人關係頁面尋找財報",
        "selector": "a[href*='.pdf']",
        "issue": "需要特殊導航邏輯，頁面使用 iframe 或 AJAX"
    },
    9: {
        "name": "國泰世華商業銀行",
        "method": "在公告專區尋找財報連結",
        "selector": "a[href*='pdf'], a:has-text('財務報告')",
        "issue": "網頁使用動態載入，需要滾動或點擊展開"
    },
    11: {
        "name": "高雄銀行",
        "method": "在財務資訊頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "URL 結構特殊，可能需要調整訪問路徑"
    },
    12: {
        "name": "兆豐國際商業銀行",
        "method": "在法定揭露頁面尋找財報",
        "selector": "a[href*='.pdf'][href*='114']",
        "issue": "網頁結構需要調整，可能有分頁或篩選功能"
    },
    13: {
        "name": "花旗（台灣）銀行",
        "method": "在國際集團網站尋找台灣監管披露",
        "selector": "a[href*='.pdf']",
        "issue": "國際網站結構不同，需要特殊處理"
    },
    16: {
        "name": "臺灣中小企業銀行",
        "method": "在投資人關係頁面尋找季報",
        "selector": "a[href*='.pdf'], a:has-text('114年')",
        "issue": "需要展開選單或切換標籤頁"
    },
    18: {
        "name": "台中商業銀行",
        "method": "在財報頁面尋找 PDF 連結",
        "selector": "a[href*='.pdf']",
        "issue": "ASP.NET 頁面，可能需要提交表單"
    },
    20: {
        "name": "匯豐(台灣)商業銀行",
        "method": "在公告頁面尋找財報",
        "selector": "a[href*='.pdf']",
        "issue": "國際網站需要特殊處理，可能有地區限制"
    },
    22: {
        "name": "華泰商業銀行",
        "method": "在公開資訊頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "檔案連結格式不同，需要調整選擇器"
    },
    23: {
        "name": "臺灣新光商業銀行",
        "method": "在財務資訊頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "需要點擊多層選單才能看到財報"
    },
    24: {
        "name": "陽信商業銀行",
        "method": "在資訊揭露頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "網頁結構複雜，需要分析頁面結構"
    },
    27: {
        "name": "聯邦商業銀行",
        "method": "在投資人專區尋找財報",
        "selector": "a[href*='.pdf']",
        "issue": "可能需要登入或特殊操作"
    },
    28: {
        "name": "遠東國際商業銀行",
        "method": "在詳細頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "頁面結構不同，需要調整"
    },
    30: {
        "name": "永豐商業銀行",
        "method": "在投資人關係頁面尋找財報",
        "selector": "a[href*='.pdf']",
        "issue": "財報頁面需要調整選擇邏輯"
    },
    32: {
        "name": "凱基商業銀行",
        "method": "在財務摘要頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "找不到 PDF 連結，可能需要其他入口"
    },
    33: {
        "name": "星展(台灣)商業銀行",
        "method": "在法律聲明頁面尋找財報",
        "selector": "a[href*='.pdf']",
        "issue": "國際網站結構不同"
    },
    38: {
        "name": "樂天國際商業銀行",
        "method": "在資訊揭露頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "網頁動態載入，需要等待"
    },
    40: {
        "name": "連線商業銀行",
        "method": "在公司財務頁面尋找 PDF",
        "selector": "a[href*='.pdf']",
        "issue": "網頁結構需要調整"
    },
    41: {
        "name": "將來商業銀行",
        "method": "在揭露專區下載財報",
        "selector": "a[href*='.pdf']",
        "issue": "需要特殊處理，可能是直接下載頁面"
    },
}


async def capture_bank_page(bank_code: int, bank_name: str, url: str, output_dir: Path):
    """開啟銀行網頁並截圖"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="zh-TW",
        )
        page = await context.new_page()
        
        try:
            print(f"  正在載入 {bank_name}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)  # 額外等待動態內容
            
            # 截圖
            screenshot_path = output_dir / f"{bank_code:02d}_{bank_name}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"  ✓ 截圖已儲存: {screenshot_path.name}")
            
            # 分析頁面上的 PDF 連結
            pdf_links = await page.query_selector_all("a[href*='.pdf']")
            all_links = await page.query_selector_all("a")
            
            return {
                "success": True,
                "pdf_count": len(pdf_links),
                "total_links": len(all_links),
                "screenshot": str(screenshot_path),
            }
            
        except Exception as e:
            print(f"  ✗ 錯誤: {e}")
            # 嘗試截取當前狀態
            try:
                screenshot_path = output_dir / f"{bank_code:02d}_{bank_name}_error.png"
                await page.screenshot(path=str(screenshot_path))
            except:
                pass
            return {
                "success": False,
                "error": str(e),
            }
        finally:
            await browser.close()


async def diagnose_all_banks():
    """診斷所有失敗的銀行"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(__file__).parent.parent / "診斷截圖" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"銀行下載失敗診斷工具")
    print(f"截圖目錄: {output_dir}")
    print(f"{'='*60}\n")
    
    results = []
    
    for bank_code, bank_name, url in FAILED_BANKS:
        print(f"\n[{bank_code:02d}] {bank_name}")
        print(f"  URL: {url}")
        
        rule = SELECTOR_RULES.get(bank_code, {})
        print(f"  選取方法: {rule.get('method', '未定義')}")
        print(f"  選擇器: {rule.get('selector', '未定義')}")
        print(f"  問題: {rule.get('issue', '未定義')}")
        
        result = await capture_bank_page(bank_code, bank_name, url, output_dir)
        result["code"] = bank_code
        result["name"] = bank_name
        result["url"] = url
        result["rule"] = rule
        results.append(result)
    
    # 生成報告
    report_path = output_dir / "診斷報告.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 銀行下載失敗診斷報告\n\n")
        f.write(f"**診斷時間**: {timestamp}\n\n")
        f.write(f"---\n\n")
        
        for result in results:
            f.write(f"## [{result['code']:02d}] {result['name']}\n\n")
            f.write(f"- **URL**: {result['url']}\n")
            f.write(f"- **選取方法**: {result['rule'].get('method', '未定義')}\n")
            f.write(f"- **選擇器**: `{result['rule'].get('selector', '未定義')}`\n")
            f.write(f"- **問題**: {result['rule'].get('issue', '未定義')}\n")
            
            if result.get("success"):
                f.write(f"- **頁面 PDF 連結數**: {result.get('pdf_count', 0)}\n")
                f.write(f"- **總連結數**: {result.get('total_links', 0)}\n")
            else:
                f.write(f"- **錯誤**: {result.get('error', '未知')}\n")
            
            f.write(f"\n**截圖**:\n\n")
            f.write(f"![{result['name']}]({result['code']:02d}_{result['name']}.png)\n\n")
            f.write(f"---\n\n")
    
    print(f"\n{'='*60}")
    print(f"診斷完成！")
    print(f"截圖目錄: {output_dir}")
    print(f"報告檔案: {report_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(diagnose_all_banks())
