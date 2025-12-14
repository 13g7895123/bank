# 銀行財報自動化系統 - Refactor 版本

> 自動下載台灣各銀行財報 PDF 並提取「資產品質」資料

## 快速開始

### 1. 安裝相依套件

```bash
# 1. 建立並啟用虛擬環境 (建議)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 2. 安裝 Python 套件
pip install -r requirements.txt

# 3. 安裝 Playwright 瀏覽器
playwright install chromium

# 4. OCR 支援（可選，處理掃描式 PDF）
# Mac: brew install tesseract tesseract-lang poppler
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-chi-tra poppler-utils
# Windows: 需手動安裝 Tesseract OCR 與 Poppler 並設定 PATH
```

### 2. 執行程式

```bash
cd refactor

# 互動式選單（推薦）
python cli.py

# 命令列模式
python main.py 114Q1                    # 下載 + 生成報表
python main.py 114Q1 --download-only    # 只下載
python main.py 114Q1 --report-only      # 只生成報表
```

---

## 開發環境設定與遷移

若您需要更換電腦或重新建置開發環境，請遵循以下標準流程。

### 為什麼不能直接複製 venv？
虛擬環境 (`venv`) 資料夾包含絕對路徑與特定作業系統的二進位檔案，**無法直接複製到另一台電腦使用**。請務必在新電腦上重新建立環境。

### 遷移步驟

1. **舊電腦：匯出依賴**
   確認 `requirements.txt` 包含所有需要的套件：
   ```bash
   pip freeze > requirements.txt
   ```

2. **傳輸程式碼**
   將專案資料夾複製到新電腦（**排除** `venv` 資料夾）。

3. **新電腦：重建環境**
   ```bash
   # 1. 進入專案目錄
   cd refactor

   # 2. 建立新的虛擬環境
   python -m venv venv

   # 3. 啟用虛擬環境
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate

   # 4. 安裝依賴
   pip install -r requirements.txt
   playwright install chromium
   ```

---

## 功能說明

### 支援銀行

支援 **38 家** 台灣銀行的財報下載與解析：
- 臺灣銀行、土地銀行、合庫、一銀、華銀...
- 中信、國泰、玉山、台新、永豐...
- LINE Bank、將來銀行、樂天銀行...

完整清單請參考 [STATUS.md](STATUS.md)

### 資料類別

提取「資產品質」表中的 **8 種業務類別**：

| 代碼 | 類別 |
|------|------|
| 01 | 企業金融_擔保 |
| 02 | 企業金融_無擔保 |
| 03 | 消費金融_住宅抵押貸款 |
| 04 | 消費金融_現金卡 |
| 05 | 消費金融_小額純信用貸款 |
| 06 | 消費金融_其他_擔保 |
| 07 | 消費金融_其他_無擔保 |
| 08 | 合計 |

### 輸出資料

每個類別提取以下欄位：
- 逾期放款金額
- 放款總額
- 逾期放款比率
- 備抵呆帳金額
- 備抵呆帳覆蓋率

---

## 使用方式

### 方式一：互動式介面（推薦）

```bash
python cli.py
```

選單選項：
1. 下載財報
2. 生成報表
3. 下載並生成報表
4. 查看銀行清單
5. 離開

### 方式二：命令列

```bash
# 完整流程（下載 + 報表）
python main.py 114Q1

# 只下載 PDF
python main.py 114Q1 --download-only

# 只生成報表（需要先有 PDF）
python main.py 114Q1 --report-only

# 指定輸出目錄
python main.py 114Q1 --output ./my_output
```

### 方式三：Python API

```python
from refactor.core import DownloadManager, ReportManager

# 初始化
dm = DownloadManager(data_dir='data')
rm = ReportManager()

# 下載單一銀行
result = dm.download('玉山商業銀行', 114, 1)
print(f'狀態: {result.status.name}')
print(f'檔案: {result.file_path}')

# 下載所有銀行
results = dm.download_all(114, 1)
summary = dm.get_download_summary(results)
print(f'成功: {summary["success"]}, 失敗: {summary["failed"]}')

# 解析 PDF
parse_result = rm.parse_pdf('data/114Q1/31_玉山商業銀行_114Q1.pdf')
print(f'解析類別: {parse_result.category_count}/8')
for row in parse_result.rows:
    print(f'{row.subject}: 逾期={row.overdue_amount:,.0f}')

# 生成報表
df = rm.generate_report('data/114Q1', 'output/report.xlsx')
print(f'共 {len(df)} 筆資料')
```

