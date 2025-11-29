"""
銀行財報自動化系統 - Refactor 版本

主要模組：
- core: 核心邏輯（下載管理器、報表管理器、資料模型）
- banks: 各銀行下載器實作
- utils: 工具函數

使用方式：
    # 方式一：使用核心模組
    from refactor.core import DownloadManager, ReportManager
    
    dm = DownloadManager(data_dir='data')
    result = dm.download('玉山商業銀行', 114, 1)
    
    rm = ReportManager()
    df = rm.generate_report('data/114Q1', 'output/report.xlsx')
    
    # 方式二：使用舊版相容介面
    from refactor.downloader import BankDownloader
    from refactor.report_generator import generate_report
"""

__version__ = "2.0.0"
__author__ = "Bank Report Team"

# 匯出主要類別（延遲載入以避免循環引用）
def get_download_manager():
    from .core.download_manager import DownloadManager
    return DownloadManager

def get_report_manager():
    from .core.report_manager import ReportManager
    return ReportManager
