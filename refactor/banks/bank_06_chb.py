"""
彰化商業銀行 (6) - Chang Hwa Commercial Bank
網址: https://www.bankchb.com/frontend/finance.jsp
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CHBDownloader(BaseBankDownloader):
    """彰化商業銀行下載器"""
    
    bank_name = "彰化商業銀行"
    bank_code = 6
    bank_url = "https://www.bankchb.com/frontend/finance.jsp"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找第一個連結確認年度
        first_link = page.query_selector("ul.ul-itemss a")
        if not first_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料連結"
            )
        
        link_text = first_link.inner_text()
        
        # 解析年度
        try:
            year_on_page = int(link_text.split("國")[1].split("年")[0])
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析年度"
            )
        
        # 計算可用季度數
        items = page.query_selector_all("ul.ul-itemss li.ul-li-itemss")
        quarters_available = len(items)
        
        if year_on_page != year or quarters_available < quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料"
            )
        
        # 點擊連結進入子頁面
        href = first_link.get_attribute("href")
        page.goto(f"https://www.bankchb.com/frontend/{href}")
        page.wait_for_load_state("networkidle")
        
        # 找 PDF 連結
        pdf_link = page.query_selector("a.editor_link")
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        if not pdf_href.startswith("http"):
            pdf_url = f"https://www.bankchb.com{pdf_href}"
        else:
            pdf_url = pdf_href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
