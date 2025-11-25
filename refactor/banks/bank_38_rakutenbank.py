"""
樂天國際商業銀行 (38) - Rakuten Bank
網址: https://www.rakuten-bank.com.tw/portal/other/disclosure
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class RakutenBankDownloader(BaseBankDownloader):
    """樂天國際商業銀行下載器"""
    
    bank_name = "樂天國際商業銀行"
    bank_code = 38
    bank_url = "https://www.rakuten-bank.com.tw/portal/other/disclosure"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 點擊財務資訊 tab
        finance_tab = page.query_selector("#finance")
        if finance_tab:
            finance_tab.click()
            page.wait_for_timeout(2000)
        
        # 找所有折疊區塊
        blocks = page.query_selector_all("div.collapse-block-head")
        
        target_index = -1
        for i, block in enumerate(blocks[:2]):  # 只檢查前兩個
            title_div = block.query_selector("div.txt.collapse-block-title")
            if title_div:
                title = title_div.inner_text()
                if str(year) in title and quarter_text in title:
                    target_index = i
                    break
        
        if target_index == -1:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        # 點擊下載按鈕
        download_btns = page.query_selector_all(".download-btn")
        if target_index >= len(download_btns):
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載按鈕"
            )
        
        # 監聽新視窗
        with page.context.expect_page() as new_page_info:
            download_btns[target_index].click()
        
        new_page = new_page_info.value
        new_page.wait_for_load_state("networkidle")
        pdf_url = new_page.url
        new_page.close()
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
