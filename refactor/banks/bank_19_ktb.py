"""
京城商業銀行 (19) - King's Town Bank
網址: https://customer.ktb.com.tw/new/about/8d88e237
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class KTBDownloader(BaseBankDownloader):
    """京城商業銀行下載器"""
    
    bank_name = "京城商業銀行"
    bank_code = 19
    bank_url = "https://customer.ktb.com.tw/new/about/8d88e237"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找年度標題
        year_title = page.query_selector("div.ktbcontent h3")
        if not year_title:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到年度標題"
            )
        
        try:
            year_on_page = int(year_title.inner_text().split("年")[0])
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析年度"
            )
        
        if year_on_page != year:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年 的資料 (目前: {year_on_page}年)"
            )
        
        # 找表格
        table = page.query_selector("table.tftable")
        if not table:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        rows = table.query_selector_all("tr")
        # 從下往上數，第 quarter 列
        target_row_index = len(rows) - quarter
        if target_row_index < 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的資料"
            )
        
        target_row = rows[target_row_index]
        tds = target_row.query_selector_all("td")
        if len(tds) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="資料列格式錯誤"
            )
        
        link = tds[1].query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的下載連結"
            )
        
        href = link.get_attribute("href")
        pdf_url = href if href.startswith("http") else f"https://customer.ktb.com.tw{href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
