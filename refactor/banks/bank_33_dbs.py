"""
星展(台灣)商業銀行 (33) - DBS Bank (Taiwan)
網址: https://www.dbs.com.tw/personal-zh/legal-disclaimers-and-announcements.page

財務資訊揭露 > 重要財務業務資訊

URL 格式說明：
- 2024-2025: /iwov-resources/pdf/LegalDisclaimersandAnnouncements/03_financial_information_disclosure/01_financial_and_business_information/SUB_InternetReport_{year}Q{quarter}.pdf
- 2018-2023: /iwov-resources/pdf/legal disclaimers and announcements/03_financial information disclosure/01_financial and business information/(SUB)Internet Report_{year}Q{quarter}.pdf
- 更早年份: 檔名格式不統一，需從網頁動態抓取
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page
from urllib.parse import quote


class DBSBankDownloader(BaseBankDownloader):
    """星展(台灣)商業銀行下載器"""
    
    bank_name = "星展(台灣)商業銀行"
    bank_code = 33
    bank_url = "https://www.dbs.com.tw/personal-zh/legal-disclaimers-and-announcements.page"
    
    def _build_pdf_url(self, year_ad: int, quarter: int) -> str:
        """
        根據年份構建重要財務業務資訊的 PDF URL
        
        Args:
            year_ad: 西元年
            quarter: 季度 (1-4)
        
        Returns:
            PDF 下載 URL
        """
        base = "https://www.dbs.com.tw/iwov-resources/pdf"
        
        if year_ad >= 2024:
            # 2024 年起使用新格式 (無空格路徑)
            return f"{base}/LegalDisclaimersandAnnouncements/03_financial_information_disclosure/01_financial_and_business_information/SUB_InternetReport_{year_ad}Q{quarter}.pdf"
        elif year_ad >= 2018:
            # 2018-2023 年使用舊格式 (有空格路徑)
            path = f"legal disclaimers and announcements/03_financial information disclosure/01_financial and business information/(SUB)Internet Report_{year_ad}Q{quarter}.pdf"
            return f"{base}/{quote(path, safe='/()')}"
        else:
            # 更早年份格式不統一，返回 None 讓後續從網頁抓取
            return None
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        year_ad = year + 1911  # 民國轉西元
        
        # 先嘗試直接構建 URL 下載
        pdf_url = self._build_pdf_url(year_ad, quarter)
        if pdf_url:
            response = await page.request.head(pdf_url)
            if response.ok:
                return await self.download_pdf_from_url(page, pdf_url, year, quarter)
        
        # 如果直接 URL 失敗，使用網頁動態抓取
        return await self._download_from_webpage(page, year, quarter, year_ad)
    
    async def _download_from_webpage(self, page: Page, year: int, quarter: int, 
                                year_ad: int) -> DownloadResult:
        """從網頁動態抓取財務報告連結"""
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)
        
        # 點擊財務資訊揭露展開
        fin_link = page.locator("text=財務資訊揭露").first
        if await fin_link.count() > 0:
            await fin_link.click()
            await page.wait_for_timeout(1000)
        
        # 點擊重要財務業務資訊展開
        important_fin = page.locator("text=重要財務業務資訊").first
        if await important_fin.count() > 0:
            await important_fin.click()
            await page.wait_for_timeout(1500)
        
        # 搜尋目標連結 - 格式為 "2025年3季" 或 "2025年1季"
        search_text = f"{year_ad}年{quarter}季"
        
        # 查找所有 PDF 連結
        links = await page.query_selector_all("a[href*='.pdf']")
        pdf_url = None
        
        for link in links:
            try:
                text = (await link.inner_text()).strip()
                href = await link.get_attribute("href") or ""
                
                # 確認是目標年份和季度的 SUB (子公司) 報告
                if text == search_text and "SUB" in href.upper():
                    pdf_url = href if href.startswith("http") else f"https://www.dbs.com.tw{href}"
                    break
            except:
                continue
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的重要財務業務資訊"
            )
        
        return await self.download_pdf_from_url(page, pdf_url, year, quarter)
