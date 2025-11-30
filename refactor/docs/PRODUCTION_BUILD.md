# Production 建置說明

## 概述

本文件說明如何從 `refactor` 目錄建置 `production` 版本。

## 建置規則

### 複製項目
- `banks/` - 所有銀行下載器
- `core/` - 核心模組
- `utils/` - 工具函數
- `*.py` - 根目錄 Python 檔案
- `README.md` - 說明文件

### 排除項目
- `data/` - 下載的 PDF 檔案
- `docs/` - 開發文件
- `output/` / `Output/` - 輸出報表
- `tests/` - 測試檔案
- `ARCHITECTURE.md` - 架構文件
- `__pycache__/` - Python 快取

### 特殊處理
- `STATUS.md` - 僅保留「各銀行狀態明細」表格

## 使用方式

```bash
# 使用預設路徑 (../production)
./build_production.sh

# 指定自訂路徑
./build_production.sh /path/to/production
```

## 建置腳本

執行 `build_production.sh` 會：
1. 清空目標目錄（如存在）
2. 複製所需檔案（排除指定項目）
3. 生成精簡版 STATUS.md
4. 顯示建置結果
