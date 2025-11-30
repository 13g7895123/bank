"""
華泰商業銀行 (22) - Hwatai Bank
網址: https://www.hwataibank.com.tw/public/public02-01/

網頁結構：
- 連結文字使用中文數字（一百一十三年）
- href 包含 113Q4.pdf 這樣的格式
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class HwataiBankDownloader(BaseBankDownloader):
    """華泰商業銀行下載器"""
    
    bank_name = "華泰商業銀行"
    bank_code = 22
    bank_url = "https://www.hwataibank.com.tw/public/public02-01/"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 搜尋 href 包含 113Q4.pdf 這樣格式的連結
        search_pattern = f"{year}Q{quarter}.pdf"
        
        links = page.locator("a")
        target_link = None
        
        for i in range(await links.count()):
            href = await links.nth(i).get_attribute("href") or ""
            if search_pattern in href:
                target_link = links.nth(i)
                break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        pdf_url = await target_link.get_attribute("href")
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
