"""
臺灣中小企業銀行 (16) - Taiwan Business Bank
網址: https://ir.tbb.com.tw/financial/quarterly-results
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class TBBDownloader(BaseBankDownloader):
    """臺灣中小企業銀行下載器"""
    
    bank_name = "臺灣中小企業銀行"
    bank_code = 16
    bank_url = "https://www.tbb.com.tw/web/guest/-/468"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        if quarter == 4:
            quarter_text = "度"  # 第四季用 "年度"
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 找下載區塊
        download_div = page.query_selector("div.l-download.u-mb-4")
        if not download_div:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載區塊"
            )
        
        links = download_div.query_selector_all("a")
        
        pdf_url = None
        for link in links:
            title = link.get_attribute("title") or link.inner_text()
            if str(year) in title and quarter_text in title:
                href = link.get_attribute("href")
                if href:
                    pdf_url = f"https://www.tbb.com.tw{href}" if not href.startswith("http") else href
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
