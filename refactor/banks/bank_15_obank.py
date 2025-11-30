"""
王道商業銀行 (15) - O-Bank
網址: https://www.o-bank.com/common/regulation/regulation-financialreport

網頁結構：
- 有年份下拉選單，資料按年份分組在不同列表中
- 列表 1: 2025年資料, 列表 2: 2024年資料, ...
- 連結格式: "2025 Q1 財務業務資訊"
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class OBankDownloader(BaseBankDownloader):
    """王道商業銀行下載器"""
    
    bank_name = "王道商業銀行"
    bank_code = 15
    bank_url = "https://www.o-bank.com/common/regulation/regulation-financialreport"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 民國年轉西元年
        western_year = year + 1911
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        
        # 搜尋目標連結
        # 格式: "2024 Q4 財務業務資訊" 或 "2025 Q1 財務業務資訊"
        search_text = f"{western_year} Q{quarter}"
        
        # 在所有列表中搜尋
        all_lists = page.locator("ul.w3-ul.o-ul")
        target_link = None
        
        for i in range(all_lists.count()):
            ul = all_lists.nth(i)
            items = ul.locator("li")
            
            for j in range(items.count()):
                item_text = items.nth(j).inner_text()
                if search_text in item_text:
                    link = items.nth(j).locator("a").first
                    if link.count() > 0:
                        target_link = link
                        break
            if target_link:
                break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} ({western_year} Q{quarter}) 的下載連結"
            )
        
        href = target_link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得下載連結"
            )
        
        pdf_url = f"https://www.o-bank.com{href}" if not href.startswith("http") else href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
