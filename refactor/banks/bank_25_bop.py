"""
板信商業銀行 (25) - Bank of Panhsin
網址: https://www.bop.com.tw/Footer/Financial_Report?tni=110&refid=null

網頁結構：
- 第二個表格是「重要財務業務資訊」（季度報告）
- 表頭: 年度, 第一季, 第二季, 第三季, 第四季
- 連結格式: 113_Q4.pdf
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class BOPDownloader(BaseBankDownloader):
    """板信商業銀行下載器"""
    
    bank_name = "板信商業銀行"
    bank_code = 25
    bank_url = "https://www.bop.com.tw/Footer/Financial_Report?tni=110&refid=null"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 搜尋連結：格式為 113_Q4.pdf
        search_text = f"{year}_Q{quarter}.pdf"
        
        links = page.locator("a")
        target_link = None
        
        for i in range(await links.count()):
            text = await links.nth(i).inner_text().strip()
            if search_text in text:
                target_link = links.nth(i)
                break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        href = await target_link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得下載連結"
            )
        
        # 處理相對路徑
        if href.startswith("../"):
            pdf_url = f"https://www.bop.com.tw/{href.replace('../', '')}"
        elif not href.startswith("http"):
            pdf_url = f"https://www.bop.com.tw/{href.lstrip('/')}"
        else:
            pdf_url = href
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
