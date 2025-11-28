"""
永豐商業銀行 (30) - Bank SinoPac
網址: https://bank.sinopac.com/sinopacBT/about/investor/financial-statement.html
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class SinoPacDownloader(BaseBankDownloader):
    """永豐商業銀行下載器"""
    
    bank_name = "永豐商業銀行"
    bank_code = 30
    bank_url = "https://bank.sinopac.com/sinopacBT/about/investor/financial-statement.html"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        year_ad = year + 1911  # 民國轉西元
        
        # 前往財報頁面
        page.goto(self.bank_url, timeout=60000)
        page.wait_for_timeout(5000)
        
        # 點擊自定義選擇器打開下拉選單
        styled_div = page.query_selector("div.select-styled")
        if not styled_div:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到年度選擇器"
            )
        
        styled_div.click()
        page.wait_for_timeout(1000)
        
        # 選擇目標年份
        year_option = page.query_selector(f'li[rel="{year_ad}"]')
        if not year_option:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year_ad} 年的選項"
            )
        
        year_option.click()
        page.wait_for_timeout(3000)
        
        # 找列表中的項目
        sheet_list = page.query_selector("ul.sheet-list")
        if not sheet_list:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列表"
            )
        
        items = sheet_list.query_selector_all("li")
        
        # 優先尋找個體財報，沒有的話才用合併財報
        target_link = None
        fallback_link = None
        
        for item in items:
            link = item.query_selector("a")
            if not link:
                continue
            
            text = link.inner_text()
            
            # 檢查是否符合目標季度
            if str(year_ad) in text and quarter_text in text:
                if "個體財報" in text:
                    target_link = link
                    break
                elif "合併財報" in text and not fallback_link:
                    fallback_link = link
        
        # 如果沒有個體財報，使用合併財報
        if not target_link:
            target_link = fallback_link
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的財報"
            )
        
        # 取得 PDF 連結
        pdf_href = target_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://bank.sinopac.com{pdf_href}"
        
        # 點擊連結打開新分頁
        with page.context.expect_page() as new_page_info:
            target_link.evaluate("el => el.click()")
        
        new_page = new_page_info.value
        new_page.wait_for_timeout(3000)
        
        # 從新分頁下載 PDF
        result = self.download_pdf_from_url(new_page, pdf_url, year, quarter)
        
        # 關閉新分頁
        new_page.close()
        
        return result
