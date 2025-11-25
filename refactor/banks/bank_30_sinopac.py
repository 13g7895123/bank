"""
永豐商業銀行 (30) - Bank SinoPac
網址: https://bank.sinopac.com/sinopacBT/about/investor/financial-statement.html
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class SinoPacDownloader(BaseBankDownloader):
    """永豐商業銀行下載器"""
    
    bank_name = "永豐商業銀行"
    bank_code = 30
    bank_url = "https://bank.sinopac.com/sinopacBT/about/investor/financial-statement.html"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        year_ad = year + 1911  # 民國轉西元
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        page.reload()
        page.wait_for_timeout(3000)
        
        # 找列表
        ul = page.query_selector("ul.sheet-list")
        if not ul:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列表"
            )
        
        links = ul.query_selector_all("a")
        
        pdf_url = None
        for link in links:
            text = link.inner_text()
            # 根據季度選擇合併或個體財報
            if quarter % 2 == 1:
                if str(year_ad) in text and quarter_text in text and "合併財報" in text:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://bank.sinopac.com{pdf_href}"
                    break
            else:
                if str(year_ad) in text and quarter_text in text and "個體財報" in text:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://bank.sinopac.com{pdf_href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
