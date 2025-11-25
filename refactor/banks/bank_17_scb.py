"""
渣打國際商業銀行 (17) - Standard Chartered Bank (Taiwan)
網址: https://www.sc.com/tw/about-us/investor-relations/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class SCBDownloader(BaseBankDownloader):
    """渣打國際商業銀行下載器"""
    
    bank_name = "渣打國際商業銀行"
    bank_code = 17
    bank_url = "https://www.sc.com/tw/about-us/investor-relations/"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        # 直接嘗試固定 URL 格式
        if quarter == 1 or quarter == 3:
            pdf_url = f"https://av.sc.com/tw/content/docs/tw-fi-{year}q{quarter}.pdf"
        else:
            # 第二季和第四季用半年報格式
            half = quarter // 2
            pdf_url = f"https://av.sc.com/tw/content/docs/tw-earnings-{year}_h{half}.pdf"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
