"""
元大商業銀行 (29) - Yuanta Commercial Bank
網址: https://www.yuantabank.com.tw/bank/bulletin/statutoryDisclosure/list.do

網頁結構：
- 奇數季度頁面: layer_id=26a836f2b60000019f0b（財務業務資訊）
- 偶數季度頁面: layer_id=26a83777c500000745d9（財務報告）
- Q4 對應「年度」或「第四季」
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class YuantaBankDownloader(BaseBankDownloader):
    """元大商業銀行下載器"""
    
    bank_name = "元大商業銀行"
    bank_code = 29
    bank_url = "https://www.yuantabank.com.tw/bank/bulletin/statutoryDisclosure/list.do"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 使用財務業務資訊頁面
        url = f"{self.bank_url}?layer_id=26a836f2b60000019f0b"
        
        # 搜尋關鍵字
        if quarter == 4:
            search_patterns = [f"{year}年度", f"{year}年第四季", f"{year}年度第四季"]
        else:
            search_patterns = [f"{year}年度{quarter_text}", f"{year}年{quarter_text}"]
        
        # 前往財報頁面
        await page.goto(url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 搜尋連結
        links = page.locator("a")
        target_link = None
        
        for i in range(await links.count()):
            text = await links.nth(i).inner_text().strip()
            for pattern in search_patterns:
                if pattern in text:
                    target_link = links.nth(i)
                    break
            if target_link:
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
        
        pdf_url = href if href.startswith("http") else f"https://www.yuantabank.com.tw{href}"
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
