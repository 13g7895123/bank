"""
連線商業銀行 (40) - LINE Bank
網址: https://corp.linebank.com.tw/zh-tw/company-financial
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class LineBankDownloader(BaseBankDownloader):
    """連線商業銀行下載器"""
    
    bank_name = "連線商業銀行"
    bank_code = 40
    bank_url = "https://corp.linebank.com.tw/zh-tw/company-financial"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        
        # 找 tabs 內容
        tab_contents = await page.query_selector_all("div.el-tabs__content")
        if len(tab_contents) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        # 找附件區
        attachments = tab_contents[1].query_selector_all("div.attachments.layout-row")
        
        pdf_url = None
        for attachment in attachments:
            link = attachment.query_selector("a")
            if link:
                title = await link.get_attribute("title") or link.inner_text()
                if str(year) in title and quarter_text in title:
                    pdf_href = await link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://corp.linebank.com.tw{pdf_href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
