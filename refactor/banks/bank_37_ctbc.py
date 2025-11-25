"""
中國信託商業銀行 (37) - CTBC Bank
網址: https://www.ctbcbank.com/content/dam/twrbo/pdf/aboutctbc/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CTBCBankDownloader(BaseBankDownloader):
    """中國信託商業銀行下載器"""
    
    bank_name = "中國信託商業銀行"
    bank_code = 37
    bank_url = "https://www.ctbcbank.com"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        # 直接嘗試固定 URL 格式
        pdf_url = f"{self.bank_url}/content/dam/twrbo/pdf/aboutctbc/{year}Q{quarter}_CTBC.pdf"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
