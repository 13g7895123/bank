"""
安泰商業銀行 (36) - EnTie Commercial Bank
網址: https://www.entiebank.com.tw/entie/disclosure-financial

網頁結構：
- 預設顯示「財務業務資訊」tab
- 表格格式: 年度標題行 (如 "114年度") + 季度資料行 (第一季~第四季)
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class EntieBankDownloader(BaseBankDownloader):
    """安泰商業銀行下載器"""
    
    bank_name = "安泰商業銀行"
    bank_code = 36
    bank_url = "https://www.entiebank.com.tw/entie/disclosure-financial"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_map = {1: "第一季", 2: "第二季", 3: "第三季", 4: "第四季"}
        quarter_text = quarter_map[quarter]
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(5000)
        
        # 找表格，解析年度與季度結構
        table = await page.query_selector("table")
        if not table:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        rows = await table.query_selector_all("tr")
        current_year = None
        pdf_url = None
        
        for row in rows:
            text = (await row.inner_text()).strip()
            
            # 檢查是否為年度行 (格式: "114年度")
            if "年度" in text and text.replace("年度", "").isdigit():
                current_year = int(text.replace("年度", ""))
                continue
            
            # 如果當前年度匹配，找季度連結
            if current_year == year:
                links = await row.query_selector_all("a")
                for link in links:
                    link_text = (await link.inner_text()).strip()
                    if link_text == quarter_text:
                        href = await link.get_attribute("href")
                        pdf_url = href if href.startswith("http") else f"https://www.entiebank.com.tw{href}"
                        break
                if pdf_url:
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
