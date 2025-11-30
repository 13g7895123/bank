"""
聯邦商業銀行 (27) - Union Bank of Taiwan
網址: https://www.ubot.com.tw/investors
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class UBOTDownloader(BaseBankDownloader):
    """聯邦商業銀行下載器"""
    
    bank_name = "聯邦商業銀行"
    bank_code = 27
    bank_url = "https://www.ubot.com.tw/investors"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(5000)
        
        # 找到 thead 中有 p 元素且 text 為「財務資訊」的表格（第一個 table）
        table = await page.query_selector("table")
        if not table:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到表格"
            )
        
        tbody = table.query_selector("tbody")
        if not tbody:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 tbody"
            )
        
        # 在 tbody 中找到目標年度的 tr
        target_row = None
        rows = tbody.query_selector_all("tr")
        
        for row in rows:
            first_td = row.query_selector("td")
            if first_td:
                td_text = (await first_td.text_content()).strip()
                if f"{year}年度" in td_text:
                    target_row = row
                    break
        
        if not target_row:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年度 的資料"
            )
        
        # 取得所有 td，第一個是年度，後面依序是 Q1, Q2, Q3, Q4(全年度)
        # Q1 = td[1], Q2 = td[2], Q3 = td[3], Q4 = td[4]
        tds = target_row.query_selector_all("td")
        
        if len(tds) <= quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的欄位"
            )
        
        target_td = tds[quarter]  # quarter 1-4 對應 td[1]-td[4]
        
        # 在目標 td 中找 a 元素
        target_link = target_td.query_selector("a")
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的連結"
            )
        
        # 取得 href 屬性，組成完整 URL
        pdf_href = await target_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.ubot.com.tw{pdf_href}"
        
        # 監聯新分頁，用 JavaScript 點擊連結
        async with page.context.expect_page() as new_page_info:
            await target_link.evaluate("el => el.click()")
        
        new_page = await new_page_info.value
        await new_page.wait_for_load_state("networkidle")
        
        # 從新分頁下載 PDF
        result = await self.download_pdf_from_url(new_page, pdf_url, year, quarter)
        
        # 關閉新分頁
        await new_page.close()
        
        return result
