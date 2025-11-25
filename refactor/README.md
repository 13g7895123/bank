# 銀行財報下載重構版 - 使用 Playwright

本資料夾包含使用 Playwright 重構的銀行財報下載功能。

## 結構

```
refactor/
├── __init__.py
├── downloader.py      # 主下載器類別
├── banks/             # 各銀行下載模組
│   ├── __init__.py
│   ├── base.py        # 銀行下載基礎類別
│   ├── bank_01_bot.py         # 臺灣銀行
│   ├── bank_02_landbank.py    # 臺灣土地銀行
│   ├── ...
│   └── bank_41_nextbank.py    # 將來商業銀行
├── test_all.py        # 測試所有銀行
└── README.md
```

## 使用方式

```python
from refactor.downloader import BankDownloader

downloader = BankDownloader()
result = downloader.download("臺灣銀行", year=114, quarter=1)
```

## 優點

1. 使用 Playwright 取代 Selenium，更穩定且快速
2. 模組化設計，每家銀行獨立檔案，易於維護
3. 統一的錯誤處理和日誌記錄
4. 無需 Proxy 設定