### 方式四：OCR 解析（掃描式 PDF）

部分銀行的 PDF 為掃描圖片格式，需使用 OCR：

```python
from refactor.core import OCRParser, is_scanned_pdf

pdf_path = 'data/114Q1/20_匯豐(台灣)商業銀行_114Q1.pdf'

# 檢查是否需要 OCR
if is_scanned_pdf(pdf_path):
    parser = OCRParser()
    result = parser.parse_pdf(pdf_path, '匯豐(台灣)商業銀行')
    
    print(f'解析類別: {result.category_count}/8')
    for row in result.rows:
        print(f'{row.subject}: {row.overdue_amount:,.0f}')
```

---

## 目錄結構

```
refactor/
├── core/                    # 核心模組
│   ├── models.py            # 資料模型
│   ├── download_manager.py  # 下載管理器
│   ├── report_manager.py    # 報表管理器
│   └── ocr_parser.py        # OCR 解析器
│
├── banks/                   # 銀行下載器（38 個）
│   ├── base.py              # 基礎類別
│   └── bank_XX_xxx.py       # 各銀行實作
│
├── utils/                   # 工具模組
│   ├── text.py              # 文字處理
│   ├── date.py              # 日期處理
│   └── file.py              # 檔案處理
│
├── docs/                    # 文件
│   ├── DOWNLOADER_AUDIT.md  # 下載器盤點
│   └── *.md                 # 調查報告
│
├── cli.py                   # 互動式介面
├── main.py                  # 命令列主程式
├── downloader.py            # 下載器
├── report_generator.py      # 報表生成器
├── ARCHITECTURE.md          # 架構說明
├── STATUS.md                # 狀態說明
└── README.md                # 使用說明（本文件）
```

---

## 輸出說明

### PDF 檔案

下載的 PDF 儲存於 `data/{年度}Q{季度}/` 目錄：

```
data/
└── 114Q1/
    ├── 01_臺灣銀行_114Q1.pdf
    ├── 02_臺灣土地銀行_114Q1.pdf
    ├── 03_合作金庫商業銀行_114Q1.pdf
    └── ...
```

### Excel 報表

生成的報表包含以下欄位：

| 欄位 | 說明 |
|------|------|
| 銀行名稱 | 銀行中文名稱 |
| 年度 | 民國年度（如 114） |
| 季度 | Q1, Q2, Q3, Q4 |
| 業務類別 | 01~08 類別代碼 |
| 逾期放款金額 | 千元 |
| 放款總額 | 千元 |
| 逾期放款比率 | 百分比 |
| 備抵呆帳金額 | 千元 |
| 備抵呆帳覆蓋率 | 百分比 |

---

## 常見問題

### Q: 下載失敗怎麼辦？

1. 檢查網路連線
2. 確認銀行官網是否可訪問
3. 執行診斷工具：
   ```bash
   python tests/diagnose_failed_banks.py
   ```

### Q: 解析結果不完整？

部分銀行的 PDF 格式特殊：
- **掃描式 PDF**：使用 OCR 解析（匯豐、瑞興）
- **政策性銀行**：無消費金融業務（輸出入銀行）

### Q: 如何新增銀行支援？

1. 建立 `banks/bank_XX_xxx.py`
2. 繼承 `BaseBankDownloader`
3. 實作 `_download()` 方法

詳見 [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 相關文件

| 文件 | 說明 |
|------|------|
| [STATUS.md](STATUS.md) | 系統狀態、各銀行功能狀態 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 架構說明、API 文件 |
| [docs/DOWNLOADER_AUDIT.md](docs/DOWNLOADER_AUDIT.md) | 下載器完整盤點 |

---

## 更新日誌

| 版本 | 日期 | 變更 |
|------|------|------|
| 2.1 | 2024-11-29 | 新增 OCR 解析器、修復匯豐銀行下載器 |
| 2.0 | 2024-11-29 | 重構架構：新增 core/, utils/ 模組 |
| 1.0 | 2024-11-25 | 初始 Playwright 版本 |
