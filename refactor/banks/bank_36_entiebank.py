"""
安泰商業銀行 (36) - EnTie Commercial Bank
網址: https://www.entiebank.com.tw/entie/disclosure-financial
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class EntieBankDownloader(BaseBankDownloader):
    """安泰商業銀行下載器"""
    
    bank_name = "安泰商業銀行"
    bank_code = 36
    bank_url = "https://www.entiebank.com.tw/entie/disclosure-financial"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 點擊第二個 tab
        tabs = page.query_selector_all(".tabsTitleName")
        if len(tabs) >= 2:
            tabs[1].click()
            page.wait_for_timeout(1000)
        
        # 找表格
        rows = page.query_selector_all("tbody tr")
        if len(rows) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        # 檢查年度 (第一列)
        year_row = rows[0]
        year_text = year_row.inner_text()
        
        if str(year) not in year_text:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年 的資料"
            )
        
        # 找第二列的資料
        data_row = rows[1]
        tds = data_row.query_selector_all("td")
        
        pdf_url = None
        for td in tds:
            link = td.query_selector("a")
            if link:
                link_text = link.inner_text()
                if quarter_text in link_text:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.entiebank.com.tw{pdf_href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
