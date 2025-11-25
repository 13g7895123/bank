"""
匯豐(台灣)商業銀行 (20) - HSBC Bank (Taiwan)
網址: https://www.hsbc.com.tw/help/announcements/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class HSBCDownloader(BaseBankDownloader):
    """匯豐(台灣)商業銀行下載器"""
    
    bank_name = "匯豐(台灣)商業銀行"
    bank_code = 20
    bank_url = "https://www.hsbc.com.tw/help/announcements/"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        year_ad = year + 1911  # 民國轉西元
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 找所有下載區塊
        divs = page.query_selector_all("div.O-SMARTSPCGEN-DEV.M-CONTMAST-RW-RBWM.links")
        if len(divs) < 4:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到足夠的資料區塊"
            )
        
        # 通常第4個區塊是財報
        target_div = divs[3]
        link = target_div.query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        title = link.get_attribute("data-event-name") or link.inner_text()
        
        if str(year_ad) not in title or quarter_text not in title:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料"
            )
        
        href = link.get_attribute("href")
        pdf_url = href if href.startswith("http") else f"https://www.hsbc.com.tw{href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
