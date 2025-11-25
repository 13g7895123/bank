"""
凱基商業銀行 (32) - KGI Bank
網址: https://www.kgibank.com.tw/zh-tw/about-us/financial-summary
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class KGIBankDownloader(BaseBankDownloader):
    """凱基商業銀行下載器"""
    
    bank_name = "凱基商業銀行"
    bank_code = 32
    bank_url = "https://www.kgibank.com.tw/zh-tw/about-us/financial-summary"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        year_ad = year + 1911  # 民國轉西元
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 找 slick-track 中的資料
        slick_tracks = page.query_selector_all("div.slick-track")
        if len(slick_tracks) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        row = slick_tracks[1].query_selector("div.row")
        if not row:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列"
            )
        
        year_divs = row.query_selector_all("div.h3.ml-16")
        target_links = row.query_selector_all("a")
        
        pdf_url = None
        for i, link in enumerate(target_links):
            if i >= len(year_divs):
                break
            year_text = year_divs[i].inner_text()
            
            if str(year_ad) in year_text and quarter_text in year_text:
                # 根據季度選擇合併或非合併財報
                if quarter % 2 == 1 and "合併財務報告" in year_text:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.kgibank.com.tw{pdf_href}"
                    break
                elif quarter % 2 == 0 and "非合併財務報告" in year_text:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.kgibank.com.tw{pdf_href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
