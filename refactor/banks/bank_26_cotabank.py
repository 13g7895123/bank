"""
三信商業銀行 (26) - Cota Commercial Bank
網址: https://www.cotabank.com.tw/web/public/expose/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CotaBankDownloader(BaseBankDownloader):
    """三信商業銀行下載器"""
    
    bank_name = "三信商業銀行"
    bank_code = 26
    bank_url = "https://www.cotabank.com.tw/web/public/expose/#tab-財務業務資訊"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找表格
        tbody = page.query_selector("tbody")
        if not tbody:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
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
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.cotabank.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
