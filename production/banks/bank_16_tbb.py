"""
臺灣中小企業銀行 (16) - Taiwan Business Bank
網址: https://ir.tbb.com.tw/financial/quarterly-results
"""
import subprocess
import os
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.async_api import Page


class TBBDownloader(BaseBankDownloader):
    """臺灣中小企業銀行下載器"""
    
    bank_name = "臺灣中小企業銀行"
    bank_code = 16
    bank_url = "https://ir.tbb.com.tw/financial/quarterly-results"
    
    async def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 民國年轉西元年
        western_year = year + 1911
        
        # 前往財報頁面
        await page.goto(self.bank_url)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 點選年份 (href="?y=2025" 的 a tag)
        year_link = page.locator(f'a[href="?y={western_year}"]')
        if await year_link.count() > 0:
            await year_link.first.click()
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)
        
        # 建立搜尋的報告名稱
        # 格式: "2025年第一季合併財務報告" 或 "2024年度合併財務報告" (第四季)
        quarter_names = {
            1: "第一季",
            2: "第二季",
            3: "第三季"
        }
        
        if quarter == 4:
            # 第四季為年度報告
            search_text = f"{western_year}年度合併財務報告"
        else:
            search_text = f"{western_year}年{quarter_names[quarter]}合併財務報告"
        
        # 在 ul li 結構中找到對應的 p 元素
        # 找到包含目標文字的 li 元素，然後取得同層的 a.download 連結
        pdf_url = None
        
        # 找所有的 li 元素
        li_elements = await page.locator("ul li").all()
        
        for li in li_elements:
            # 檢查 li 底下的 p 元素是否包含目標文字
            p_element = li.locator("p")
            if await p_element.count() > 0:
                p_text = (await p_element.first.inner_text()).strip()
                if search_text in p_text:
                    # 找到目標 li，取得 a.download 的 href
                    download_link = li.locator("a.download")
                    if await download_link.count() > 0:
                        href = await download_link.first.get_attribute("href")
                        if href:
                            # 組合完整 URL
                            if href.startswith("http"):
                                pdf_url = href
                            else:
                                pdf_url = f"https://ir.tbb.com.tw{href}"
                            break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} ({search_text}) 的下載連結"
            )
        
        # 使用 wget 下載 (類似華南銀行的方式)
        try:
            self.ensure_dir(year, quarter)
            file_path = self.get_file_path(year, quarter)
            
            # 使用 wget 下載，--no-check-certificate 跳過 SSL 驗證
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
                return DownloadResult(
                    status=DownloadStatus.ERROR,
                    message=f"wget 下載失敗: {result.stderr}"
                )
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載失敗: {str(e)}"
            )
