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
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        target_text = f"{year}年度{quarter_text}銀行重要財務業務資訊之補充揭露"
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找表格中的目標列
        rows = page.query_selector_all("tbody tr")
        
        pdf_url = None
        for row in rows:
            tds = row.query_selector_all("td")
            if len(tds) >= 3:
                first_td_text = tds[0].inner_text()
                if target_text in first_td_text:
                    # PDF 連結通常在第三個 td
                    link = tds[2].query_selector("a") or tds[1].query_selector("a")
                    if link:
                        href = link.get_attribute("href")
                        if href:
                            pdf_url = href if href.startswith("http") else f"https://www.firstbank.com.tw{href}"
                            break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
