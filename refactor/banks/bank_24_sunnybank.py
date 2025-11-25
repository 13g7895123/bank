"""
陽信商業銀行 (24) - Sunny Bank
網址: https://www.sunnybank.com.tw/net/Page/Smenu/4
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class SunnyBankDownloader(BaseBankDownloader):
    """陽信商業銀行下載器"""
    
    bank_name = "陽信商業銀行"
    bank_code = 24
    bank_url = "https://www.sunnybank.com.tw/net/Page/Smenu/4"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找表格
        table = page.query_selector("table.table.table-borderless")
        if not table:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        # 檢查年度
        year_span = table.query_selector("span")
        if not year_span:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到年度資訊"
            )
        
        year_text = year_span.inner_text()
        if str(year) not in year_text:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年 的資料"
            )
        
        # 找對應季度的連結
        links = table.query_selector_all("a")
        sub_url = None
        for link in links:
            title = link.inner_text()
            if quarter_text in title:
                href = link.get_attribute("href")
                sub_url = href if href.startswith("http") else f"https://www.sunnybank.com.tw{href}"
                break
        
        if not sub_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的連結"
            )
        
        # 訪問子頁面
        page.goto(sub_url)
        page.wait_for_load_state("networkidle")
        
        # 找表格中的 PDF 連結
        tbody = page.query_selector("tbody")
        if not tbody:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        rows = tbody.query_selector_all("tr")
        if not rows:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列"
            )
        
        tds = rows[0].query_selector_all("td")
        if len(tds) <= quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的資料"
            )
        
        year_in_row = tds[0].inner_text()
        if str(year) not in year_in_row:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"資料年度不符"
            )
        
        pdf_link = tds[quarter].query_selector("a")
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.sunnybank.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
