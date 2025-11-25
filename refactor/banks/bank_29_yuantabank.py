"""
元大商業銀行 (29) - Yuanta Commercial Bank
網址: https://www.yuantabank.com.tw/bank/bulletin/statutoryDisclosure/list.do
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class YuantaBankDownloader(BaseBankDownloader):
    """元大商業銀行下載器"""
    
    bank_name = "元大商業銀行"
    bank_code = 29
    bank_url = "https://www.yuantabank.com.tw/bank/bulletin/statutoryDisclosure/list.do"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 根據季度選擇不同頁面
        if quarter % 2 == 0:
            url = f"{self.bank_url}?layer_id=26a83777c500000745d9"
            search_text = "上半年" if quarter == 2 else "年度個體"
        else:
            url = f"{self.bank_url}?layer_id=26a836f2b60000019f0b"
            search_text = quarter_text
        
        # 前往財報頁面
        page.goto(url)
        page.wait_for_load_state("networkidle")
        
        # 找新聞列表
        news_div = page.query_selector("div.news")
        if not news_div:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料區塊"
            )
        
        items = news_div.query_selector_all("li")
        
        pdf_url = None
        for item in items[:4]:  # 只檢查前4個
            link = item.query_selector("a")
            if link:
                link_text = link.inner_text()
                if str(year) in link_text and search_text in link_text:
                    pdf_href = link.get_attribute("href")
                    pdf_url = pdf_href if pdf_href.startswith("http") else f"https://www.yuantabank.com.tw{pdf_href}"
                    break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
