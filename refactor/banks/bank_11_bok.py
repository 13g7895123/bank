"""
高雄銀行 (11) - Bank of Kaohsiung
網址: https://www.bok.com.tw/-107
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class BOKDownloader(BaseBankDownloader):
    """高雄銀行下載器"""
    
    bank_name = "高雄銀行"
    bank_code = 11
    bank_url = "https://www.bok.com.tw/-107"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        quarter_chinese = {"第一季": "一", "第二季": "二", "第三季": "三", "第四季": "四"}
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 找下載項目 (第二個通常是資產品質)
        items = page.query_selector_all("li.files-download-item")
        if len(items) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載項目"
            )
        
        # 檢查第二個項目
        item = items[1]
        link = item.query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載連結"
            )
        
        link_text = link.inner_text()
        
        # 解析年度
        try:
            year_on_page = int(link_text.split("年")[0].split()[-1])
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析年度"
            )
        
        # 解析季度
        quarter_on_page = 0
        for q_text, q_char in quarter_chinese.items():
            if f"第{q_char}季" in link_text:
                quarter_on_page = list(quarter_chinese.keys()).index(q_text) + 1
                break
        
        if year_on_page != year or quarter_on_page != quarter:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年{quarter_text} 的資料 (目前: {year_on_page}年第{quarter_on_page}季)"
            )
        
        href = link.get_attribute("href")
        pdf_url = href if href.startswith("http") else f"https://www.bok.com.tw{href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
