"""
京城商業銀行 (19) - King's Town Bank
網址: https://customer.ktb.com.tw/new/about/8d88e237

網頁結構：
- 每個年度有一個 h3 標題和一個 table.tftable
- 114年、113年、112年... 按順序排列
- 表格第一行是標題，後續行是季度資料
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class KTBDownloader(BaseBankDownloader):
    """京城商業銀行下載器"""
    
    bank_name = "京城商業銀行"
    bank_code = 19
    bank_url = "https://customer.ktb.com.tw/new/about/8d88e237"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # 找所有年度標題和表格
        year_titles = page.locator("div.ktbcontent h3")
        tables = page.locator("table.tftable")
        
        # 找到目標年度的索引
        target_index = -1
        for i in range(await year_titles.count()):
            title_text = await year_titles.nth(i).inner_text()
            try:
                year_on_page = int(title_text.split("年")[0])
                if year_on_page == year:
                    target_index = i
                    break
            except:
                continue
        
        if target_index < 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年 的資料"
            )
        
        if target_index >= await tables.count():
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年 的表格"
            )
        
        # 取得目標表格
        table = tables.nth(target_index)
        rows = table.locator("tr")
        
        # 搜尋目標季度
        # 格式: "第四季", "第三季", "第二季", "第一季"
        quarter_map = {1: "第一季", 2: "第二季", 3: "第三季", 4: "第四季"}
        target_quarter_text = quarter_map.get(quarter, "")
        
        target_link = None
        for i in range(1, await rows.count()):  # 跳過標題行
            row_text = await rows.nth(i).inner_text()
            if target_quarter_text in row_text:
                # 找第二個 td 中的連結（母子公司合併報表）
                tds = rows.nth(i).locator("td")
                if await tds.count() >= 2:
                    link = tds.nth(1).locator("a").first
                    if await link.count() > 0:
                        target_link = link
                        break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的下載連結"
            )
        
        href = await target_link.get_attribute("href")
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得下載連結"
            )
        
        pdf_url = href if href.startswith("http") else f"https://customer.ktb.com.tw{href}"
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
