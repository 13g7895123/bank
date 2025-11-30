"""
上海商業儲蓄銀行 (7) - Shanghai Commercial & Savings Bank
網址: https://www.scsb.com.tw/content/about/about04_a_01.jsp

網頁結構：
- 有年份下拉選單 (id=generalQaList)，選項值為 #year_114、#year_113 等
- 下載連結 title 格式: "開新視窗(第一季)法定財務業務資訊(PDF)"
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class SCSBDownloader(BaseBankDownloader):
    """上海商業儲蓄銀行下載器"""
    
    bank_name = "上海商業儲蓄銀行"
    bank_code = 7
    bank_url = "https://www.scsb.com.tw/content/about/about04_a_01.jsp"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 步驟1: 切換年份下拉選單
        year_select = page.locator('select#generalQaList')
        if await year_select.count() > 0:
            year_option = f"#year_{year}"
            try:
                await year_select.select_option(year_option)
                await page.wait_for_timeout(1500)
            except:
                pass  # 如果選項不存在，繼續嘗試
        
        # 步驟2: 尋找對應季度的連結
        # 格式: "開新視窗(第一季)法定財務業務資訊(PDF)" 或 "開新視窗-第一季法定財務業務資訊(PDF)"
        search_patterns = [
            f"開新視窗({quarter_text})法定財務業務資訊(PDF)",
            f"開新視窗-{quarter_text}法定財務業務資訊(PDF)",
            f"({quarter_text})法定財務業務資訊",
            f"{quarter_text}法定財務業務資訊",
        ]
        
        link = None
        for pattern in search_patterns:
            locator = page.locator(f'a[title*="{pattern}"]')
            if await locator.count() > 0:
                link = locator.first
                break
        
        if not link:
            # 嘗試在下載區塊中搜尋
            links = page.locator("div.list-group.downloadLister a")
            for i in range(await links.count()):
                l = links.nth(i)
                title = await l.get_attribute("title") or await l.inner_text()
                if quarter_text in title and "法定財務" in title:
                    link = l
                    break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        href = await link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        if not href.startswith("http"):
            pdf_url = f"https://www.scsb.com.tw/content/about/{href}"
        else:
            pdf_url = href
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
