"""
中國輸出入銀行 (10) - Export-Import Bank of the Republic of China
網址: https://www.eximbank.com.tw/zh-tw/FinanceInfo/Finance/Pages/default.aspx
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class EximBankDownloader(BaseBankDownloader):
    """中國輸出入銀行下載器"""
    
    bank_name = "中國輸出入銀行"
    bank_code = 10
    bank_url = "https://www.eximbank.com.tw/zh-tw/FinanceInfo/Finance/Pages/default.aspx"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        # 直接訪問特定季度頁面
        target_url = f"https://www.eximbank.com.tw/zh-tw/FinanceInfo/Pages/FinanceReports.aspx?year={year}Q{quarter}"
        
        page.goto(target_url)
        page.wait_for_load_state("networkidle")
        
        # 找資產品質區塊的連結 (通常是第4個 row_list)
        lists = page.query_selector_all("ul.row_list")
        if len(lists) < 4:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        target_list = lists[3]
        text = target_list.inner_text().strip()
        
        if not text:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}Q{quarter} 的資料"
            )
        
        link = target_list.query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        href = link.get_attribute("href")
        if not href.startswith("http"):
            pdf_url = f"https://www.eximbank.com.tw{href}"
        else:
            pdf_url = href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
