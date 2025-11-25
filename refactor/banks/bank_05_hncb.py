"""
華南商業銀行 (5) - Hua Nan Commercial Bank
網址: https://www.hncb.com.tw/footer/public_disclosure
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class HNCBDownloader(BaseBankDownloader):
    """華南商業銀行下載器"""
    
    bank_name = "華南商業銀行"
    bank_code = 5
    bank_url = "https://www.hncb.com.tw/footer/public_disclosure"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 尋找包含年度和季度的連結
        links = page.query_selector_all("a")
        
        pdf_url = None
        for link in links:
            title = link.get_attribute("title") or ""
            text = link.inner_text()
            
            # 檢查是否符合目標
            if (str(year) in title or str(year) in text) and (quarter_text in title or quarter_text in text or f"Q{quarter}" in title):
                href = link.get_attribute("href")
                if href and ".pdf" in href.lower():
                    if not href.startswith("http"):
                        pdf_url = f"https://www.hncb.com.tw{href}"
                    else:
                        pdf_url = href
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
