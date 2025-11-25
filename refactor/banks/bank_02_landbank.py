"""
臺灣土地銀行 (2) - Land Bank of Taiwan
網址: https://www.landbank.com.tw/Category/Items/財務業務資訊-財報
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class LandBankDownloader(BaseBankDownloader):
    """臺灣土地銀行下載器"""
    
    bank_name = "臺灣土地銀行"
    bank_code = 2
    bank_url = "https://www.landbank.com.tw/Category/Items/財務業務資訊-財報"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找資產品質表格
        table = page.query_selector('table[summary="資產品質年度季報表"]')
        if not table:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資產品質表格"
            )
        
        # 取得第一列
        first_row = table.query_selector("tr")
        if not first_row:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列"
            )
        
        # 解析年度
        row_text = first_row.inner_text()
        try:
            year_on_page = int(row_text.split('年')[0])
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析年度"
            )
        
        # 取得所有季度連結
        tds = first_row.query_selector_all("td")
        quarters_available = len(tds)
        
        if year_on_page != year or quarters_available < quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料 (目前: {year_on_page}年, {quarters_available}季)"
            )
        
        # 取得對應季度的連結
        link = tds[quarter - 1].query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的下載連結"
            )
        
        href = link.get_attribute("href")
        if not href.startswith("http"):
            pdf_url = f"https://www.landbank.com.tw{href}"
        else:
            pdf_url = href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
