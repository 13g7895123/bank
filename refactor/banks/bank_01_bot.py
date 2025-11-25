"""
臺灣銀行 (1) - Bank of Taiwan
網址: https://www.bot.com.tw/about/financial-statements/quarterly-report
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class BOTDownloader(BaseBankDownloader):
    """臺灣銀行下載器"""
    
    bank_name = "臺灣銀行"
    bank_code = 1
    bank_url = "https://www.bot.com.tw/about/financial-statements/quarterly-report"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 尋找目標連結
        target_title = f"個體財務報告 {year}年{quarter_text}"
        
        # 找所有下載連結
        links = page.query_selector_all("app-document-download a")
        
        pdf_url = None
        for link in links:
            title = link.get_attribute("title") or ""
            if target_title in title:
                href = link.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        pdf_url = f"https://www.bot.com.tw{href}"
                    else:
                        pdf_url = href
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
