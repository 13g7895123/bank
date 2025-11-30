"""
國泰世華商業銀行 (9) - Cathay United Bank
網址: https://www.cathaybk.com.tw/cathaybk/personal/about/news/announce/

網頁特性：
- 載入較慢，需要較長超時時間
- 有多個下載區塊，需搜尋特定季度
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class CathayDownloader(BaseBankDownloader):
    """國泰世華商業銀行下載器"""
    
    bank_name = "國泰世華商業銀行"
    bank_code = 9
    bank_url = "https://www.cathaybk.com.tw/cathaybk/personal/about/news/announce/"
    headless = False  # 強制使用有頭模式
    retry_with_head = False
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面（增加超時時間）
        await page.goto(self.bank_url, timeout=120000)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # 搜尋關鍵字
        # 格式可能是: "114年度 第一季財務報告" 或 "114年第1季"
        search_patterns = [
            f"{year}年度 {quarter_text}財務報告",
            f"{year}年度{quarter_text}財務報告",
            f"{year}年{quarter_text}",
            f"{year}年度 第{quarter}季",
        ]
        
        # 找所有下載區塊
        download_divs = page.locator("div.cubre-m-download")
        count = await download_divs.count()
        
        if count == 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載區塊"
            )
        
        # 搜尋包含目標季度的區塊
        target_div = None
        for i in range(count):
            div = download_divs.nth(i)
            div_text = await div.inner_text()
            
            for pattern in search_patterns:
                if pattern in div_text:
                    target_div = div
                    break
            if target_div:
                break
        
        if not target_div:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        # 找下載連結
        link = target_div.locator("a[href*='.pdf'], a[href*='download']").first
        if await link.count() == 0:
            link = target_div.locator("div.cubre-o-action__item a").first
        
        if await link.count() == 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        href = await link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得下載連結"
            )
        
        if not href.startswith("http"):
            pdf_url = f"https://www.cathaybk.com.tw{href}"
        else:
            pdf_url = href
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
