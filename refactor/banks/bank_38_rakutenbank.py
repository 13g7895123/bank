"""
樂天國際商業銀行 (38) - Rakuten Bank
網址: https://www.rakuten-bank.com.tw/portal/other/disclosure

財務資訊頁籤 > 重要財務業務資訊

特點：
1. 網站有 Incapsula 防護，需使用 Firefox 瀏覽器繞過
2. 使用 GraphQL API 獲取財務資訊資料
3. GraphQL API 返回的 PDF URL 格式為 cmspv.rakuten-bank.com.tw:9443/file/xxx.pdf
   但實際可下載的 URL 是 www.rakuten-bank.com.tw/cms-upload/file/xxx.pdf
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page, BrowserContext
import json
import re


class RakutenBankDownloader(BaseBankDownloader):
    """樂天國際商業銀行下載器"""
    
    bank_name = "樂天國際商業銀行"
    bank_code = 38
    bank_url = "https://www.rakuten-bank.com.tw/portal/other/disclosure"
    
    # 樂天銀行需要使用 Firefox 繞過 Incapsula 防護
    browser_type = "firefox"
    
    def _convert_pdf_url(self, api_url: str) -> str:
        """
        將 GraphQL API 返回的 PDF URL 轉換為實際可下載的 URL
        
        API 返回格式: https://cmspv.rakuten-bank.com.tw:9443/file/xxx.pdf
        實際下載格式: https://www.rakuten-bank.com.tw/cms-upload/file/xxx.pdf
        """
        if "cmspv.rakuten-bank.com.tw:9443" in api_url:
            return api_url.replace(
                "https://cmspv.rakuten-bank.com.tw:9443",
                "https://www.rakuten-bank.com.tw/cms-upload"
            )
        return api_url
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 搜尋文字格式: "114年第三季重要財務業務資訊"
        search_title = f"{year}年{quarter_text}重要財務業務資訊"
        
        # 先嘗試透過 GraphQL API 獲取 PDF URL
        pdf_url = self._get_pdf_url_from_api(page, year, quarter_text)
        
        if pdf_url:
            # 轉換 URL 為實際可下載格式
            download_url = self._convert_pdf_url(pdf_url)
            return self._download_pdf(page, download_url, year, quarter)
        
        # 如果 API 失敗，使用網頁動態抓取
        return self._download_from_webpage(page, year, quarter, search_title)
    
    def _get_pdf_url_from_api(self, page: Page, year: int, quarter_text: str) -> str:
        """透過 GraphQL API 獲取 PDF URL"""
        
        # 先訪問頁面取得必要的 cookie
        page.goto(self.bank_url, timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        graphql_url = "https://www.rakuten-bank.com.tw/graphql"
        query = """query ddisclosurecat($categoryId: JSON) {
          ddisclosurecats(where: $categoryId) {
            ddisclosures(sort: "order:asc") {
              id
              title
              description
              file {
                url
                __typename
              }
              __typename
            }
            __typename
          }
        }"""
        
        variables = {"categoryId": {"categoryId": "finance"}}
        
        try:
            response = page.request.post(
                graphql_url,
                data={
                    "operationName": "ddisclosurecat",
                    "variables": json.dumps(variables),
                    "query": query
                }
            )
            
            if not response.ok:
                return None
            
            data = response.json()
            disclosures = data.get("data", {}).get("ddisclosurecats", [{}])[0].get("ddisclosures", [])
            
            # 搜尋目標季度的報告
            search_title = f"{year}年{quarter_text}重要財務業務資訊"
            
            for item in disclosures:
                title = item.get("title", "")
                if title == search_title:
                    file_info = item.get("file", {})
                    pdf_url = file_info.get("url")
                    if pdf_url:
                        return pdf_url
            
            return None
            
        except Exception as e:
            return None
    
    def _download_from_webpage(self, page: Page, year: int, quarter: int, 
                                search_title: str) -> DownloadResult:
        """從網頁動態抓取財務報告連結 (備用方案)"""
        quarter_text = self.get_quarter_text(quarter)
        
        # 前往財報頁面
        page.goto(self.bank_url, timeout=60000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 點擊財務資訊 tab
        finance_tab = page.locator('text=財務資訊').first
        if finance_tab:
            finance_tab.click()
            page.wait_for_timeout(2000)
        
        # 找到目標季度的下載按鈕
        q_head = page.locator(f'div.collapse-block-head:has(div:has-text("{search_title}"))').first
        
        if not q_head:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} 的資料"
            )
        
        download_btn = q_head.locator('a.download-btn').first
        
        if not download_btn:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message="找不到下載按鈕"
            )
        
        try:
            # 使用 expect_download 捕獲下載
            with page.expect_download(timeout=30000) as download_info:
                download_btn.click()
            
            download = download_info.value
            
            # 儲存 PDF
            file_path = self.get_file_path(year, quarter)
            self.ensure_dir(year, quarter)
            download.save_as(file_path)
            
            return DownloadResult(
                status=DownloadStatus.SUCCESS,
                message="下載成功 (網頁方式)",
                file_path=file_path
            )
            
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載失敗: {str(e)}"
            )
    
    def _download_pdf(self, page: Page, pdf_url: str, year: int, quarter: int) -> DownloadResult:
        """下載 PDF 檔案"""
        try:
            response = page.request.get(pdf_url)
            
            if not response.ok:
                return DownloadResult(
                    status=DownloadStatus.ERROR,
                    message=f"下載失敗: HTTP {response.status}"
                )
            
            content = response.body()
            
            # 驗證是否為 PDF
            if not content.startswith(b'%PDF'):
                return DownloadResult(
                    status=DownloadStatus.ERROR,
                    message="下載的檔案不是有效的 PDF"
                )
            
            # 儲存 PDF
            file_path = self.save_pdf(content, year, quarter)
            
            return DownloadResult(
                status=DownloadStatus.SUCCESS,
                message="下載成功",
                file_path=file_path
            )
            
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載失敗: {str(e)}"
            )
