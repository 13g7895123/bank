# 銀行財報自動化系統 (Refactor 版)

## 專案簡介

本系統是銀行財報自動化抓取與分析系統的重構版本，使用 Playwright 取代 Selenium，提供更穩定、快速的網頁自動化體驗。支援 **38 家** 台灣銀行的財報處理，目前 **30 家運作正常**。

## 功能特色

### 1. 財報自動下載
- 自動從各銀行官網抓取指定年度/季度的財務報表
- 支援單一銀行或批次下載全部銀行
- 模組化設計，每家銀行獨立檔案，易於維護
- 支援多種瀏覽器（Chromium、Firefox、WebKit）
- 自動檢測已下載檔案，避免重複下載

### 2. 資產品質報表製作
- 自動解析 PDF 財報，提取「資產品質」表格資料
- 支援多種 PDF 格式解析（文字型與圖片型）
- 將資料彙整輸出為 Excel 格式

## 環境需求

### Python 版本
- Python 3.8 以上

### 必要套件
```bash
pip install -r requirements.txt
```

主要依賴：
```bash
# 網頁自動化
pip install playwright
playwright install  # 安裝瀏覽器

# 資料處理
pip install pandas openpyxl

# PDF 處理
pip install pdfplumber
```

## 檔案結構

```
refactor/
├── cli.py                 # 互動式命令列介面（主程式）
├── main.py                # 命令列參數版主程式
├── downloader.py          # 下載器主模組
├── report_generator.py    # 報表生成模組
├── README.md              # 說明文件
├── banks/                 # 各銀行下載模組
│   ├── __init__.py
│   ├── base.py            # 基礎類別
│   ├── bank_01_bot.py     # 臺灣銀行
│   ├── bank_02_landbank.py # 臺灣土地銀行
│   ├── ...                # 其他銀行
│   └── bank_41_nextbank.py # 將來商業銀行
└── data/                  # 測試用資料目錄
```

## 使用方式

### 方式一：互動式介面（推薦）

```bash
cd refactor
python cli.py
```

啟動後會顯示選單：

```
============================================================
              銀行財報自動化系統 (Refactor 版)
============================================================

請選擇功能：

  [1] 下載財報
  [2] 製作報表
  [0] 離開程式

請選擇功能：
```

#### 模式一：下載財報 (輸入 1)

1. 輸入欲下載的季度，格式為 `年度Q季度`（例如：`114Q1`）
2. 選擇下載方式：
   - 輸入 `1`：下載單一銀行財報
   - 輸入 `ALL`：下載全部銀行財報

##### 單一銀行下載
```
請輸入銀行代碼或名稱（部分名稱亦可）：
```
可輸入銀行代碼（如 `3`）或名稱關鍵字（如 `合作金庫`）。

##### 全部銀行下載
系統會自動下載所有銀行的財報，完成後會列出下載失敗的銀行清單。

#### 模式二：製作報表 (輸入 2)

1. 輸入欲製作報表的季度（例如：`114Q1`）
2. 系統會自動解析 `data/` 資料夾中對應季度的 PDF 檔案
3. 提取「資產品質」資料並輸出至 `Output/` 資料夾

### 方式二：命令列參數

```bash
# 下載並生成報表（預設 114Q1）
python main.py

# 指定年度季度
python main.py 114Q1

# 只下載
python main.py 114Q1 --download-only

# 只生成報表
python main.py 114Q1 --report-only

# 指定銀行
python main.py 114Q1 --banks 合作金庫 玉山 台新

# 顯示瀏覽器視窗（除錯用）
python main.py 114Q1 --show-browser
```

### 方式三：程式碼呼叫

```python
from refactor.downloader import BankDownloader

# 建立下載器
downloader = BankDownloader(data_dir="data")

# 下載單一銀行
result = downloader.download("合作金庫商業銀行", year=114, quarter=1)
print(result.status, result.message)

# 下載全部銀行
results = downloader.download_all(year=114, quarter=1)

# 列出支援的銀行
banks = BankDownloader.list_supported_banks()
```

## 支援狀態

### 運作正常（30 家）✅

