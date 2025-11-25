"""
將來商業銀行 (41) - Next Bank
網址: https://www.nextbank.com.tw/disclosures/download/52831e76d4000000d9ee07510ffac025
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class NextBankDownloader(BaseBankDownloader):
    """將來商業銀行下載器"""
    
    bank_name = "將來商業銀行"
    bank_code = 41
    bank_url = "https://www.nextbank.com.tw/disclosures/download/52831e76d4000000d9ee07510ffac025"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找所有標題 (b 標籤)
        b_tags = page.query_selector_all("b")
        
        pdf_url = None
        for i, b_tag in enumerate(b_tags):
            text = b_tag.inner_text()
            if str(year) in text and quarter_text in text:
                # 找同層級的連結
                parent = b_tag.evaluate_handle("el => el.parentElement")
                link = parent.as_element().query_selector("a")
                if link:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.nextbank.com.tw{pdf_href}"
                    break
        
        if not pdf_url:
            # 嘗試直接找包含年度和季度的連結
            links = page.query_selector_all("a")
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.inner_text()
                if (str(year) in text or str(year) in href) and (quarter_text in text or f"Q{quarter}" in href):
                    pdf_url = href if href.startswith("http") else f"https://www.nextbank.com.tw{href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
