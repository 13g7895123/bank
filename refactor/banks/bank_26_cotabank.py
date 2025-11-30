"""
三信商業銀行 (26) - Cota Commercial Bank
網址: https://www.cotabank.com.tw/web/public/expose/

網頁結構：
- 側邊欄點選「重要財務業務資訊」後，右側顯示各年度季度連結
- 連結格式: "3月", "6月", "9月", "12月" 對應各季度
- href 格式: /web/wp-content/uploads/files/expose/MNews{年}{月}.pdf
- 例如: MNews11403.pdf = 114年3月 = Q1
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class CotaBankDownloader(BaseBankDownloader):
    """三信商業銀行下載器"""
    
    bank_name = "三信商業銀行"
    bank_code = 26
    bank_url = "https://www.cotabank.com.tw/web/public/expose/"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 季度對應月份（格式為兩位數）
        quarter_month_map = {1: "03", 2: "06", 3: "09", 4: "12"}
        target_month = quarter_month_map.get(quarter, "")
        
        # 直接組合 PDF URL（MNews 格式）
        # 格式: MNews{年}{月}.pdf，例如 MNews11403.pdf
        pdf_filename = f"MNews{year}{target_month}.pdf"
        pdf_url = f"https://www.cotabank.com.tw/web/wp-content/uploads/files/expose/{pdf_filename}"
        
        # 前往財報頁面確認連結存在
        await page.goto(self.bank_url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(2000)
        
        # 確認頁面上有對應的連結
        links = page.locator(f'a[href*="{pdf_filename}"]')
        if await links.count() == 0:
            # 嘗試搜尋文字連結
            month_text = str(int(target_month))  # "03" -> "3"
            year_links = page.locator(f'a:has-text("{month_text}月")')
            found = False
            for i in range(await year_links.count()):
                href = await year_links.nth(i).get_attribute("href") or ""
                if f"MNews{year}" in href:
                    found = True
                    break
            
            if not found:
                return DownloadResult(
                    status=DownloadStatus.NO_DATA,
                    message=f"找不到 {year}年{quarter_text} 的資料"
                )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
