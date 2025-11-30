# 銀行財報自動化系統

> 自動下載台灣各銀行財報 PDF 並提取「資產品質」資料到 Excel 報表

**✅ 系統狀態：正常運行** | 支援 **38 家銀行** | 最後更新：2025-11-30

## 快速開始

### 1. 環境準備

```bash
# 安裝 Python 3.8+ 相依套件
pip install -r requirements.txt

# Playwright 瀏覽器驅動
python -m playwright install chromium

# 【選用】OCR 支援（處理掃描式 PDF）
# Linux/Mac:
brew install tesseract tesseract-lang poppler
# 或
sudo apt install tesseract-ocr poppler-utils
```

### 2. 快速執行

```bash
# 【推薦】互動式選單
python3 cli.py

# 或命令列模式
python3 main.py 114Q1                      # 完整流程
python3 main.py 114Q1 --download-only      # 只下載 PDF
python3 main.py 114Q1 --report-only        # 只生成報表
```

---

## 功能特色

### 📊 支援銀行

**38 家台灣銀行**，包括：
- 公股行庫：臺灣銀行、土地銀行、合庫、一銀、華銀
- 民營商銀：中信、國泰、玉山、台新、永豐
- 網路銀行：LINE Bank、樂天銀行、將來銀行

完整清單及狀態詳見 [STATUS.md](STATUS.md)

### 📈 提取資料

每家銀行的每季財報提取 **8 種業務類別**：

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

### 💻 方式一：互動式選單（推薦）

```bash
python3 cli.py
```

選單功能：
1. 下載財報 PDF
2. 生成資產品質報表
3. 下載並生成報表（完整流程）
4. 查看支援銀行清單
5. 離開程式

### 🖥️ 方式二：命令列（適合自動化）

```bash
# 完整流程（下載 + 報表）
python3 main.py 114Q1

# 只下載 PDF
python3 main.py 114Q1 --download-only

# 只生成報表（前提：已有 PDF 檔案）
python3 main.py 114Q1 --report-only

# 指定特定銀行
python3 main.py 114Q1 --banks 臺灣銀行 台新銀行

# 指定輸出路徑
python3 main.py 114Q1 --output ./my_output

# 並行下載（加快速度，預設 5）
python3 main.py 114Q1 --parallel 10

# 顯示瀏覽器過程（預設無頭模式）
python3 main.py 114Q1 --show-browser
```

### 🐍 方式三：Python API

```python
from downloader import DownloadManager
from report_generator import ReportGenerator

# 初始化下載管理器
dm = DownloadManager(data_dir='data', headless=True)

# 下載單一銀行（以玉山銀行 114Q1 為例）
result = dm.download_bank('玉山商業銀行', 114, 1)
print(f'下載狀態: {result["status"]}')
print(f'檔案路徑: {result["file_path"]}')

# 下載所有銀行
results = dm.download_all(114, 1, parallel=5)
successful = sum(1 for r in results if r['status'] == 'success')
print(f'成功: {successful}/{len(results)}')

# 生成報表
rg = ReportGenerator()
excel_file = rg.generate_report('data/114Q1', 'output/report_114Q1.xlsx')
print(f'報表已生成：{excel_file}')
```

### 🔍 方式四：OCR 解析（掃描式 PDF）

部分銀行（匯豐、瑞興）的 PDF 為掃描圖片格式，系統自動使用 OCR 解析：

```bash
# 系統已內建自動檢測和 OCR 處理
python3 main.py 114Q1

# 查看 OCR 處理進度
# （日誌中會顯示 "OCR 解析中..." 標記）
```

---

## 目錄結構

```
production/
├── core/                    # 核心模組（已棄用，使用新架構）
├── banks/                   # 銀行下載器實現（38 個銀行）
├── utils/                   # 工具模組
│   ├── text.py              # 文字處理
│   ├── date.py              # 日期轉換
│   └── file.py              # 檔案操作
├── data/                    # PDF 下載存放目錄
│   └── {年度}Q{季度}/       # 如 114Q1/
├── output/                  # Excel 報表輸出目錄
├── cli.py                   # 互動式介面（主推薦）
├── main.py                  # 命令列程式
├── downloader.py            # 下載器核心邏輯
├── report_generator.py      # 報表生成器
├── STATUS.md                # 各銀行狀態表
└── README.md                # 本說明文件
```

## 輸出說明

### 📁 下載的 PDF

存放於 `data/{年度}Q{季度}/` 目錄，命名格式：

