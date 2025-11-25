"""
花旗（台灣）銀行 (13) - Citibank Taiwan
網址: https://www.citigroup.com/global/about-us/global-presence/zh-TW/taiwan/regulatory-disclosures
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CitibankDownloader(BaseBankDownloader):
    """花旗（台灣）銀行下載器"""
    
    bank_name = "花旗（台灣）銀行"
    bank_code = 13
    bank_url = "https://www.citibank.com.tw/global_docs/chi/pressroom/financial_info/financial.htm"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找資料列
        td = page.query_selector("td.1b")
        if not td:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        td_text = td.inner_text()
        
        # 解析日期 (格式: MM/DD/YYYY)
        try:
            parts = td_text.split("/")
            year_ad = int(parts[2])
            year_on_page = year_ad - 1911
            quarter_on_page = int(int(parts[0]) / 3)
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析日期"
            )
        
        if year_on_page != year or quarter_on_page != quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料"
            )
        
        link = td.query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        href = link.get_attribute("href")
        pdf_url = f"https://www.citibank.com.tw/global_docs/chi/pressroom/financial_info/{href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
