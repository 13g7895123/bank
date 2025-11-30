"""
臺灣土地銀行 (2) - Land Bank of Taiwan
網址: https://www.landbank.com.tw/Category/Items/財務業務資訊-財報

表格結構說明：
- 表格每兩行為一組：第一行是年度標題+季度標題，第二行是對應的下載連結
- row[0]: td[0]=114年度, td[1]=第一季標題, td[2]=第二季標題, td[3]=第三季標題, td[4]=全年度標題
- row[1]: td[0]=財務報告連結, td[1]=財務報告連結, td[2]=財務報告連結, td[3]=財務報告連結
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class LandBankDownloader(BaseBankDownloader):
    """臺灣土地銀行下載器"""
    
    bank_name = "臺灣土地銀行"
    bank_code = 2
    bank_url = "https://www.landbank.com.tw/Category/Items/%E8%B2%A1%E5%8B%99%E6%A5%AD%E5%8B%99%E8%B3%87%E8%A8%8A-%E8%B2%A1%E5%A0%B1"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財務業務資訊頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)  # 等待頁面完全載入
        
        # 步驟1: 點擊「銀行重要財務業務資訊」展開按鈕
        expand_btn = page.locator('[aria-label="按下後展開資訊"][title="銀行重要財務業務資訊"]')
        
        if await expand_btn.count() == 0:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="找不到「銀行重要財務業務資訊」展開按鈕"
            )
        
        # 點擊展開
        await expand_btn.click()
        await page.wait_for_timeout(1500)  # 等待展開動畫
        
        # 步驟2: 找到包含指定年度的表格列
        # 表格結構：年度標題在 td[0]，連結在下一行
        year_str = f"{year}年度"
        rows = page.locator('tbody tr')
        row_count = await rows.count()
        
        target_row_idx = -1
        for i in range(row_count):
            row = rows.nth(i)
            first_td = row.locator('td').first
            if await first_td.count() > 0:
                text = (await first_td.text_content()).strip()
                if year_str in text:
                    target_row_idx = i
                    break
        
        if target_row_idx == -1:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year} 年度的資料列"
            )
        
        # 步驟3: 取得下一行（連結行）的對應季度連結
        # 季度對應欄位: Q1=td[0], Q2=td[1], Q3=td[2], Q4=td[3]
        link_row = rows.nth(target_row_idx + 1)
        tds = link_row.locator('td')
        td_count = await tds.count()
        
        # 季度對應的 td 索引（第一季=0, 第二季=1, 第三季=2, 第四季/全年度=3）
        quarter_td_idx = quarter - 1
        
        if td_count <= quarter_td_idx:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的下載連結"
            )
        
        target_td = tds.nth(quarter_td_idx)
        quarter_link = target_td.locator('a:has-text("財務報告")')
        
        if await quarter_link.count() == 0:
            # 嘗試找任何 a 連結
            quarter_link = target_td.locator('a')
        
        if await quarter_link.count() == 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的財務報告連結"
            )
        
        # 取得 PDF URL
        href = await quarter_link.first.get_attribute("href")
        
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        # 組合完整 URL
        if not href.startswith("http"):
            pdf_url = f"https://www.landbank.com.tw{href}"
        else:
            pdf_url = href
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
