"""
第一商業銀行 (4) - First Commercial Bank
網址: https://www.firstbank.com.tw/sites/fcb/Statutory
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class FirstBankDownloader(BaseBankDownloader):
    """第一商業銀行下載器"""
    
    bank_name = "第一商業銀行"
    bank_code = 4
    bank_url = "https://www.firstbank.com.tw/sites/fcb/Statutory"
    headless = False  # 該銀行有 WAF 防護，需要有頭模式
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 建立要搜尋的 title 關鍵字
        # 網站格式多變，例如:
        # - "下載連結 - 點擊執行下載114年第三季..."
        # - "下載連結 - 點擊執行下載113年度第四季..."
        # - "下載連結 - 點擊執行下載114年度第一季..."
        search_keywords = [
            f"下載連結 - 點擊執行下載{year}年{quarter_text}銀行重要財務業務資訊",
            f"下載連結 - 點擊執行下載{year}年度{quarter_text}銀行重要財務業務資訊",
        ]
        
        # Q4 額外嘗試「全年度」
        if quarter == 4:
            search_keywords.extend([
                f"下載連結 - 點擊執行下載{year}年全年度銀行重要財務業務資訊",
                f"下載連結 - 點擊執行下載{year}年度全年度銀行重要財務業務資訊",
            ])
        
        # 嘗試各種關鍵字
        link = None
        for keyword in search_keywords:
            locator = page.locator(f'a[title*="{keyword}"]')
            if locator.count() > 0:
                link = locator.first
                break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的下載連結"
            )
        
        # 使用點擊下載（該銀行的連結需要 JavaScript 處理）
        return self.download_pdf_by_click(page, link, year, quarter)
