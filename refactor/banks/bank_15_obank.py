"""
王道商業銀行 (15) - O-Bank
網址: https://www.o-bank.com/common/regulation/regulation-financialreport
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class OBankDownloader(BaseBankDownloader):
    """王道商業銀行下載器"""
    
    bank_name = "王道商業銀行"
    bank_code = 15
    bank_url = "https://www.o-bank.com/common/regulation/regulation-financialreport"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找列表
        ul = page.query_selector("ul.w3-ul.o-ul.ul-2")
        if not ul:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列表"
            )
        
        items = ul.query_selector_all("li")
        if not items:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料項目"
            )
        
        # 檢查第一個項目的年度
        first_item_text = items[0].inner_text()
        try:
            year_ad = int(first_item_text.split()[0])
            year_on_page = year_ad - 1911
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析年度"
            )
        
        quarters_available = len(items)
        
        if year_on_page != year or quarters_available < quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料"
            )
        
        # 取得第一個項目的連結
        link = items[0].query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        href = link.get_attribute("href")
        pdf_url = f"https://www.o-bank.com{href}" if not href.startswith("http") else href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
