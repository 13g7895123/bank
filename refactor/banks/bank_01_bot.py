"""
臺灣銀行 (1) - Bank of Taiwan
網址: https://www.bot.com.tw/tw/about/financial-statements/quarterly-report
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class BOTDownloader(BaseBankDownloader):
    """臺灣銀行下載器"""
    
    bank_name = "臺灣銀行"
    bank_code = 1
    bank_url = "https://www.bot.com.tw/tw/about/financial-statements/quarterly-report"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        # 前往財報頁面
        await page.goto(self.bank_url, wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # 切換到指定年份（下拉選單預設可能不是目標年份）
        try:
            select_button = page.locator("button.select-styled")
            current_year = (await select_button.text_content()).strip().replace("年", "")
            if str(year) != current_year:
                await select_button.click()
                await page.wait_for_timeout(1000)
                await page.locator(f"ul.select-options li:has-text('{year}年')").click()
                await page.wait_for_timeout(2000)
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"切換年份失敗: {e}"
            )
        
        # 網站 title 格式: "個體財務報告113年第2季.pdf(另開分頁)"
        target_title = f"個體財務報告{year}年第{quarter}季"
        
        # 找所有下載連結
        links = await page.query_selector_all("app-document-download a")
        
        pdf_url = None
        for link in links:
            title = await link.get_attribute("title") or ""
            if target_title in title:
                href = await link.get_attribute("href")
                if href:
                    pdf_url = href if href.startswith("http") else f"https://www.bot.com.tw{href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年第{quarter}季 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
