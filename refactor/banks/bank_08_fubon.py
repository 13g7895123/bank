"""
台北富邦銀行 (8) - Taipei Fubon Commercial Bank
網址: https://www.fubon.com/banking/about/intro_FBB/Financial_status.htm
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class FubonDownloader(BaseBankDownloader):
    """台北富邦銀行下載器"""
    
    bank_name = "台北富邦銀行"
    bank_code = 8
    bank_url = "https://www.fubon.com/banking/about/intro_FBB/Financial_status.htm"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        # 直接嘗試下載 PDF (固定 URL 格式)
        pdf_url = f"https://www.fubon.com/banking/document/about/intro_FBB/TW/{year}Q{quarter}.pdf"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
