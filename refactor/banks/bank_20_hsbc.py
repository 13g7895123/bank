"""
匯豐(台灣)商業銀行 (20) - HSBC Bank (Taiwan)
網址: https://www.hsbc.com.tw/help/announcements/
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class HSBCDownloader(BaseBankDownloader):
    """匯豐(台灣)商業銀行下載器"""
    
    bank_name = "匯豐(台灣)商業銀行"
    bank_code = 20
    bank_url = "https://www.hsbc.com.tw/help/announcements/"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        year_ad = year + 1911  # 民國轉西元
        quarter_map = {1: "第一季", 2: "第二季", 3: "第三季", 4: "第四季"}
        quarter_text = quarter_map.get(quarter, "")
        
        # 前往財報頁面（增加 timeout）
        await page.goto(self.bank_url, timeout=120000)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # 搜尋目標連結 - 格式: "2025年第一季重要財務業務資訊"
        target_text = f"{year_ad}年{quarter_text}重要財務業務資訊"
        
        # 找所有連結
        links = await page.query_selector_all("a")
        
        pdf_url = None
        for link in links:
            text = (await link.inner_text()).strip()
            href = await link.get_attribute("href") or ""
            
            # 匹配目標文字
            if target_text in text and href.endswith(".pdf"):
                if not href.startswith("http"):
                    pdf_url = f"https://www.hsbc.com.tw{href}"
                else:
                    pdf_url = href
                break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
