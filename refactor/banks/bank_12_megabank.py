"""
兆豐國際商業銀行 (12) - Mega International Commercial Bank
網址: https://www.megabank.com.tw/about/announcement/legal-disclosure/finance-report
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class MegaBankDownloader(BaseBankDownloader):
    """兆豐國際商業銀行下載器"""
    
    bank_name = "兆豐國際商業銀行"
    bank_code = 12
    bank_url = "https://www.megabank.com.tw/about/announcement/legal-disclosure/finance-report"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        target_text = f"{year}年度{quarter_text}"
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 找表格第二列 (第一列通常是標題)
        rows = page.query_selector_all("tbody tr")
        if len(rows) < 2:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資料列"
            )
        
        target_row = rows[1]
        link = target_row.query_selector("a")
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到連結"
            )
        
        title = link.get_attribute("title") or link.inner_text()
        
        if target_text not in title:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"尚無 {year}年度{quarter_text} 的資料"
            )
        
        # 取得子頁面連結
        href = link.get_attribute("href")
        sub_url = f"https://www.megabank.com.tw{href}" if not href.startswith("http") else href
        
        # 訪問子頁面取得 PDF
        page.goto(sub_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 找 PDF 連結 (通常在第三個表格的第二個 td)
        tables = page.query_selector_all("table.borderall")
        if len(tables) < 3:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 PDF 表格"
            )
        
        pdf_link = tables[2].query_selector("td:nth-child(2) a")
        if not pdf_link:
            # 嘗試其他方式
            pdf_link = tables[2].query_selector("a")
        
        if not pdf_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 PDF 連結"
            )
        
        pdf_href = pdf_link.get_attribute("href")
        pdf_url = f"https://www.megabank.com.tw{pdf_href}" if not pdf_href.startswith("http") else pdf_href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
