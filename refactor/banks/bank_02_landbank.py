"""
臺灣土地銀行 (2) - Land Bank of Taiwan
網址: https://www.landbank.com.tw/Category/Items/財務業務資訊-財報
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class LandBankDownloader(BaseBankDownloader):
    """臺灣土地銀行下載器"""
    
    bank_name = "臺灣土地銀行"
    bank_code = 2
    bank_url = "https://www.landbank.com.tw/Category/Items/%E8%B2%A1%E5%8B%99%E6%A5%AD%E5%8B%99%E8%B3%87%E8%A8%8A-%E8%B2%A1%E5%A0%B1"
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財務業務資訊頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)  # 等待頁面完全載入
        
        # 步驟1: 點擊「銀行重要財務業務資訊」展開按鈕
        expand_btn = page.locator('[aria-label="按下後展開資訊"][title="銀行重要財務業務資訊"]')
        
        if expand_btn.count() == 0:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="找不到「銀行重要財務業務資訊」展開按鈕"
            )
        
        # 點擊展開
        expand_btn.click()
        page.wait_for_timeout(1000)  # 等待展開動畫
        
        # 步驟2: 在 tbody 中找到指定年度的 tr
        # 表格結構: tbody > tr > th(年度) + td > a(季度連結)
        year_str = f"{year}年度"
        
        # 找到 th 包含指定年度的 tr
        target_row = page.locator(f'tbody tr:has(th:text("{year_str}"))')
        
        if target_row.count() == 0:
            # 嘗試其他年度格式
            target_row = page.locator(f'tbody tr:has(th:text("{year}年"))')
        
        if target_row.count() == 0:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year} 年度的資料列"
            )
        
        # 步驟3: 在該 tr 中找到對應季度的連結
        # 季度對應: 1=第一季, 2=第二季, 3=第三季, 4=全年度
        quarter_mapping = {
            1: "第一季",
            2: "第二季", 
            3: "第三季",
            4: "全年度"
        }
        
        quarter_name = quarter_mapping.get(quarter, f"第{quarter}季")
        
        # 找該列中包含季度文字的 a 連結
        quarter_link = target_row.locator(f'td a:has-text("{quarter_name}")')
        
        if quarter_link.count() == 0:
            # 嘗試用 td 的順序來找（第1個td=第一季, 第2個=第二季...）
            tds = target_row.locator('td')
            td_count = tds.count()
            
            if td_count >= quarter:
                # 取得對應的 td（索引從 0 開始）
                target_td = tds.nth(quarter - 1)
                quarter_link = target_td.locator('a')
            
            if quarter_link.count() == 0:
                return DownloadResult(
                    status=DownloadStatus.NO_DATA,
                    message=f"找不到 {year}年{quarter_name} 的下載連結"
                )
        
        # 取得 PDF URL
        href = quarter_link.first.get_attribute("href")
        
        if not href:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message="無法取得 PDF 連結"
            )
        
        # 組合完整 URL
        if not href.startswith("http"):
            pdf_url = f"https://www.landbank.com.tw{href}"
        else:
            pdf_url = href
        
        return self.download_pdf_from_url(page, pdf_url, year, quarter)
