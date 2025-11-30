"""
瑞興商業銀行 (21) - Taipei Star Bank
網址: https://www.taipeistarbank.com.tw/StatutoryDisclosure/FinancialReports
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class TaipeiStarBankDownloader(BaseBankDownloader):
    """瑞興商業銀行下載器"""
    
    bank_name = "瑞興商業銀行"
    bank_code = 21
    bank_url = "https://www.taipeistarbank.com.tw/StatutoryDisclosure/FinancialReports"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        
        # 找表格中的連結
        tds = await page.query_selector_all("tbody td.tb_td")
        
        pdf_url = None
        for td in tds:
            link = td.query_selector("a")
            if link:
                title = await link.inner_text()
                if str(year) in title and quarter_text in title:
                    href = await link.get_attribute("href")
                    pdf_url = f"https://www.taipeistarbank.com.tw{href}" if not href.startswith("http") else href
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
