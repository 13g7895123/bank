"""
星展(台灣)商業銀行 (33) - DBS Bank (Taiwan)
網址: https://www.dbs.com.tw/personal-zh/legal-disclaimers-and-announcements.page
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class DBSBankDownloader(BaseBankDownloader):
    """星展(台灣)商業銀行下載器"""
    
    bank_name = "星展(台灣)商業銀行"
    bank_code = 33
    bank_url = "https://www.dbs.com.tw/personal-zh/legal-disclaimers-and-announcements.page"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        year_ad = year + 1911  # 民國轉西元
        
        # 根據季度設定搜尋文字
        if quarter == 1:
            search_text = f"{year_ad}年1季"
        elif quarter == 2:
            search_text = f"{year_ad}年06月"
        elif quarter == 3:
            search_text = f"{year_ad}年3季"
        else:
            search_text = f"{year_ad}年12月"
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 找資料區塊
        divs = page.query_selector_all("div.sc-1ebj2bl.dpxttY")
        if len(divs) < 4:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        target_div = divs[3]
        
        # 找目標連結
        link = target_div.query_selector(f"a:text('{search_text}')")
        
        if not link:
            # 嘗試找所有連結
            links = target_div.query_selector_all("a")
            for l in links:
                text = l.inner_text()
                if search_text in text:
                    link = l
                    break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年第{quarter}季 的資料"
            )
        
        pdf_href = link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.dbs.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
