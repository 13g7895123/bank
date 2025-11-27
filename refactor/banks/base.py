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
    headless: bool = True  # 是否使用無頭模式，部分銀行需要設為 False
    
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
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()
                
                result = self._download(page, year, quarter)
                
                browser.close()
                return result
                
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載錯誤: {str(e)}"
            )
    
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
