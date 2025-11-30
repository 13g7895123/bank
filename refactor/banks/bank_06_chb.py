"""
彰化商業銀行 (6) - Chang Hwa Commercial Bank
網址: https://www.bankchb.com/frontend/finance.jsp

網頁結構：
- 資料列表在 ul.ul-itemss 中
- 連結格式: "民國114年第一季" 或 "民國113年度"（Q4 為年度）
- 點擊後進入詳細頁面，再找 PDF 連結
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class CHBDownloader(BaseBankDownloader):
    """彰化商業銀行下載器"""
    
    bank_name = "彰化商業銀行"
    bank_code = 6
    bank_url = "https://www.bankchb.com/frontend/finance.jsp"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 建立搜尋關鍵字
        # Q4 對應「年度」，其他季度對應「第X季」
        if quarter == 4:
            search_patterns = [
                f"民國{year}年度",
                f"民國{year}年第四季",
                f"民國{year}年第4季",
            ]
        else:
            search_patterns = [
                f"民國{year}年{quarter_text}",
                f"民國{year}年第{quarter}季",
            ]
        
        # 在連結列表中搜尋
        links = page.locator('ul.ul-itemss a')
        target_link = None
        
        for i in range(links.count()):
            link_text = links.nth(i).inner_text().strip()
            for pattern in search_patterns:
                if pattern in link_text:
                    target_link = links.nth(i)
                    break
            if target_link:
                break
        
        if not target_link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        # 點擊連結進入子頁面
        href = target_link.get_attribute("href")
        page.goto(f"https://www.bankchb.com/frontend/{href}")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        
        # 找 PDF 連結（法定財務業務資訊）
        pdf_link = page.locator('a.editor_link:has-text("法定財務業務資訊")')
        if pdf_link.count() == 0:
            # 嘗試找任何 PDF 連結
            pdf_link = page.locator('a.editor_link')
        
        if pdf_link.count() == 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到 PDF 連結"
            )
        
        pdf_href = pdf_link.first.get_attribute("href")
        if not pdf_href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        if not pdf_href.startswith("http"):
            pdf_url = f"https://www.bankchb.com{pdf_href}"
        else:
            pdf_url = pdf_href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
