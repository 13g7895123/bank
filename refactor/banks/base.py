"""
銀行財報下載基礎類別
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from playwright.sync_api import sync_playwright, Page, Browser


class DownloadStatus(Enum):
    """下載狀態"""
    SUCCESS = 1
    ALREADY_EXISTS = 2
    NO_DATA = -1
    ERROR = -2


@dataclass
class DownloadResult:
    """下載結果"""
    status: DownloadStatus
    message: str = ""
    file_path: str = ""


class BaseBankDownloader(ABC):
    """銀行下載器基礎類別"""
    
    # 子類別需要覆寫這些屬性
    bank_name: str = ""
    bank_code: int = 0
    bank_url: str = ""
    headless: bool = True  # 是否使用無頭模式，預設為 True
    force_headless: bool = False  # 強制使用無頭模式（不自動重試有頭模式）
    retry_with_head: bool = True  # 無頭模式失敗時是否自動重試有頭模式
    browser_type: str = "chromium"  # 瀏覽器類型: chromium, firefox, webkit
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        
    def get_quarter_text(self, quarter: int) -> str:
        """取得季度文字"""
        quarter_map = {1: "第一季", 2: "第二季", 3: "第三季", 4: "第四季"}
        return quarter_map.get(quarter, "")
    
    def get_file_path(self, year: int, quarter: int) -> str:
        """取得檔案路徑"""
        return f"{self.data_dir}/{year}Q{quarter}/{self.bank_code}_{self.bank_name}_{year}Q{quarter}.pdf"
    
    def ensure_dir(self, year: int, quarter: int) -> str:
        """確保資料夾存在"""
        dir_path = f"{self.data_dir}/{year}Q{quarter}"
        os.makedirs(dir_path, exist_ok=True)
        return dir_path
    
    def file_exists(self, year: int, quarter: int) -> bool:
        """檢查檔案是否已存在"""
        return os.path.isfile(self.get_file_path(year, quarter))
    
    def save_pdf(self, content: bytes, year: int, quarter: int) -> str:
        """儲存 PDF 檔案"""
        self.ensure_dir(year, quarter)
        file_path = self.get_file_path(year, quarter)
        with open(file_path, 'wb') as f:
            f.write(content)
        return file_path
    
    def _get_browser(self, playwright):
        """根據 browser_type 取得對應的瀏覽器"""
        if self.browser_type == "firefox":
            return playwright.firefox
        elif self.browser_type == "webkit":
            return playwright.webkit
        else:
            return playwright.chromium
    
    def _get_user_agent(self) -> str:
        """根據瀏覽器類型取得對應的 User-Agent"""
        if self.browser_type == "firefox":
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        else:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def download(self, year: int, quarter: int) -> DownloadResult:
        """
        下載財報
        
        Args:
            year: 民國年
            quarter: 季度 (1-4)
            
        Returns:
            DownloadResult: 下載結果
        """
        # 檢查檔案是否已存在
        if self.file_exists(year, quarter):
            return DownloadResult(
                status=DownloadStatus.ALREADY_EXISTS,
                message="檔案已存在",
                file_path=self.get_file_path(year, quarter)
            )
        
        # 第一次嘗試：使用預設的 headless 設定
        result = self._try_download(year, quarter, headless=self.headless)
        
        # 驗證下載結果
        if self._is_download_successful(result, year, quarter):
            return result
        
        # 如果無頭模式失敗且允許重試有頭模式
        if self.headless and self.retry_with_head and not self.force_headless:
            # 清理可能產生的不完整檔案
            self._cleanup_failed_download(year, quarter)
            
            # 第二次嘗試：使用有頭模式
            result = self._try_download(year, quarter, headless=False)
            
            # 再次驗證
            if self._is_download_successful(result, year, quarter):
                result.message = f"{result.message} (使用有頭模式)"
                return result
        
        return result
    
    def _try_download(self, year: int, quarter: int, headless: bool) -> DownloadResult:
        """嘗試下載（內部方法）"""
        try:
            with sync_playwright() as p:
                browser_launcher = self._get_browser(p)
                browser = browser_launcher.launch(headless=headless)
                context = browser.new_context(
                    user_agent=self._get_user_agent(),
                    viewport={"width": 1920, "height": 1080}
                )
                page = context.new_page()
                page.set_default_timeout(60000)  # 60 秒超時
                page.set_default_navigation_timeout(60000)
                
                result = self._download(page, year, quarter)
                
                browser.close()
                return result
                
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載錯誤: {str(e)}"
            )
    
    def _is_download_successful(self, result: DownloadResult, year: int, quarter: int) -> bool:
        """驗證下載是否成功"""
        # 狀態不是成功，直接返回 False
        if result.status != DownloadStatus.SUCCESS:
            return False
        
        # 檢查檔案是否存在
        file_path = result.file_path or self.get_file_path(year, quarter)
        if not os.path.isfile(file_path):
            return False
        
        # 檢查檔案大小（PDF 至少應該有幾 KB）
        file_size = os.path.getsize(file_path)
        if file_size < 1024:  # 小於 1KB 可能是錯誤頁面
            return False
        
        # 檢查檔案頭是否為 PDF 格式
        try:
            with open(file_path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF'):
                    return False
        except Exception:
            return False
        
        return True
    
    def _cleanup_failed_download(self, year: int, quarter: int):
        """清理失敗的下載檔案"""
        file_path = self.get_file_path(year, quarter)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
    
    @abstractmethod
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        """
        實際下載邏輯，子類別需實作
        
        Args:
            page: Playwright Page 物件
            year: 民國年
            quarter: 季度
            
        Returns:
            DownloadResult: 下載結果
        """
        pass
    
    def download_pdf_from_url(self, page: Page, url: str, year: int, quarter: int) -> DownloadResult:
        """從 URL 下載 PDF"""
        try:
            response = page.request.get(url)
            
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                if 'pdf' in content_type.lower() or url.endswith('.pdf'):
                    file_path = self.save_pdf(response.body(), year, quarter)
                    return DownloadResult(
                        status=DownloadStatus.SUCCESS,
                        message="下載成功",
                        file_path=file_path
                    )
                else:
                    return DownloadResult(
                        status=DownloadStatus.ERROR,
                        message=f"非 PDF 格式: {content_type}"
                    )
            else:
                return DownloadResult(
                    status=DownloadStatus.NO_DATA,
                    message=f"HTTP {response.status}"
                )
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載失敗: {str(e)}"
            )
    
    def download_pdf_by_click(self, page: Page, locator, year: int, quarter: int) -> DownloadResult:
        """透過點擊連結下載 PDF（適用於需要 JavaScript 處理的下載連結）"""
        try:
            # 確保目錄存在
            self.ensure_dir(year, quarter)
            file_path = self.get_file_path(year, quarter)
            
            # 啟動下載監聽
            with page.expect_download(timeout=30000) as download_info:
                locator.click()
            
            download = download_info.value
            
            # 儲存檔案
            download.save_as(file_path)
            
            return DownloadResult(
                status=DownloadStatus.SUCCESS,
                message="下載成功",
                file_path=file_path
            )
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"點擊下載失敗: {str(e)}"
            )
