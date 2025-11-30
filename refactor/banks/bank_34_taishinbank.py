"""
台新國際商業銀行 (34) - Taishin International Bank
網址: https://www.taishinbank.com.tw/TSB/about-taishin/brief-introduction-to-the-bank/financeInfo
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class TaishinBankDownloader(BaseBankDownloader):
    """台新國際商業銀行下載器"""
    
    bank_name = "台新國際商業銀行"
    bank_code = 34
    bank_url = "https://www.taishinbank.com.tw/TSB/about-taishin/brief-introduction-to-the-bank/financeInfo"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        year_ad = year + 1911  # 民國轉西元
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        
        # 使用 JavaScript 切換年份下拉選單
        await page.evaluate(f'''() => {{
            const selects = document.querySelectorAll('select');
            const yearSelect = selects[selects.length - 1];
            if (yearSelect) {{
                yearSelect.value = '{year_ad}';
                yearSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }}''')
        await page.wait_for_timeout(2000)
        
        # 找資料區塊
        table = await page.query_selector("div.ts-comp-076.btn-two")
        if not table:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        text_blocks = table.query_selector_all("div.text-block")
        btn_blocks = table.query_selector_all("div.btnnn")
        
        pdf_url = None
        for i, text_div in enumerate(text_blocks):
            if i >= len(btn_blocks):
                break
            text = await text_div.inner_text()
            
            if str(year_ad) in text and f"Q{quarter}" in text and "財務業務資訊" in text:
                link = btn_blocks[i].query_selector("a")
                if link:
                    pdf_href = await link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.taishinbank.com.tw{pdf_href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年Q{quarter} 的資料"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
