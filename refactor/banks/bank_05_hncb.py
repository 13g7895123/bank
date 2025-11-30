"""
華南商業銀行 (5) - Hua Nan Commercial Bank
網址: https://www.hnfhc.com.tw/HNFHC/ir/d.do

網頁結構：
- 有年份下拉選單 (id=year)，需先切換到對應年份
- 下載連結 title 格式: "下載 華南銀行2025年第1季合併財務報告.pdf"
"""
import subprocess
import os
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class HNCBDownloader(BaseBankDownloader):
    """華南商業銀行下載器"""
    
    bank_name = "華南商業銀行"
    bank_code = 5
    bank_url = "https://www.hnfhc.com.tw/HNFHC/ir/d.do"
    headless = True  # 預設無頭模式，失敗時自動重試有頭模式
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 民國年轉西元年
        western_year = year + 1911
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 步驟1: 切換年份下拉選單
        year_select = page.locator('select#year')
        if await year_select.count() > 0:
            await year_select.select_option(str(western_year))
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)
        
        # 步驟2: 建立搜尋的 title 關鍵字
        # 格式: "下載 華南銀行2025年第1季合併財務報告.pdf"
        quarter_num = quarter
        
        search_keywords = [
            f"下載 華南銀行{western_year}年第{quarter_num}季",
        ]
        
        # Q4 額外嘗試「全年度」或「年度」
        if quarter == 4:
            search_keywords.extend([
                f"下載 華南銀行{western_year}年全年度",
                f"下載 華南銀行{western_year}年度",
            ])
        
        # 嘗試各種關鍵字找連結
        link = None
        for keyword in search_keywords:
            locator = page.locator(f'a[title*="{keyword}"]')
            if await locator.count() > 0:
                link = locator.first
                break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} ({western_year}年第{quarter_num}季) 的下載連結"
            )
        
        # 取得 href（直接 PDF URL）
        href = await link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        # 使用 wget 下載（比較能處理 SSL 問題）
        try:
            self.ensure_dir(year, quarter)
            file_path = self.get_file_path(year, quarter)
            
            # 使用 wget 下載，--no-check-certificate 跳過 SSL 驗證
            result = subprocess.run(
                ['wget', '--no-check-certificate', '-q', '-O', file_path, href],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return DownloadResult(
                    status=DownloadStatus.SUCCESS,
                    message="下載成功",
                    file_path=file_path
                )
            else:
                return DownloadResult(
                    status=DownloadStatus.ERROR,
                    message=f"wget 下載失敗: {result.stderr}"
                )
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載失敗: {str(e)}"
            )
