"""
合作金庫商業銀行 (3) - Taiwan Cooperative Bank
網址: https://www.tcb-bank.com.tw/about-tcb/disclosure/bad-debt/asset-quality
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class TCBBankDownloader(BaseBankDownloader):
    """合作金庫商業銀行下載器"""
    
    bank_name = "合作金庫商業銀行"
    bank_code = 3
    bank_url = "https://www.tcb-bank.com.tw/about-tcb/disclosure/bad-debt/asset-quality"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        
        # 找所有項目
        items = await page.query_selector_all("li.c-list__item")
        
        pdf_url = None
        for item in items:
            title_div = await item.query_selector("div.c-list__title")
            if title_div:
                title = await title_div.inner_text()
                if str(year) in title and quarter_text in title:
                    link = await item.query_selector("a")
                    if link:
                        href = await link.get_attribute("href")
                        if href:
                            if not href.startswith("http"):
                                pdf_url = f"https://www.tcb-bank.com.tw{href}"
                            else:
                                pdf_url = href
                            break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
