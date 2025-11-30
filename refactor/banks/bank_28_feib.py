"""
遠東國際商業銀行 (28) - Far Eastern International Bank
網址: https://www.feib.com.tw/detail?id=349

網頁結構：
- 第二個下拉選單包含財務業務資訊
- 選項格式: "113 年第四季"
- value 是 PDF URL
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class FEIBDownloader(BaseBankDownloader):
    """遠東國際商業銀行下載器"""
    
    bank_name = "遠東國際商業銀行"
    bank_code = 28
    bank_url = "https://www.feib.com.tw/detail?id=349"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        
        # 找第二個下拉選單
        selects = page.locator("select")
        if selects.count() < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到選擇器"
            )
        
        # 搜尋目標選項: "113 年第四季"
        search_text = f"{year} 年{quarter_text}"
        
        options = selects.nth(1).locator("option")
        target_value = None
        
        for i in range(options.count()):
            text = options.nth(i).inner_text().strip()
            if search_text in text:
                target_value = options.nth(i).get_attribute("value")
                break
        
        if not target_value or target_value == "#top":
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        pdf_url = target_value if target_value.startswith("http") else f"https://www.feib.com.tw{target_value}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
