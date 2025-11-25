"""
板信商業銀行 (25) - Bank of Panhsin
網址: https://www.bop.com.tw/Footer/Financial_Report
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class BOPDownloader(BaseBankDownloader):
    """板信商業銀行下載器"""
    
    bank_name = "板信商業銀行"
    bank_code = 25
    bank_url = "https://www.bop.com.tw/Footer/Financial_Report?tni=110&refid=null"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找第二個表格
        tables = page.query_selector_all("table.table.table-hover")
        if len(tables) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        tbody = tables[1].query_selector("tbody")
        if not tbody:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到表格內容"
            )
        
        first_row = tbody.query_selector("tr")
        if not first_row:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列"
            )
        
        tds = first_row.query_selector_all("td")
        if len(tds) <= quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的資料"
            )
        
        # 檢查年度
        year_text = tds[0].inner_text()
        if str(year) not in year_text:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年 的資料"
            )
        
        # 取得 PDF 連結
        pdf_link = tds[quarter].query_selector("a")
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.bop.com.tw/{pdf_href.lstrip('/')}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
