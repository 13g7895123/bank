"""
聯邦商業銀行 (27) - Union Bank of Taiwan
網址: https://www.ubot.com.tw/investors
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class UBOTDownloader(BaseBankDownloader):
    """聯邦商業銀行下載器"""
    
    bank_name = "聯邦商業銀行"
    bank_code = 27
    bank_url = "https://www.ubot.com.tw/businessmsg"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 等待表格載入
        page.wait_for_selector("tbody", timeout=10000)
        
        # 找表格
        rows = page.query_selector_all("tbody tr")
        if len(rows) <= quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的資料"
            )
        
        target_row = rows[quarter]
        td = target_row.query_selector("td")
        if not td:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料欄位"
            )
        
        pdf_link = td.query_selector("a")
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.ubot.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
