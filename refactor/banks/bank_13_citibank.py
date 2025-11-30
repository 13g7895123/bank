"""
花旗（台灣）銀行 (13) - Citibank Taiwan
網址: https://www.citigroup.com/global/about-us/global-presence/zh-TW/taiwan/regulatory-disclosures

網頁結構：
- PDF 連結格式多變: 
  - taiwan-financial-information-2024-q4.pdf
  - taiwan-financial-information-2025q1.pdf
  - Web-FinancialInformation-2025Q3.pdf
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page
import re


class CitibankDownloader(BaseBankDownloader):
    """花旗（台灣）銀行下載器"""
    
    bank_name = "花旗（台灣）銀行"
    bank_code = 13
    bank_url = "https://www.citigroup.com/global/about-us/global-presence/zh-TW/taiwan/regulatory-disclosures"
    headless = False  # 強制使用有頭模式
    retry_with_head = False
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 民國年轉西元年
        western_year = year + 1911
        
        # 前往財報頁面
        await page.goto(self.bank_url, timeout=120000)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(8000)
        
        # 取得頁面 HTML 並搜尋 PDF
        html = await page.content()
        
        # 搜尋 PDF 連結模式
        # 格式可能是:
        # - taiwan-financial-information-2024-q4.pdf
        # - taiwan-financial-information-2025q1.pdf
        # - Web-FinancialInformation-2025Q3.pdf
        search_patterns = [
            rf'taiwan-financial-information-{western_year}-?q{quarter}\.pdf',
            rf'taiwan-financial[-_]information[-_]{western_year}[-_]?q{quarter}\.pdf',
            rf'Web-FinancialInformation-{western_year}Q{quarter}\.pdf',
            rf'FinancialInformation[-_]{western_year}[-_]?Q{quarter}\.pdf',
            rf'financial[-_]?report[-_]?{western_year}[-_]?q{quarter}\.pdf',
        ]
        
        pdf_url = None
        for pattern in search_patterns:
            matches = re.findall(rf'[^"\'\s>]*{pattern}', html, re.IGNORECASE)
            if matches:
                href = matches[0]
                if not href.startswith("http"):
                    pdf_url = f"https://www.citigroup.com{href}"
                else:
                    pdf_url = href
                break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} ({western_year}Q{quarter}) 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
