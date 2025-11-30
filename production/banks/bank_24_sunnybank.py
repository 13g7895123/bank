"""
陽信商業銀行 (24) - Sunny Bank
網址: https://www.sunnybank.com.tw/net/Page/Smenu/4
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page
import re


class SunnyBankDownloader(BaseBankDownloader):
    """陽信商業銀行下載器"""
    
    bank_name = "陽信商業銀行"
    bank_code = 24
    bank_url = "https://www.sunnybank.com.tw/net/Page/Smenu/4"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        
        # 根據季度建立目標 href 的搜尋模式
        # Q1-Q3: /public/pdf/114年第1季.pdf
        # Q4: /public/pdf/114年度公開說明書.pdf
        if quarter == 4:
            # 第四季是年度公開說明書
            target_pattern = f"/public/pdf/{year}年度公開說明書.pdf"
        else:
            # Q1-Q3
            target_pattern = f"/public/pdf/{year}年第{quarter}季.pdf"
        
        # 找所有 a 元素，檢查 href 屬性
        target_link = None
        all_links = await page.query_selector_all("a")
        
        for link in all_links:
            href = await link.get_attribute("href")
            if href and target_pattern in href:
                target_link = link
                break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的連結 (目標: {target_pattern})"
            )
        
        # 取得完整 PDF 連結
        pdf_href = await target_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.sunnybank.com.tw{pdf_href}"
        
        # 點擊連結觸發下載（完整流程）
        with page.expect_download() as download_info:
            await target_link.click()
        
        download = download_info.value
        
        # 儲存檔案
        save_path = self.get_file_path(year, quarter)
        download.save_as(save_path)
        
        return DownloadResult(
            status=DownloadStatus.SUCCESS,
            message="下載成功",
            file_path=str(save_path)
        )
