"""
高雄銀行 (11) - Bank of Kaohsiung
網址: https://www.bok.com.tw/-107
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class BOKDownloader(BaseBankDownloader):
    """高雄銀行下載器"""
    
    bank_name = "高雄銀行"
    bank_code = 11
    bank_url = "https://www.bok.com.tw/-107"
    headless = False  # 可能需要有頭模式
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 建立搜尋的 title 關鍵字
        # Q1-Q3 格式: "114年度第二季季報.pdf（另開視窗）"
        # Q4 格式: "113年度 年報.pdf（另開視窗）"
        if quarter == 4:
            # 第四季用年報
            search_keywords = [
                f"{year}年度 年報.pdf（另開視窗）",
                f"{year}年度年報.pdf（另開視窗）",
            ]
        else:
            # Q1-Q3 用季報
            quarter_num_map = {1: "一", 2: "二", 3: "三"}
            quarter_num = quarter_num_map.get(quarter, str(quarter))
            search_keywords = [
                f"{year}年度第{quarter_num}季季報.pdf（另開視窗）",
                f"{year}年度第{quarter}季季報.pdf（另開視窗）",
            ]
        
        # 嘗試各種關鍵字找連結
        link = None
        for keyword in search_keywords:
            locator = page.locator(f'a[title="{keyword}"]')
            if locator.count() > 0:
                link = locator.first
                break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的下載連結"
            )
        
        # 取得 href
        href = link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        # 組合完整 URL
        if not href.startswith("http"):
            pdf_url = f"https://www.bok.com.tw{href}"
        else:
            pdf_url = href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
