# AGENTS.md

本文件為 AI 代理（如 GitHub Copilot、Cursor 等）在本專案中協作的指導規範。

## 專案概述

本專案是一個銀行財報自動化抓取與分析系統，用於從台灣各大銀行官網抓取財務報表，並提取「資產品質」相關資料彙整成 Excel 報表。

## 技術棧

- **程式語言**：Python 3.8+
- **網頁爬蟲**：Selenium、BeautifulSoup、Requests
- **PDF 處理**：pdfplumber、tabula-py、PyMuPDF
- **圖像處理**：OpenCV、pytesseract (OCR)
- **資料處理**：pandas、numpy、openpyxl

## 專案結構

```
bank/
├── Main.py              # 主程式入口
├── get_Data.py          # 財報下載模組（各銀行爬蟲邏輯）
├── gat_report.py        # 報表製作模組（PDF 解析與資料提取）
├── bank.xlsx            # 銀行清單設定檔
├── requirements.txt     # Python 依賴套件
├── data/                # 下載的財報 PDF 存放目錄
└── Output/              # 輸出報表存放目錄
```

## Git Commit 規範

**務必遵守 [Conventional Commits 1.0](https://www.conventionalcommits.org/zh-hant/v1.0.0/) 規範要求。**

### Commit 訊息格式

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Type 類型

| Type | 說明 |
|------|------|
| `feat` | 新增功能 |
| `fix` | 修復 Bug |
| `docs` | 文件變更 |
| `style` | 程式碼格式調整（不影響程式邏輯） |
| `refactor` | 重構程式碼（不新增功能也不修復 Bug） |
| `perf` | 效能優化 |
| `test` | 新增或修改測試 |
| `chore` | 建構工具或輔助工具變更 |
| `ci` | CI/CD 相關變更 |

### Scope 範圍（選用）

- `crawler` - 爬蟲相關（get_Data.py）
- `report` - 報表製作相關（gat_report.py）
- `main` - 主程式相關（Main.py）
- `config` - 設定檔相關
- `deps` - 依賴套件相關

### Commit 範例

```bash
# 新增功能
feat(crawler): 新增玉山銀行財報下載功能

# 修復 Bug
fix(report): 修正 PDF 解析時表格欄位錯位問題

# 文件更新
docs: 更新 README 安裝說明

# 重構
refactor(crawler): 統一各銀行爬蟲的錯誤處理邏輯

# 依賴更新
chore(deps): 升級 selenium 至 4.15.0
```

## 程式碼風格

- 遵循 PEP 8 規範
- 使用繁體中文撰寫註解與文件
- 函式與變數命名使用英文，採用 snake_case
- 類別命名採用 PascalCase

## 開發注意事項

1. **Proxy 設定**：`get_Data.py` 中的 Proxy IP 需依據實際環境修改
2. **銀行爬蟲**：各銀行網站結構不同，每家銀行有獨立的爬蟲邏輯
3. **PDF 解析**：部分銀行使用掃描式 PDF，需透過 OCR 處理
4. **錯誤處理**：下載失敗時應記錄失敗原因，不中斷整體流程

## 測試指引

執行程式前請確認：
1. 已安裝所有依賴套件：`pip install -r requirements.txt`
2. 已安裝 Edge WebDriver 並加入 PATH
3. 已安裝 Tesseract OCR（如需處理掃描式 PDF）
4. `bank.xlsx` 檔案存在且格式正確

## 常見任務

### 新增銀行支援

1. 在 `bank.xlsx` 中新增銀行資訊
2. 在 `get_Data.py` 中新增對應的爬蟲邏輯（使用 `if name == '銀行名稱':` 分支）
3. 測試下載功能是否正常
4. 確認 PDF 可被 `gat_report.py` 正確解析

### 修復爬蟲失敗

1. 確認銀行官網是否更新結構
2. 使用瀏覽器開發者工具分析新的網頁結構
3. 更新對應的 BeautifulSoup 選擇器或 Selenium 操作
