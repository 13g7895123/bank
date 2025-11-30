"""
將來商業銀行 (41) - Next Bank
網址: https://www.nextbank.com.tw/disclosures/download/52831e76d4000000d9ee07510ffac025

網頁結構：
- 使用 b 標籤顯示季度標題（如 "114年度第一季"）
- 每個季度區塊有多個連結，包括「資產品質」
- 連結 href 沒有年份，需要根據區塊位置判斷
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class NextBankDownloader(BaseBankDownloader):
    """將來商業銀行下載器"""
    
    bank_name = "將來商業銀行"
    bank_code = 41
    bank_url = "https://www.nextbank.com.tw/disclosures/download/52831e76d4000000d9ee07510ffac025"
    headless = False  # 強制使用有頭模式
    retry_with_head = False
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url, timeout=120000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(8000)
        
        # 搜尋目標季度: "113年度第四季" 或 "114年度第一季"
        search_text = f"{year}年度{quarter_text}"
        
        # 找所有 b 標籤（季度標題）
        b_tags = page.locator("b")
        target_index = -1
        
        for i in range(b_tags.count()):
            text = b_tags.nth(i).inner_text().strip()
            if search_text in text:
                target_index = i
                break
        
        if target_index < 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的區塊"
            )
        
        # 找「資產品質」連結
        # 因為每個季度區塊都有一個「資產品質」連結，按順序對應
        asset_quality_links = page.locator('a:has-text("資產品質")')
        
        if target_index >= asset_quality_links.count():
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資產品質連結"
            )
        
        target_link = asset_quality_links.nth(target_index)
        href = target_link.get_attribute("href")
        
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得下載連結"
            )
        
        pdf_url = href if href.startswith("http") else f"https://www.nextbank.com.tw{href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
