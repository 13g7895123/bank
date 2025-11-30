"""
三信商業銀行 (26) - Cota Commercial Bank
網址: https://www.cotabank.com.tw/web/public/expose/#tab-財務業務資訊

網頁結構：
- 連結格式: "113 年 12月" 對應 Q4
- href 格式: /web/wp-content/uploads/files/expose/riskman/113_02.pdf
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CotaBankDownloader(BaseBankDownloader):
    """三信商業銀行下載器"""
    
    bank_name = "三信商業銀行"
    bank_code = 26
    bank_url = "https://www.cotabank.com.tw/web/public/expose/#tab-財務業務資訊"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 季度對應月份
        quarter_month_map = {1: "3", 2: "6", 3: "9", 4: "12"}
        target_month = quarter_month_map.get(quarter, "")
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(3000)
        
        # 搜尋連結：格式為 "113 年 3月" 或 "113 年 12月"
        links = page.locator("a")
        target_link = None
        
        for i in range(links.count()):
            text = links.nth(i).inner_text().strip()
            href = links.nth(i).get_attribute("href") or ""
            # 匹配 "113 年 12月" 格式，且 href 包含 riskman（財務業務資訊）
            if str(year) in text and f"{target_month}月" in text and "riskman" in href:
                target_link = links.nth(i)
                break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        href = target_link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得下載連結"
            )
        
        pdf_url = f"https://www.cotabank.com.tw{href}" if not href.startswith("http") else href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
