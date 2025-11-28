"""
凱基商業銀行 (32) - KGI Bank
網址: https://www.kgibank.com.tw/zh-tw/about-us/financial-summary

URL 格式說明：
- 2015-2022: /{year}/{year}-q{q}-consolidated-financial-statement.pdf
- 2023: /2023-financial-report/{year}-q{q}-consolidated-financial-statement.pdf
- 2024-2025: /{year}/{year}-q{q}-consol-financial.pdf
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class KGIBankDownloader(BaseBankDownloader):
    """凱基商業銀行下載器"""
    
    bank_name = "凱基商業銀行"
    bank_code = 32
    bank_url = "https://www.kgibank.com.tw/zh-tw/about-us/financial-summary"
    
    def _build_pdf_url(self, year_ad: int, quarter: int) -> str:
        """
        根據年份構建合併財務報告的 PDF URL
        
        Args:
            year_ad: 西元年
            quarter: 季度 (1-4)
        
        Returns:
            PDF 下載 URL
        """
        base = "https://www.kgibank.com.tw/zh-tw/-/media/files/kgib/financial-summary/financial-report"
        
        if year_ad >= 2024:
            # 2024 年起使用新格式
            return f"{base}/{year_ad}/{year_ad}-q{quarter}-consol-financial.pdf"
        elif year_ad == 2023:
            # 2023 年使用特殊路徑
            return f"{base}/2023-financial-report/{year_ad}-q{quarter}-consolidated-financial-statement.pdf"
        else:
            # 2022 年及之前使用舊格式
            return f"{base}/{year_ad}/{year_ad}-q{quarter}-consolidated-financial-statement.pdf"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        year_ad = year + 1911  # 民國轉西元
        
        # 先嘗試直接構建 URL 下載
        pdf_url = self._build_pdf_url(year_ad, quarter)
        
        # 驗證 URL 是否可用
        response = page.request.head(pdf_url)
        if response.ok:
            return self.download_pdf_from_url(page, pdf_url, year, quarter)
        
        # 如果直接 URL 失敗，使用網頁動態抓取
        return self._download_from_webpage(page, year, quarter, year_ad, quarter_text)
    
    def _download_from_webpage(self, page: Page, year: int, quarter: int, 
                                year_ad: int, quarter_text: str) -> DownloadResult:
        """從網頁動態抓取財務報告連結"""
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 滾動到財務報告區塊
        page.evaluate("window.scrollTo(0, 800)")
        page.wait_for_timeout(500)
        
        # 找到年份選擇按鈕
        year_btn = None
        arrows = page.query_selector_all("[class*='arrowDown']")
        for arrow in arrows:
            if arrow.is_visible():
                text = arrow.inner_text().strip()
                if text.isdigit() and 2015 <= int(text) <= 2030:
                    year_btn = arrow
                    break
        
        if not year_btn:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到年份選擇按鈕"
            )
        
        # 點擊年份按鈕展開下拉選單
        year_btn.click()
        page.wait_for_timeout(800)
        
        # 選擇目標年份
        year_options = page.query_selector_all("a, li, div")
        year_selected = False
        for opt in year_options:
            if opt.is_visible():
                text = opt.inner_text().strip()
                if text == str(year_ad):
                    opt.click()
                    page.wait_for_timeout(1500)
                    year_selected = True
                    break
        
        if not year_selected:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year_ad} 年的選項"
            )
        
        # 查找合併財務報告連結
        links = page.query_selector_all("a[href*='financial-report']")
        pdf_url = None
        
        for link in links:
            href = link.get_attribute("href") or ""
            # 確認是目標年份和季度的合併財務報告
            if str(year_ad) in href and f"-q{quarter}-" in href:
                # 優先選擇合併財務報告 (consolidated 或 consol)
                if "consolidated" in href.lower() or "consol" in href.lower():
                    # 排除非合併財務報告 (non-consolidated)
                    if "non-consolidated" not in href.lower():
                        pdf_url = href if href.startswith("http") else f"https://www.kgibank.com.tw{href}"
                        break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的合併財務報告"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