```
data/114Q1/
├── 01_臺灣銀行_114Q1.pdf
├── 02_臺灣土地銀行_114Q1.pdf
├── 03_合作金庫商業銀行_114Q1.pdf
└── ...（共 38 家銀行）
```

### 📊 Excel 報表

生成的報表包含以下欄位：

| 欄位 | 說明 | 備註 |
|------|------|------|
| 銀行名稱 | 銀行中文名稱 | - |
| 年度 | 民國年度 | 如 114 |
| 季度 | 季別 | Q1, Q2, Q3, Q4 |
| 業務類別 | 資產品質類別代碼 | 01~08 |
| 逾期放款金額 | 單位：千元 | 原始數值 |
| 放款總額 | 單位：千元 | 原始數值 |
| 逾期放款比率 | 百分比 (%) | 自動計算 |
| 備抵呆帳金額 | 單位：千元 | 原始數值 |
| 備抵呆帳覆蓋率 | 百分比 (%) | 自動計算 |

**範例輸出檔案**：`output/114Q1_資產品質.xlsx`

---

## 常見問題

### Q: 下載失敗或卡住怎麼辦？

**解決方案**：
1. 檢查網路連線穩定性
2. 確認銀行官網可正常訪問
3. 確認已安裝 Chromium 瀏覽器驅動：
   ```bash
   python3 -m playwright install chromium
   ```
4. 顯示瀏覽器視窗，觀察下載過程：
   ```bash
   python3 main.py 114Q1 --show-browser
   ```

### Q: 部分銀行無法解析資料？

**原因與處理**：
- **掃描式 PDF**（匯豐、瑞興）→ 系統自動使用 OCR 解析
- **政策性銀行**（輸出入銀行）→ 業務類別少於 8 個（正常）
- **無特定業務**（如國泰無現金卡）→ 該類別無資料（正常）

查看 [STATUS.md](STATUS.md) 了解各銀行已知狀態。

### Q: 如何自訂下載並行數？

```bash
# 並行 10 個下載（預設 5 個）
python3 main.py 114Q1 --parallel 10

# 或在程式中
dm = DownloadManager()
results = dm.download_all(114, 1, parallel=10)
```

### Q: Excel 報表無法開啟？

確保已安裝 `openpyxl`：
```bash
pip install openpyxl --upgrade
```

### Q: 如何新增銀行支援？

詳見 [ARCHITECTURE.md](ARCHITECTURE.md) 內的「擴展指南」部分。

---

## 技術細節

### 依賴套件

| 套件 | 版本 | 用途 |
|------|------|------|
| playwright | ≥1.40.0 | 網頁自動化、PDF 下載 |
| pandas | ≥1.5.0 | 資料處理與轉換 |
| pdfplumber | ≥0.7.0 | PDF 表格解析 |
| openpyxl | ≥3.0.0 | Excel 生成 |
| pytesseract | ≥0.3.10 | OCR 文字辨識（可選） |
| opencv-python | ≥4.7.0 | 圖像處理（可選） |

### 支援 Python 版本

- Python 3.8+
- 推薦 Python 3.10+

### 系統需求

| 項目 | 要求 |
|------|------|
| OS | Windows / macOS / Linux |
| 磁碟空間 | 500MB（含瀏覽器驅動） |
| 記憶體 | 2GB 以上 |
| 網路 | 穩定 Internet 連線 |

---

## 相關文件

| 文件 | 內容 |
|------|------|
| [STATUS.md](STATUS.md) | 38 家銀行的下載與解析狀態明細表 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系統架構設計、API 詳細文件 |
| [AGENTS.md](AGENTS.md) | AI 協作指南與開發規範 |


---

## 更新日誌

| 版本 | 日期 | 主要變更 |
|------|------|---------|
| **2.2** | 2025-11-30 | 📚 更新文件結構、完善 README；✅ 驗證所有 38 家銀行狀態；🔍 完成 STATUS.md 表格 |
| 2.1 | 2024-11-29 | 新增 OCR 解析器、修復匯豐銀行下載器 |
| 2.0 | 2024-11-29 | 重構架構：新增 core/, utils/ 模組、支援並行下載 |
| 1.0 | 2024-11-25 | 初始 Playwright 版本 |

---

## 許可證

MIT License - 詳見 LICENSE 檔案

## 貢獻指南

若發現問題或有改進建議，歡迎提交 Issue 或 Pull Request。

---

**最後更新**：2025-11-30  
**維護者**：Bank Report Automation Team
