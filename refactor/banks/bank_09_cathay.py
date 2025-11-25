"""
國泰世華商業銀行 (9) - Cathay United Bank
網址: https://www.cathaybk.com.tw/cathaybk/personal/about/news/announce/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CathayDownloader(BaseBankDownloader):
    """國泰世華商業銀行下載器"""
    
    bank_name = "國泰世華商業銀行"
    bank_code = 9
    bank_url = "https://www.cathaybk.com.tw/cathaybk/personal/about/news/announce/"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        target_text = f"{year}年度 {quarter_text}財務報告"
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 找下載區塊
        download_div = page.query_selector("div.cubre-m-download")
        if not download_div:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載區塊"
            )
        
        # 檢查是否有目標資料
        page_text = download_div.inner_text()
        if target_text not in page_text:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年度 {quarter_text} 的資料"
            )
        
        # 找下載連結
        link = download_div.query_selector("div.cubre-o-action__item a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        href = link.get_attribute("href")
        if not href.startswith("http"):
            pdf_url = f"https://www.cathaybk.com.tw{href}"
        else:
            pdf_url = href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
