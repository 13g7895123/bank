"""
臺灣新光商業銀行 (23) - Shin Kong Bank
網址: https://www.skbank.com.tw/QFI
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class SKBankDownloader(BaseBankDownloader):
    """臺灣新光商業銀行下載器"""
    
    bank_name = "臺灣新光商業銀行"
    bank_code = 23
    bank_url = "https://www.skbank.com.tw/789.html"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找目標項目
        target = page.query_selector("li.control_me_li")
        if not target:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料項目"
            )
        
        title = target.inner_text()
        
        if str(year) not in title or quarter_text not in title:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料"
            )
        
        # 取得第一層連結
        link = target.query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到連結"
            )
        
        href = link.get_attribute("href")
        sub_url = href if href.startswith("http") else f"https://www.skbank.com.tw{href}"
        
        # 訪問子頁面
        page.goto(sub_url)
        page.wait_for_load_state("networkidle")
        
        # 根據季度找 PDF 連結
        if quarter == 1 or quarter == 3:
            items = page.query_selector_all("li.control_me_li")
            if len(items) >= 7:
                pdf_link = items[6].query_selector("a")
            else:
                pdf_link = None
        else:
            ol = page.query_selector("ol.sena")
            if ol:
                items = ol.query_selector_all("li")
                pdf_link = items[-1].query_selector("a") if items else None
            else:
                pdf_link = None
        
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.skbank.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
