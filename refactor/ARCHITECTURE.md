# 銀行財報自動化系統 - Refactor 版本

> 更新日期：2024-11-29

## 架構概覽

```
refactor/
├── core/                    # 核心模組
│   ├── __init__.py
│   ├── models.py            # 資料模型定義
│   ├── download_manager.py  # 下載管理器
│   ├── report_manager.py    # 報表管理器
│   └── ocr_parser.py        # OCR 解析器（掃描式 PDF）
│
├── banks/                   # 銀行下載器
│   ├── base.py              # 下載器基礎類別
│   └── bank_XX_xxx.py       # 各銀行實作（38 個）
│
├── utils/                   # 工具模組
│   ├── __init__.py
│   ├── text.py              # 文字處理（normalize_text, parse_number）
│   ├── date.py              # 日期處理（parse_year_quarter）
│   └── file.py              # 檔案處理（ensure_dir, get_file_path）
│
├── docs/                    # 文件
│   ├── DOWNLOADER_AUDIT.md  # 下載器盤點報告
│   └── *.md                 # 調查報告
│
├── tests/                   # 測試工具
│   ├── diagnose_failed_banks.py  # 下載失敗診斷
│   └── test_all.py               # 批次測試
│
├── cli.py                   # 互動式命令列介面
├── main.py                  # 命令列主程式
├── downloader.py            # 下載器（相容舊版）
├── report_generator.py      # 報表生成器（相容舊版）
├── ARCHITECTURE.md          # 架構說明（本文件）
└── STATUS.md                # 狀態說明文件
```

## 模組說明

### 1. 核心模組 (`core/`)

#### `models.py` - 資料模型

| 類別 | 說明 |
|------|------|
| `DownloadStatus` | 下載狀態列舉（SUCCESS, ALREADY_EXISTS, NO_DATA, ERROR） |
| `ParseStatus` | 解析狀態列舉（SUCCESS, PARTIAL, FAILED, NO_FILE） |
| `BankInfo` | 銀行基本資訊 |
| `DownloadResult` | 下載結果 |
| `AssetQualityRow` | 資產品質資料列 |
| `ParseResult` | 解析結果 |
| `SUBJECT_MAPPING` | 業務類別對應表（8 種類別） |

#### `download_manager.py` - 下載管理器

```python
from refactor.core import DownloadManager

manager = DownloadManager(data_dir='data')

# 下載單一銀行
result = manager.download('玉山商業銀行', 114, 1)

# 下載所有銀行
results = manager.download_all(114, 1)

# 取得統計
summary = manager.get_download_summary(results)
```

#### `report_manager.py` - 報表管理器

```python
from refactor.core import ReportManager

manager = ReportManager()

# 解析單一 PDF
result = manager.parse_pdf('data/114Q1/31_玉山商業銀行_114Q1.pdf')

# 生成報表
df = manager.generate_report('data/114Q1', 'output/report.xlsx')
```

#### `ocr_parser.py` - OCR 解析器（新增）

處理掃描式 PDF（無法直接提取文字的 PDF）。

```python
from refactor.core import OCRParser, is_scanned_pdf

# 檢查是否為掃描式 PDF
if is_scanned_pdf('path/to/pdf'):
    parser = OCRParser()
    result = parser.parse_pdf('path/to/pdf', '銀行名稱')
    
    print(f'解析類別: {result.category_count}/8')
    for row in result.rows:
        print(f'{row.subject}: {row.overdue_amount}')
```

**OCR 設定**：
- 語言：繁體中文 + 英文 (`chi_tra+eng`)
- DPI：400
- 預處理：灰階、增強對比、銳化

### 2. 銀行下載器 (`banks/`)

每個銀行有獨立的下載器檔案，繼承自 `BaseBankDownloader`：

```python
class BaseBankDownloader(ABC):
    bank_name: str      # 銀行名稱
    bank_code: int      # 銀行代碼
    bank_url: str       # 財報網址
    headless: bool = True  # 預設無頭模式
    retry_with_head: bool = True  # 失敗時自動重試有頭模式
    
    def download(self, year: int, quarter: int) -> DownloadResult:
        """下載財報"""
        
    @abstractmethod
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        """實際下載邏輯（子類別實作）"""
```

**無頭/有頭模式自動切換**：

