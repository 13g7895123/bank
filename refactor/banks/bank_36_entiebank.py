"""
安泰商業銀行 (36) - EnTie Commercial Bank
網址: https://www.entiebank.com.tw/entie/disclosure-financial

網頁結構：
- 預設顯示「財務業務資訊」tab
- 表格格式: 年度標題行 + 季度資料行
- Q4 對應「年度」
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class EntieBankDownloader(BaseBankDownloader):
    """安泰商業銀行下載器"""
    
    bank_name = "安泰商業銀行"
    bank_code = 36
    bank_url = "https://www.entiebank.com.tw/entie/disclosure-financial"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(5000)
        
        # 搜尋連結
        # Q4 對應「年度」，Q1-Q3 對應「第X季」
        if quarter == 4:
            search_patterns = [f"{year}年度", f"{year}年第四季"]
        else:
            search_patterns = [f"{quarter_text}"]
        
        # 找所有連結
        links = page.locator("a")
        target_link = None
        
        for i in range(links.count()):
            text = links.nth(i).inner_text().strip()
            href = links.nth(i).get_attribute("href") or ""
            
            # 檢查是否匹配年度和季度
            if str(year) in text or str(year) in href:
                for pattern in search_patterns:
                    if pattern in text:
                        target_link = links.nth(i)
                        break
            if target_link:
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
        
        pdf_url = href if href.startswith("http") else f"https://www.entiebank.com.tw{href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
