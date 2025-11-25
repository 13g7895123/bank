"""
遠東國際商業銀行 (28) - Far Eastern International Bank
網址: https://www.feib.com.tw/detail?id=349
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class FEIBDownloader(BaseBankDownloader):
    """遠東國際商業銀行下載器"""
    
    bank_name = "遠東國際商業銀行"
    bank_code = 28
    bank_url = "https://www.feib.com.tw/detail?id=349"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 找下拉選單 (第二個 select)
        selects = page.query_selector_all("select")
        if len(selects) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到選擇器"
            )
        
        # 取得最後一個選項
        options = selects[1].query_selector_all("option")
        if not options:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到選項"
            )
        
        last_option = options[-1]
        option_text = last_option.inner_text()
        
        if str(year) not in option_text or quarter_text not in option_text:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料"
            )
        
        pdf_href = last_option.get_attribute("value")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.feib.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