1. 預設使用無頭模式（headless=True）下載
2. 下載後自動驗證：
   - 檔案是否存在
   - 檔案大小是否 > 1KB
   - 檔案頭是否為 `%PDF`
3. 若驗證失敗，自動清理並使用有頭模式重試
4. 訊息會標註 `(使用有頭模式)` 表示經過重試

**下載方式**：

| 方式 | 方法 | 數量 | 說明 |
|------|------|------|------|
| URL 直接下載 | `download_pdf_from_url` | 31 家 | 透過 `page.request.get()` |
| 點擊下載 | `download_pdf_by_click` | 4 家 | 透過 `expect_download` |
| 特殊處理 | 自訂 | 3 家 | GraphQL API / JavaScript |

### 3. 工具模組 (`utils/`)

| 模組 | 功能 |
|------|------|
| `text.py` | `normalize_text()` 文字正規化、`parse_number()` 數字解析 |
| `date.py` | `parse_year_quarter()` 年度季度解析、`get_quarter_text()` 格式化 |
| `file.py` | `ensure_dir()` 目錄處理、`get_file_path()` 檔案路徑 |

### 4. 文件 (`docs/`)

| 文件 | 說明 |
|------|------|
| `DOWNLOADER_AUDIT.md` | 38 家銀行下載器完整盤點 |
| `企業金融類別調查報告.md` | 企業金融解析問題調查 |
| `現金卡資料調查報告.md` | 現金卡解析問題調查 |
| `消費金融其他無擔保調查報告.md` | 消費金融解析問題調查 |

## 使用方式

### 命令列介面

```bash
# 互動式選單
python refactor/cli.py

# 指令模式
python refactor/main.py 114Q1                    # 下載+報表
python refactor/main.py 114Q1 --download-only    # 只下載
python refactor/main.py 114Q1 --report-only      # 只報表
```

### Python API

```python
# 方式一：使用管理器（推薦）
from refactor.core import DownloadManager, ReportManager

dm = DownloadManager(data_dir='data')
rm = ReportManager()

# 下載
result = dm.download('玉山商業銀行', 114, 1)

# 解析
parse_result = rm.parse_pdf('data/114Q1/31_玉山商業銀行_114Q1.pdf')

# 方式二：使用舊版相容介面
from refactor.downloader import BankDownloader
from refactor.report_generator import generate_report

downloader = BankDownloader(data_dir='data')
result = downloader.download('玉山商業銀行', 114, 1)

df = generate_report('data/114Q1', 'output/report.xlsx')

# 方式三：OCR 解析（掃描式 PDF）
from refactor.core import OCRParser, is_scanned_pdf

if is_scanned_pdf('path/to/pdf'):
    parser = OCRParser()
    result = parser.parse_pdf('path/to/pdf', '銀行名稱')
```

## 設計原則

### 1. 易讀性
- 清晰的模組分層
- 完整的型別標註
- 詳細的 docstring

### 2. 易維護性
- 單一職責原則
- 每個銀行獨立檔案
- 統一的錯誤處理

### 3. 可擴充性
- 抽象基礎類別
- 註冊機制
- 插件式架構

## 新增銀行支援

1. 建立新檔案 `banks/bank_XX_xxx.py`
2. 繼承 `BaseBankDownloader`
3. 實作 `_download()` 方法
4. 在 `downloader.py` 中註冊

```python
# banks/bank_99_newbank.py
from .base import BaseBankDownloader, DownloadResult, DownloadStatus

class NewBankDownloader(BaseBankDownloader):
    bank_name = "新銀行"
    bank_code = 99
    bank_url = "https://example.com"
    
    def _download(self, page, year, quarter):
        # 實作下載邏輯
        pass
```

## 相依套件

### 必要套件

```
playwright>=1.40.0    # 網頁自動化
pdfplumber>=0.7.0     # PDF 解析
pandas>=1.5.0         # 資料處理
openpyxl>=3.0.0       # Excel 輸出
```

### OCR 支援（可選）

```bash
# macOS
brew install tesseract tesseract-lang poppler

# Python 套件
pip install pytesseract pdf2image pillow
```

## 相關文件

| 文件 | 說明 |
|------|------|
| `STATUS.md` | 系統狀態、各銀行功能狀態、修復記錄 |
| `docs/DOWNLOADER_AUDIT.md` | 下載器完整盤點報告 |
| `../AGENTS.md` | AI 代理協作指南 |
