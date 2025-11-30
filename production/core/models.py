"""
資料模型定義

定義系統中使用的所有資料結構。
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class DownloadStatus(Enum):
    """下載狀態列舉"""
    SUCCESS = "success"              # 下載成功
    ALREADY_EXISTS = "already_exists"  # 檔案已存在
    NO_DATA = "no_data"              # 該季度尚無資料
    ERROR = "error"                  # 下載錯誤
    NOT_SUPPORTED = "not_supported"  # 不支援的銀行


class ParseStatus(Enum):
    """解析狀態列舉"""
    SUCCESS = "success"              # 解析成功
    PARTIAL = "partial"              # 部分解析（缺少某些類別）
    FAILED = "failed"                # 解析失敗
    NO_FILE = "no_file"              # 檔案不存在


@dataclass
class BankInfo:
    """銀行基本資訊"""
    code: int                        # 銀行代碼
    name: str                        # 銀行名稱
    short_name: str = ""             # 簡稱
    url: str = ""                    # 財報網址
    notes: str = ""                  # 備註（如：政策性銀行）
    
    def __post_init__(self):
        if not self.short_name:
            self.short_name = self.name


@dataclass
class DownloadResult:
    """下載結果"""
    status: DownloadStatus
    message: str = ""
    file_path: str = ""
    bank_code: int = 0
    bank_name: str = ""
    year: int = 0
    quarter: int = 0
    
    @property
    def is_success(self) -> bool:
        """是否成功（包含已存在）"""
        return self.status in [DownloadStatus.SUCCESS, DownloadStatus.ALREADY_EXISTS]
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            'status': self.status.value,
            'message': self.message,
            'file_path': self.file_path,
            'bank_code': self.bank_code,
            'bank_name': self.bank_name,
            'year': self.year,
            'quarter': self.quarter,
        }


@dataclass
class AssetQualityRow:
    """資產品質資料列"""
    year: str                        # 資料年度（民國年）
    quarter: str                     # 季度（如 Q1）
    subject: str                     # 業務別項目
    overdue_amount: float            # 逾期放款金額（仟元）
    total_loan: float                # 放款總額（仟元）
    overdue_ratio: float             # 逾放比率（%）
    bank_name: str                   # 銀行名稱
    bank_code: int = 0               # 銀行代碼
    
    def to_dict(self) -> dict:
        """轉換為字典"""
        return {
            '資料年度': self.year,
            '季度': self.quarter,
            '業務別項目': self.subject,
            '逾期放款金額(單位：仟元)': self.overdue_amount,
            '放款總額(單位：仟元)': self.total_loan,
            '逾放比率': self.overdue_ratio,
            '銀行名稱': self.bank_name,
        }


@dataclass
class ParseResult:
    """解析結果"""
    status: ParseStatus
    rows: List[AssetQualityRow] = field(default_factory=list)
    message: str = ""
    bank_name: str = ""
    file_path: str = ""
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == ParseStatus.SUCCESS
    
    @property
    def category_count(self) -> int:
        """已解析的類別數量"""
        return len(self.rows)
    
    @property
    def is_complete(self) -> bool:
        """是否完整（8 個類別）"""
        return self.category_count == 8


# 8 個業務別項目
SUBJECT_CATEGORIES = [
    "01_企業金融_擔保",
    "02_企業金融_無擔保",
    "03_消費金融_住宅抵押貸款",
    "04_消費金融_現金卡",
    "05_消費金融_小額純信用貸款",
    "06_消費金融_其他_擔保",
    "07_消費金融_其他_無擔保",
    "08_合計",
]

# 業務別項目對應表（內部名稱 -> 輸出名稱）
SUBJECT_MAPPING = {
    "企業金融_擔保": "01_企業金融_擔保",
    "企業金融_無擔保": "02_企業金融_無擔保",
    "消費金融_住宅抵押貸款": "03_消費金融_住宅抵押貸款",
    "消費金融_現金卡": "04_消費金融_現金卡",
    "消費金融_小額純信用貸款": "05_消費金融_小額純信用貸款",
    "消費金融_其他_擔保": "06_消費金融_其他_擔保",
    "消費金融_其他_無擔保": "07_消費金融_其他_無擔保",
    "合計": "08_合計",
}
