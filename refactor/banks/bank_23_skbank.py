"""
臺灣新光商業銀行 (23) - Shin Kong Bank
網址: https://www.skbank.com.tw/QFI
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class SKBankDownloader(BaseBankDownloader):
    """臺灣新光商業銀行下載器"""
    
    bank_name = "臺灣新光商業銀行"
    bank_code = 23
    bank_url = "https://www.skbank.com.tw/QFI"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        search_text = f"{year}年{quarter_text}"  # 例如: 114年第三季
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        
        # 在 ul li 結構中找到目標季度的連結
        # li 中有 a 元素，會寫「114年第三季」這樣的字樣
        target_link = None
        li_elements = await page.query_selector_all("ul li")
        
        for li in li_elements:
            link = li.query_selector("a")
            if link:
                link_text = await link.inner_text()
                if str(year) in link_text and quarter_text in link_text:
                    target_link = link
                    break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {search_text} 的連結"
            )
        
        # 點擊連結進入子頁面
        await target_link.click()
        await page.wait_for_load_state("networkidle")
        
        # 在子頁面找「資產品質」連結
        asset_quality_link = None
        all_links = await page.query_selector_all("a")
        
        for link in all_links:
            link_text = await link.inner_text()
            if "資產品質" in link_text:
                asset_quality_link = link
                break
        
        if not asset_quality_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到「資產品質」連結"
            )
        
        # 取得 PDF 連結並下載
        pdf_href = await asset_quality_link.get_attribute("href")
        if not pdf_href:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="「資產品質」連結無 href 屬性"
            )
        
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.skbank.com.tw{pdf_href}"
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
