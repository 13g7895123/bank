"""
兆豐國際商業銀行 (12) - Mega International Commercial Bank
網址: https://www.megabank.com.tw/about/announcement/news/regulatory-disclosures/finance-report
"""
import subprocess
import os
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class MegaBankDownloader(BaseBankDownloader):
    """兆豐國際商業銀行下載器"""
    
    bank_name = "兆豐國際商業銀行"
    bank_code = 12
    bank_url = "https://www.megabank.com.tw/about/announcement/news/regulatory-disclosures/finance-report"
    headless = False  # 可能需要有頭模式
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 步驟1: 找到季度連結並點擊
        # 格式: "前往114年度第一季重要財務業務資訊"
        search_keywords = [
            f"前往{year}年度{quarter_text}重要財務業務資訊",
        ]
        
        # Q4 額外嘗試「全年度」
        if quarter == 4:
            search_keywords.extend([
                f"前往{year}年度全年度重要財務業務資訊",
                f"前往{year}年度年報重要財務業務資訊",
            ])
        
        # 嘗試各種關鍵字找連結
        link = None
        for keyword in search_keywords:
            locator = page.locator(f'a[title="{keyword}"]')
            if locator.count() > 0:
                link = locator.first
                break
        
        if not link:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的下載連結"
            )
        
        # 點擊進入子頁面
        link.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 步驟2: 找「資產品質」的連結並點擊
        # 格式: title="下載pdf檔案 資產品質 另開新視窗"
        asset_link = page.locator('a[title="下載pdf檔案 資產品質 另開新視窗"]')
        
        if asset_link.count() == 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到資產品質連結"
            )
        
        # 點擊進入 PDF 頁面
        asset_link.first.click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 步驟3: 取得 PDF URL（當前頁面應該就是 PDF 或有 PDF 連結）
        current_url = page.url
        
        # 如果當前 URL 就是 PDF
        if current_url.endswith('.pdf'):
            pdf_url = current_url
        else:
            # 找頁面中的 PDF 連結
            pdf_link = page.locator('a[href*=".pdf"]').first
            if pdf_link.count() == 0:
                # 嘗試找 embed 或 iframe 中的 PDF
                embed = page.locator('embed[src*=".pdf"], iframe[src*=".pdf"]').first
                if embed.count() > 0:
                    pdf_url = embed.get_attribute("src")
                else:
                    return DownloadResult(
                        status=DownloadStatus.NO_DATA,
                        message="找不到 PDF 連結"
                    )
            else:
                pdf_url = pdf_link.get_attribute("href")
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        # 組合完整 URL
        if not pdf_url.startswith("http"):
            pdf_url = f"https://www.megabank.com.tw{pdf_url}"
        
        # 使用 wget 下載
        try:
            self.ensure_dir(year, quarter)
            file_path = self.get_file_path(year, quarter)
            
            result = subprocess.run(
                ['wget', '--no-check-certificate', '-q', '-O', file_path, pdf_url],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return DownloadResult(
                    status=DownloadStatus.SUCCESS,
                    message="下載成功",
                    file_path=file_path
                )
            else:
                # 嘗試用 Playwright 下載
                return self.download_pdf_from_url(page, pdf_url, year, quarter)
        except Exception as e:
            # 嘗試用 Playwright 下載
            return self.download_pdf_from_url(page, pdf_url, year, quarter)
