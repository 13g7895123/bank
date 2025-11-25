"""
華泰商業銀行 (22) - Hwatai Bank
網址: https://www.hwataibank.com.tw/public/public02-01/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class HwataiBankDownloader(BaseBankDownloader):
    """華泰商業銀行下載器"""
    
    bank_name = "華泰商業銀行"
    bank_code = 22
    bank_url = "https://www.hwataibank.com.tw/public/public02-01/"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找所有按鈕連結
        buttons = page.query_selector_all("div.elementor-button-wrapper a")
        
        pdf_url = None
        for btn in buttons:
            title = btn.get_attribute("title") or btn.inner_text()
            if str(year) in title and quarter_text in title:
                href = btn.get_attribute("href")
                if href:
                    pdf_url = href if href.startswith("http") else f"https://www.hwataibank.com.tw{href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
