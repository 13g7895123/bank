"""
玉山商業銀行 (31) - E.SUN Commercial Bank
網址: https://doc.twse.com.tw/server-java/t57sb01
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class ESunBankDownloader(BaseBankDownloader):
    """玉山商業銀行下載器"""
    
    bank_name = "玉山商業銀行"
    bank_code = 31
    bank_url = "https://doc.twse.com.tw/server-java/t57sb01"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往搜尋頁面
        search_url = f"{self.bank_url}?step=1&colorchg=1&co_id=5847&year={year}&seamon=&mtype=A&"
        page.goto(search_url)
        page.wait_for_load_state("networkidle")
        
        # 檢查是否有結果
        form = page.query_selector("form")
        if not form:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年 的資料"
            )
        
        # 找表格
        tbodies = page.query_selector_all("tbody")
        if len(tbodies) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料表格"
            )
        
        rows = tbodies[1].query_selector_all("tr")
        
        file_name = None
        for row in rows[1:]:  # 跳過標題列
            tds = row.query_selector_all("td")
            if len(tds) >= 8:
                text_quarter = tds[1].inner_text()
                report_type = tds[5].inner_text()
                
                # 根據季度選擇合併或個體財報
                if quarter % 2 == 1:
                    if quarter_text in text_quarter and report_type == "IFRSs合併財報":
                        file_name = tds[7].inner_text()
                        break
                else:
                    if quarter_text in text_quarter and report_type == "IFRSs個體財報":
                        file_name = tds[7].inner_text()
                        break
        
        if not file_name:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        # 取得下載頁面
        download_page_url = f"{self.bank_url}?step=9&colorchg=1&kind=A&co_id=5847&filename={file_name}"
        page.goto(download_page_url)
        page.wait_for_load_state("networkidle")
        
        # 取得實際 PDF 連結
        pdf_link = page.query_selector("a")
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        pdf_url = pdf_href if pdf_href.startswith("http") else f"https://doc.twse.com.tw{pdf_href}"
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
