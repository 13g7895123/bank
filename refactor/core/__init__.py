"""
核心模組

包含下載器和報表生成器的核心邏輯。
"""
from .download_manager import DownloadManager
from .report_manager import ReportManager
from .models import (
    DownloadStatus,
    DownloadResult,
    AssetQualityRow,
    BankInfo,
    ParseResult,
)

__all__ = [
    'DownloadManager',
    'ReportManager',
    'DownloadStatus',
    'DownloadResult',
    'AssetQualityRow',
    'BankInfo',
    'ParseResult',
]
