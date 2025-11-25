"""
上海商業儲蓄銀行 (7) - Shanghai Commercial & Savings Bank
網址: https://www.scsb.com.tw/content/about/about04_a_01.jsp
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class SCSBDownloader(BaseBankDownloader):
    """上海商業儲蓄銀行下載器"""
    
    bank_name = "上海商業儲蓄銀行"
    bank_code = 7
    bank_url = "https://www.scsb.com.tw/content/about/about04_a_01.jsp"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        
        # 找標題確認年度
        title_div = page.query_selector("div.titleBlk_a.h4")
        if not title_div:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到標題"
            )
        
        title_text = title_div.inner_text()
        try:
            year_on_page = int(title_text.split("年")[0])
        except:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法解析年度"
            )
        
        if year_on_page != year:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年 的資料 (目前: {year_on_page}年)"
            )
        
        # 尋找對應季度的連結
        target_title = f"開新視窗({quarter_text})法定財務業務資訊(PDF)"
        link = page.query_selector(f'a[title="{target_title}"]')
        
        if not link:
            # 嘗試其他格式
            links = page.query_selector_all("div.list-group.downloadLister a")
            for l in links:
                title = l.get_attribute("title") or l.inner_text()
                if quarter_text in title:
                    link = l
                    break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {quarter_text} 的資料"
            )
        
        href = link.get_attribute("href")
        if not href.startswith("http"):
            pdf_url = f"https://www.scsb.com.tw/content/about/{href}"
        else:
            pdf_url = href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
