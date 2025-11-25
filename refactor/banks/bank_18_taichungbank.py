"""
台中商業銀行 (18) - Taichung Commercial Bank
網址: https://www.tcbbank.com.tw/Site/intro/finReport/finReport.aspx
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class TaichungBankDownloader(BaseBankDownloader):
    """台中商業銀行下載器"""
    
    bank_name = "台中商業銀行"
    bank_code = 18
    bank_url = "https://www.tcbbank.com.tw/Site/intro/finReport/finReport.aspx"
    
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
            text = link.inner_text()
            href = link.get_attribute("href") or ""
            
            if str(year) in text and quarter_text in text and ".pdf" in href.lower():
                pdf_url = href if href.startswith("http") else f"https://www.tcbbank.com.tw{href}"
                break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
