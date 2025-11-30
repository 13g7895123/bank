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
    ParseStatus,
)

# OCR 解析器（可選）
try:
    from .ocr_parser import OCRParser, is_scanned_pdf
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    OCRParser = None
    is_scanned_pdf = None

__all__ = [
    'DownloadManager',
    'ReportManager',
    'DownloadStatus',
    'DownloadResult',
    'AssetQualityRow',
    'BankInfo',
    'ParseResult',
    'ParseStatus',
    'OCRParser',
    'is_scanned_pdf',
    'HAS_OCR',
]
