"""
銀行財報下載器主模組
使用 Playwright 進行網頁自動化
"""
import os
import sys
from pathlib import Path
from typing import Dict, Type, Optional
from dataclasses import dataclass

# 確保可以導入 banks 子模組
_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

from banks.base import BaseBankDownloader, DownloadResult, DownloadStatus

# 導入所有銀行下載器
from banks.bank_01_bot import BOTDownloader
from banks.bank_02_landbank import LandBankDownloader
from banks.bank_03_tcb import TCBBankDownloader
from banks.bank_04_firstbank import FirstBankDownloader
from banks.bank_05_hncb import HNCBDownloader
from banks.bank_06_chb import CHBDownloader
from banks.bank_07_scsb import SCSBDownloader
from banks.bank_08_fubon import FubonDownloader
from banks.bank_09_cathay import CathayDownloader
from banks.bank_10_eximbank import EximBankDownloader
from banks.bank_11_bok import BOKDownloader
from banks.bank_12_megabank import MegaBankDownloader
from banks.bank_13_citibank import CitibankDownloader
from banks.bank_15_obank import OBankDownloader
from banks.bank_16_tbb import TBBDownloader
from banks.bank_17_scb import SCBDownloader
from banks.bank_18_taichungbank import TaichungBankDownloader
from banks.bank_19_ktb import KTBDownloader
from banks.bank_20_hsbc import HSBCDownloader
from banks.bank_21_taipeistarbank import TaipeiStarBankDownloader
from banks.bank_22_hwataibank import HwataiBankDownloader
from banks.bank_23_skbank import SKBankDownloader
from banks.bank_24_sunnybank import SunnyBankDownloader
from banks.bank_25_bop import BOPDownloader
from banks.bank_26_cotabank import CotaBankDownloader
from banks.bank_27_ubot import UBOTDownloader
from banks.bank_28_feib import FEIBDownloader
from banks.bank_29_yuantabank import YuantaBankDownloader
from banks.bank_30_sinopac import SinoPacDownloader
from banks.bank_31_esunbank import ESunBankDownloader
from banks.bank_32_kgibank import KGIBankDownloader
from banks.bank_33_dbs import DBSBankDownloader
from banks.bank_34_taishinbank import TaishinBankDownloader
from banks.bank_36_entiebank import EntieBankDownloader
from banks.bank_37_ctbc import CTBCBankDownloader
from banks.bank_38_rakutenbank import RakutenBankDownloader
from banks.bank_40_linebank import LineBankDownloader
from banks.bank_41_nextbank import NextBankDownloader


# 銀行下載器對照表
BANK_DOWNLOADERS: Dict[str, Type[BaseBankDownloader]] = {
    "臺灣銀行": BOTDownloader,
    "臺灣土地銀行": LandBankDownloader,
    "合作金庫商業銀行": TCBBankDownloader,
    "第一商業銀行": FirstBankDownloader,
    "華南商業銀行": HNCBDownloader,
    "彰化商業銀行": CHBDownloader,
    "上海商業儲蓄銀行": SCSBDownloader,
    "台北富邦銀行": FubonDownloader,
    "國泰世華商業銀行": CathayDownloader,
    "中國輸出入銀行": EximBankDownloader,
    "高雄銀行": BOKDownloader,
    "兆豐國際商業銀行": MegaBankDownloader,
    "花旗（台灣）銀行": CitibankDownloader,
    "王道商業銀行": OBankDownloader,
    "臺灣中小企業銀行": TBBDownloader,
    "渣打國際商業銀行": SCBDownloader,
    "台中商業銀行": TaichungBankDownloader,
    "京城商業銀行": KTBDownloader,
    "匯豐(台灣)商業銀行": HSBCDownloader,
    "瑞興商業銀行": TaipeiStarBankDownloader,
    "華泰商業銀行": HwataiBankDownloader,
    "臺灣新光商業銀行": SKBankDownloader,
    "陽信商業銀行": SunnyBankDownloader,
    "板信商業銀行": BOPDownloader,
    "三信商業銀行": CotaBankDownloader,
    "聯邦商業銀行": UBOTDownloader,
    "遠東國際商業銀行": FEIBDownloader,
    "元大商業銀行": YuantaBankDownloader,
    "永豐商業銀行": SinoPacDownloader,
    "玉山商業銀行": ESunBankDownloader,
    "凱基商業銀行": KGIBankDownloader,
    "星展(台灣)商業銀行": DBSBankDownloader,
    "台新國際商業銀行": TaishinBankDownloader,
    "安泰商業銀行": EntieBankDownloader,
    "中國信託商業銀行": CTBCBankDownloader,
    "樂天國際商業銀行": RakutenBankDownloader,
    "連線商業銀行": LineBankDownloader,
    "將來商業銀行": NextBankDownloader,
}