| 代碼 | 銀行名稱 | 代碼 | 銀行名稱 |
|------|----------|------|----------|
| 02 | 臺灣土地銀行 | 19 | 京城商業銀行 |
| 03 | 合作金庫商業銀行 | 21 | 瑞興商業銀行 |
| 04 | 第一商業銀行 | 23 | 臺灣新光商業銀行 |
| 05 | 華南商業銀行 | 24 | 陽信商業銀行 |
| 06 | 彰化商業銀行 | 25 | 板信商業銀行 |
| 07 | 上海商業儲蓄銀行 | 26 | 三信商業銀行 |
| 08 | 台北富邦銀行 | 27 | 聯邦商業銀行 |
| 10 | 中國輸出入銀行 | 29 | 元大商業銀行 |
| 11 | 高雄銀行 | 30 | 永豐商業銀行 |
| 12 | 兆豐國際商業銀行 | 31 | 玉山商業銀行 |
| 15 | 王道商業銀行 | 32 | 凱基商業銀行 |
| 16 | 臺灣中小企業銀行 | 33 | 星展(台灣)商業銀行 |
| 17 | 渣打國際商業銀行 | 34 | 台新國際商業銀行 |
| 18 | 台中商業銀行 | 36 | 安泰商業銀行 |
|    |              | 37 | 中國信託商業銀行 |
|    |              | 38 | 樂天國際商業銀行 |

### 尚待修復（8 家）❌

| 代碼 | 銀行名稱 | 問題描述 |
|------|----------|----------|
| 01 | 臺灣銀行 | URL 需導航到財報專區 |
| 09 | 國泰世華商業銀行 | 頁面載入逾時 |
| 13 | 花旗（台灣）銀行 | 頁面載入逾時 |
| 20 | 匯豐(台灣)商業銀行 | 需找到正確財報頁面 |
| 22 | 華泰商業銀行 | 連結格式不同 |
| 28 | 遠東國際商業銀行 | URL 需調整 |
| 40 | 連線商業銀行 | 需調整選擇器 |
| 41 | 將來商業銀行 | 頁面載入逾時 |

## 輸出資料說明

### 資產品質報表欄位

| 欄位 | 說明 |
|------|------|
| 資料年度 | 民國年 |
| 季度 | Q1~Q4 |
| 業務別項目 | 8 種業務類別 |
| 逾期放款金額(單位：仟元) | 逾期放款金額 |
| 放款總額(單位：仟元) | 放款總額 |
| 逾放比率 | 逾期放款比率 |
| 銀行名稱 | 銀行名稱 |

### 8 種業務類別

1. 企業金融_擔保
2. 企業金融_無擔保
3. 消費金融_住宅抵押貸款
4. 消費金融_現金卡
5. 消費金融_小額純信用貸款
6. 消費金融_其他_擔保
7. 消費金融_其他_無擔保
8. 合計

## 架構說明

### 模組化設計

每家銀行有獨立的下載器類別，繼承自 `BaseBankDownloader`：

```python
# banks/bank_XX_example.py
from .base import BaseBankDownloader, DownloadResult, DownloadStatus

class ExampleBankDownloader(BaseBankDownloader):
    bank_name = "範例銀行"
    bank_code = 99
    bank_url = "https://example.com/financial"
    
    def _download(self, page, year, quarter) -> DownloadResult:
        # 實作下載邏輯
        pass
```

### 新增銀行支援

1. 在 `banks/` 目錄建立 `bank_XX_name.py`
2. 繼承 `BaseBankDownloader` 實作 `_download` 方法
3. 在 `downloader.py` 中註冊新的下載器

### 特殊需求

部分銀行需要特殊設定：

```python
# 使用 Firefox 繞過反爬蟲
browser_type = "firefox"

# 關閉無頭模式（除錯用）
headless = False
```

## 與原版差異

| 項目 | 原版 (Main.py) | 重構版 (refactor/) |
|------|----------------|-------------------|
| 自動化工具 | Selenium | Playwright |
| 架構 | 單一檔案 | 模組化設計 |
| 銀行邏輯 | if-else 分支 | 獨立類別 |
| Proxy | 需要設定 | 不需要 |
| 維護性 | 較低 | 較高 |
| 擴充性 | 較低 | 較高 |

## 常見問題

### Q1: Playwright 安裝失敗？
```bash
pip install playwright
playwright install
```

### Q2: 下載失敗怎麼辦？
- 確認網路連線正常
- 確認該銀行是否已公布該季度財報
- 使用 `--show-browser` 參數查看實際頁面狀況

### Q3: PDF 解析失敗？
- 部分銀行的 PDF 格式特殊，可能需要調整解析邏輯
- 檢查 PDF 檔案是否完整下載

## 更新日誌

- **v2.0** (2025-11)：使用 Playwright 重構，模組化設計
- **v2.1** (2025-11)：新增互動式 CLI 介面，完善 30 家銀行支援

## 授權資訊

本專案僅供內部使用，未經授權請勿散布
