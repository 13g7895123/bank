"""
下載管理器

統一管理所有銀行財報的下載邏輯。
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Type, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import DownloadStatus, DownloadResult, BankInfo


class DownloadManager:
    """
    下載管理器
    
    負責：
    1. 管理所有銀行下載器的註冊與調用
    2. 提供單一/批次下載功能
    3. 管理下載結果與統計
    
    使用方式:
        manager = DownloadManager(data_dir='data')
        
        # 下載單一銀行
        result = manager.download('玉山商業銀行', 114, 1)
        
        # 下載所有銀行
        results = manager.download_all(114, 1)
    """
    
    # 類別變數：儲存已註冊的下載器
    _downloaders: Dict[str, Type] = {}
    _bank_codes: Dict[int, str] = {}
    _bank_info: Dict[str, BankInfo] = {}
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化下載管理器
        
        Args:
            data_dir: 資料存放目錄
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def register(cls, bank_name: str, bank_code: int, downloader_class: Type):
        """
        註冊銀行下載器
        
        Args:
            bank_name: 銀行名稱
            bank_code: 銀行代碼
            downloader_class: 下載器類別
        """
        cls._downloaders[bank_name] = downloader_class
        cls._bank_codes[bank_code] = bank_name
        cls._bank_info[bank_name] = BankInfo(
            code=bank_code,
            name=bank_name,
            url=getattr(downloader_class, 'bank_url', ''),
        )
    
    @classmethod
    def get_supported_banks(cls) -> List[str]:
        """取得所有支援的銀行名稱"""
        return list(cls._downloaders.keys())
    
    @classmethod
    def get_bank_codes(cls) -> Dict[int, str]:
        """取得銀行代碼對照表"""
        return cls._bank_codes.copy()
    
    @classmethod
    def get_bank_info(cls, bank_name: str) -> Optional[BankInfo]:
        """取得銀行資訊"""
        return cls._bank_info.get(bank_name)
    
    @classmethod
    def get_bank_by_code(cls, code: int) -> Optional[str]:
        """依代碼取得銀行名稱"""
        return cls._bank_codes.get(code)
    
    def get_file_path(self, bank_code: int, bank_name: str, year: int, quarter: int) -> Path:
        """取得檔案路徑"""
        return self.data_dir / f"{year}Q{quarter}" / f"{bank_code}_{bank_name}_{year}Q{quarter}.pdf"
    
    def file_exists(self, bank_code: int, bank_name: str, year: int, quarter: int) -> bool:
        """檢查檔案是否存在"""
        return self.get_file_path(bank_code, bank_name, year, quarter).exists()
    
    def download(self, bank_name: str, year: int, quarter: int) -> DownloadResult:
        """
        下載指定銀行的財報
        
        Args:
            bank_name: 銀行名稱
            year: 民國年
            quarter: 季度 (1-4)
            
        Returns:
            DownloadResult: 下載結果
        """
        # 檢查是否支援
        if bank_name not in self._downloaders:
            return DownloadResult(
                status=DownloadStatus.NOT_SUPPORTED,
                message=f"不支援的銀行: {bank_name}",
                bank_name=bank_name,
                year=year,
                quarter=quarter,
            )
        
        # 取得銀行資訊
        bank_info = self._bank_info.get(bank_name)
        bank_code = bank_info.code if bank_info else 0
        
        # 檢查檔案是否已存在
        file_path = self.get_file_path(bank_code, bank_name, year, quarter)
        if file_path.exists():
            return DownloadResult(
                status=DownloadStatus.ALREADY_EXISTS,
                message="檔案已存在",
                file_path=str(file_path),
                bank_code=bank_code,
                bank_name=bank_name,
                year=year,
                quarter=quarter,
            )
        
        # 建立下載器並執行下載
        try:
            downloader_class = self._downloaders[bank_name]
            downloader = downloader_class(data_dir=str(self.data_dir))
            result = downloader.download(year, quarter)
            
            # 補充銀行資訊
            result.bank_code = bank_code
            result.bank_name = bank_name
            result.year = year
            result.quarter = quarter
            
            return result
            
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載錯誤: {str(e)}",
                bank_code=bank_code,
                bank_name=bank_name,
                year=year,
                quarter=quarter,
            )
    
    def download_by_code(self, bank_code: int, year: int, quarter: int) -> DownloadResult:
        """依銀行代碼下載"""
        bank_name = self._bank_codes.get(bank_code)
        if not bank_name:
            return DownloadResult(
                status=DownloadStatus.NOT_SUPPORTED,
                message=f"不支援的銀行代碼: {bank_code}",
                bank_code=bank_code,
                year=year,
                quarter=quarter,
            )
        return self.download(bank_name, year, quarter)
    
    def download_all(
        self,
        year: int,
        quarter: int,
        progress_callback: Callable[[str, DownloadResult], None] = None,
        max_workers: int = 1,
    ) -> Dict[str, DownloadResult]:
        """
        下載所有銀行的財報
        
        Args:
            year: 民國年
            quarter: 季度 (1-4)
            progress_callback: 進度回調函數 (bank_name, result)
            max_workers: 並行下載數（預設 1，即循序下載）
            
        Returns:
            Dict: 各銀行的下載結果
        """
        results = {}
        banks = list(self._downloaders.keys())
        
        if max_workers <= 1:
            # 循序下載
            for bank_name in banks:
                result = self.download(bank_name, year, quarter)
                results[bank_name] = result
                if progress_callback:
                    progress_callback(bank_name, result)
        else:
            # 並行下載
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.download, bank_name, year, quarter): bank_name
                    for bank_name in banks
                }
                for future in as_completed(futures):
                    bank_name = futures[future]
                    result = future.result()
                    results[bank_name] = result
                    if progress_callback:
                        progress_callback(bank_name, result)
        
        return results
    
    def get_download_summary(self, results: Dict[str, DownloadResult]) -> dict:
        """
        取得下載結果統計摘要
        
        Args:
            results: 下載結果字典
            
        Returns:
            統計摘要
        """
        summary = {
            'total': len(results),
            'success': 0,
            'already_exists': 0,
            'no_data': 0,
            'error': 0,
            'not_supported': 0,
            'failed_banks': [],
        }
        
        for bank_name, result in results.items():
            if result.status == DownloadStatus.SUCCESS:
                summary['success'] += 1
            elif result.status == DownloadStatus.ALREADY_EXISTS:
                summary['already_exists'] += 1
            elif result.status == DownloadStatus.NO_DATA:
                summary['no_data'] += 1
                summary['failed_banks'].append({'name': bank_name, 'reason': result.message})
            elif result.status == DownloadStatus.NOT_SUPPORTED:
                summary['not_supported'] += 1
            else:
                summary['error'] += 1
                summary['failed_banks'].append({'name': bank_name, 'reason': result.message})
        
        return summary