# 銀行代碼對照表
BANK_CODES: Dict[int, str] = {
    1: "臺灣銀行",
    2: "臺灣土地銀行",
    3: "合作金庫商業銀行",
    4: "第一商業銀行",
    5: "華南商業銀行",
    6: "彰化商業銀行",
    7: "上海商業儲蓄銀行",
    8: "台北富邦銀行",
    9: "國泰世華商業銀行",
    10: "中國輸出入銀行",
    11: "高雄銀行",
    12: "兆豐國際商業銀行",
    13: "花旗（台灣）銀行",
    15: "王道商業銀行",
    16: "臺灣中小企業銀行",
    17: "渣打國際商業銀行",
    18: "台中商業銀行",
    19: "京城商業銀行",
    20: "匯豐(台灣)商業銀行",
    21: "瑞興商業銀行",
    22: "華泰商業銀行",
    23: "臺灣新光商業銀行",
    24: "陽信商業銀行",
    25: "板信商業銀行",
    26: "三信商業銀行",
    27: "聯邦商業銀行",
    28: "遠東國際商業銀行",
    29: "元大商業銀行",
    30: "永豐商業銀行",
    31: "玉山商業銀行",
    32: "凱基商業銀行",
    33: "星展(台灣)商業銀行",
    34: "台新國際商業銀行",
    36: "安泰商業銀行",
    37: "中國信託商業銀行",
    38: "樂天國際商業銀行",
    40: "連線商業銀行",
    41: "將來商業銀行",
}


class BankDownloader:
    """銀行財報下載器"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化下載器
        
        Args:
            data_dir: 資料存放目錄
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_downloader(self, bank_name: str) -> Optional[BaseBankDownloader]:
        """
        取得銀行下載器
        
        Args:
            bank_name: 銀行名稱
            
        Returns:
            銀行下載器實例，若不支援則回傳 None
        """
        downloader_class = BANK_DOWNLOADERS.get(bank_name)
        if downloader_class:
            return downloader_class(data_dir=self.data_dir)
        return None
    
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
        downloader = self.get_downloader(bank_name)
        if not downloader:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"不支援的銀行: {bank_name}"
            )
        
        return downloader.download(year, quarter)
    
    def download_by_code(self, bank_code: int, year: int, quarter: int) -> DownloadResult:
        """
        依銀行代碼下載財報
        
        Args:
            bank_code: 銀行代碼
            year: 民國年
            quarter: 季度 (1-4)
            
        Returns:
            DownloadResult: 下載結果
        """
        bank_name = BANK_CODES.get(bank_code)
        if not bank_name:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"不支援的銀行代碼: {bank_code}"
            )
        
        return self.download(bank_name, year, quarter)
    
    def download_all(self, year: int, quarter: int) -> Dict[str, DownloadResult]:
        """
        下載所有銀行的財報
        
        Args:
            year: 民國年
            quarter: 季度 (1-4)
            
        Returns:
            Dict: 各銀行的下載結果
        """
        results = {}
        for bank_name in BANK_DOWNLOADERS.keys():
            print(f"下載 {bank_name}...")
            results[bank_name] = self.download(bank_name, year, quarter)
        return results
    
    @staticmethod
    def list_supported_banks() -> list:
        """列出所有支援的銀行"""
        return list(BANK_DOWNLOADERS.keys())
    
    @staticmethod
    def list_bank_codes() -> Dict[int, str]:
        """列出所有銀行代碼"""
        return BANK_CODES.copy()
