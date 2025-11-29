fm,4bbp4# 銀行下載器功能盤點報告

> 更新日期：2024-11-29

## 概覽

| 項目 | 數量 |
|------|------|
| 支援銀行數 | 38 家 |
| 下載器數量 | 38 個 |
| 使用 Playwright | 38 個 |

## 下載方式分類

### 1. URL 直接下載 (`download_pdf_from_url`)

透過 Playwright 的 `page.request.get()` 直接下載 PDF，適用於 PDF URL 可直接存取的情況。

```python
def download_pdf_from_url(self, page, url, year, quarter):
    response = page.request.get(url)
    if response.status == 200:
        self.save_pdf(response.body(), year, quarter)
```

**使用此方式的銀行**：31 家

### 2. 點擊下載 (`download_pdf_by_click` / `expect_download`)

透過模擬點擊觸發下載，適用於需要 JavaScript 處理的下載連結。

```python
def download_pdf_by_click(self, page, locator, year, quarter):
    with page.expect_download() as download_info:
        locator.click()
    download = download_info.value
    download.save_as(file_path)
```

**使用此方式的銀行**：4 家

### 3. 特殊處理

部分銀行需要特殊處理：
- **新視窗**：透過 `page.expect_popup()` 處理
- **JavaScript 執行**：透過 `page.evaluate()` 執行
- **GraphQL API**：呼叫 GraphQL 端點取得 PDF URL
- **iframe**：切換至 iframe 內操作

---

## 各銀行下載器詳細說明

### 01. 臺灣銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 01 |
| 檔案 | `bank_01_bot.py` |
| URL | https://www.bot.com.tw/about/financial-statements/quarterly-report |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財報頁面
2. 搜尋 `app-document-download a` 元素
3. 找到標題包含「個體財務報告 {year}年{quarter_text}」的連結
4. 取得 href 屬性，組成完整 URL
5. 使用 `download_pdf_from_url` 下載

---

### 02. 臺灣土地銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 02 |
| 檔案 | `bank_02_landbank.py` |
| URL | https://www.landbank.com.tw/Category/Items/財務業務資訊-財報 |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財報頁面
2. 搜尋包含年度和季度的連結
3. 取得 PDF URL
4. 使用 `download_pdf_from_url` 下載

---

### 03. 合作金庫商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 03 |
| 檔案 | `bank_03_tcb.py` |
| URL | https://www.tcb-bank.com.tw/about-tcb/disclosure/bad-debt/asset-quality |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問資產品質頁面
2. 搜尋包含年度的連結
3. 取得 PDF URL
4. 使用 `download_pdf_from_url` 下載

---

### 04. 第一商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 04 |
| 檔案 | `bank_04_firstbank.py` |
| URL | https://www.firstbank.com.tw/sites/fcb/Statutory |
| 下載方式 | 點擊下載 |
| 特殊處理 | JavaScript 處理 |

**流程**：
1. 訪問法定公開揭露頁面
2. 點擊年度展開
3. 找到對應季度連結
4. 使用 `download_pdf_by_click` 點擊下載

---

### 05. 華南商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 05 |
| 檔案 | `bank_05_hncb.py` |
| URL | https://www.hnfhc.com.tw/HNFHC/ir/d.do |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問投資人關係頁面
2. 搜尋 PDF 連結
3. 使用 `download_pdf_from_url` 下載

---

### 06. 彰化商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 06 |
| 檔案 | `bank_06_chb.py` |
| URL | https://www.bankchb.com/frontend/finance.jsp |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財務資訊頁面
2. 搜尋包含年度季度的連結
3. 取得 PDF URL
4. 使用 `download_pdf_from_url` 下載

---

### 07. 上海商業儲蓄銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 07 |
| 檔案 | `bank_07_scsb.py` |
| URL | https://www.scsb.com.tw/content/about/about04_a_01.jsp |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問關於我們頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 08. 台北富邦銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 08 |
| 檔案 | `bank_08_fubon.py` |
| URL | https://www.fubon.com/banking/about/intro_FBB/Financial_status.htm |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 固定 URL 格式 |

**流程**：
1. 直接組成 PDF URL（固定格式）
2. 使用 `download_pdf_from_url` 下載

**URL 格式**：
```
https://www.fubon.com/banking/about/intro_FBB/pdf/{year}_{quarter}.pdf
```

---

### 09. 國泰世華商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 09 |
| 檔案 | `bank_09_cathay.py` |
| URL | https://www.cathaybk.com.tw/cathaybk/personal/about/news/announce/ |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問公告頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 10. 中國輸出入銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 10 |
| 檔案 | `bank_10_eximbank.py` |
| URL | https://www.eximbank.com.tw/zh-tw/FinanceInfo/Finance/Pages/default.aspx |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 政策性銀行，無消費金融 |

**流程**：
1. 訪問特定季度頁面
2. 搜尋 PDF 連結
3. 使用 `download_pdf_from_url` 下載

---

### 11. 高雄銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 11 |
| 檔案 | `bank_11_bok.py` |
| URL | https://www.bok.com.tw/-107 |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財報頁面
2. 搜尋對應年度季度連結
3. 使用 `download_pdf_from_url` 下載

---

### 12. 兆豐國際商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 12 |
| 檔案 | `bank_12_megabank.py` |
| URL | https://www.megabank.com.tw/about/announcement/news/regulatory-disclosures/finance-report |
| 下載方式 | URL 直接下載 |
| 特殊處理 | iframe 處理 |

**流程**：
1. 訪問財報頁面
2. 處理 iframe 內容
3. 搜尋 PDF 連結
4. 使用 `download_pdf_from_url` 下載

---

### 13. 花旗（台灣）銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 13 |
| 檔案 | `bank_13_citibank.py` |
| URL | https://www.citibank.com.tw/global_docs/chi/pressroom/financial_info/financial.htm |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財務資訊頁面
2. 搜尋包含年度季度的連結
3. 使用 `download_pdf_from_url` 下載

---

### 15. 王道商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 15 |
| 檔案 | `bank_15_obank.py` |
| URL | https://www.o-bank.com/common/regulation/regulation-financialreport |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問法規遵循頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 16. 臺灣中小企業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 16 |
| 檔案 | `bank_16_tbb.py` |
| URL | https://ir.tbb.com.tw/financial/quarterly-results |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問季度財報頁面
2. 搜尋對應季度連結
3. 使用 `download_pdf_from_url` 下載

---

### 17. 渣打國際商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 17 |
| 檔案 | `bank_17_scb.py` |
| URL | https://www.sc.com/tw/about-us/investor-relations/ |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 固定 URL 格式 |

**流程**：
1. 直接組成 PDF URL（固定格式）
2. 使用 `download_pdf_from_url` 下載

---

### 18. 台中商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 18 |
| 檔案 | `bank_18_taichungbank.py` |
| URL | https://www.tcbbank.com.tw/Site/intro/finReport/finReport.aspx |
| 下載方式 | JavaScript 執行 |
| 特殊處理 | 使用 JavaScript fetch 下載 |

**流程**：
1. 訪問財報頁面
2. 搜尋 PDF URL
3. 使用 `page.evaluate()` 執行 JavaScript fetch 下載

---

### 19. 京城商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 19 |
| 檔案 | `bank_19_ktb.py` |
| URL | https://customer.ktb.com.tw/new/about/8d88e237 |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問關於我們頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 20. 匯豐(台灣)商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 20 |
| 檔案 | `bank_20_hsbc.py` |
| URL | https://www.hsbc.com.tw/help/announcements/ |
| 下載方式 | URL 直接下載 |
| 特殊處理 | PDF 為掃描式，需 OCR |

**流程**：
1. 訪問公告頁面
2. 搜尋「{西元年}年{季度}重要財務業務資訊」連結
3. 使用 `download_pdf_from_url` 下載

**注意**：下載的 PDF 為掃描圖片格式，解析需使用 OCR。

---

### 21. 瑞興商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 21 |
| 檔案 | `bank_21_taipeistarbank.py` |
| URL | https://www.taipeistarbank.com.tw/StatutoryDisclosure/FinancialReports |
| 下載方式 | URL 直接下載 |
| 特殊處理 | PDF 為掃描式，需 OCR |

**流程**：
1. 訪問財報頁面
2. 搜尋表格中的連結
3. 使用 `download_pdf_from_url` 下載

**注意**：下載的 PDF 為掃描圖片格式，解析需使用 OCR。

---

### 22. 華泰商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 22 |
| 檔案 | `bank_22_hwataibank.py` |
| URL | https://www.hwataibank.com.tw/public/public02-01/ |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問公開資訊頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 23. 臺灣新光商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 23 |
| 檔案 | `bank_23_skbank.py` |
| URL | https://www.skbank.com.tw/QFI |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問季度財務資訊頁面
2. 搜尋對應季度連結
3. 使用 `download_pdf_from_url` 下載

---

### 24. 陽信商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 24 |
| 檔案 | `bank_24_sunnybank.py` |
| URL | https://www.sunnybank.com.tw/net/Page/Smenu/4 |
| 下載方式 | 點擊下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問公開資訊頁面
2. 搜尋 `/public/pdf/{year}年第{quarter}季.pdf` 格式連結
3. 使用 `expect_download` 點擊下載

**URL 格式**：
- Q1-Q3: `/public/pdf/{year}年第{quarter}季.pdf`
- Q4: `/public/pdf/{year}年度公開說明書.pdf`

---

### 25. 板信商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 25 |
| 檔案 | `bank_25_bop.py` |
| URL | https://www.bop.com.tw/Footer/Financial_Report |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財報頁面
2. 搜尋對應季度連結
3. 使用 `download_pdf_from_url` 下載

---

### 26. 三信商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 26 |
| 檔案 | `bank_26_cotabank.py` |
| URL | https://www.cotabank.com.tw/web/public/expose/#tab-財務業務資訊 |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問公開資訊頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 27. 聯邦商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 27 |
| 檔案 | `bank_27_ubot.py` |
| URL | https://www.ubot.com.tw/investors |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 新視窗處理 |

**流程**：
1. 訪問投資人關係頁面
2. 點擊連結開啟新視窗
3. 在新視窗中搜尋 PDF URL
4. 使用 `download_pdf_from_url` 下載

---

### 28. 遠東國際商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 28 |
| 檔案 | `bank_28_feib.py` |
| URL | https://www.feib.com.tw/detail?id=349 |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問詳情頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 29. 元大商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 29 |
| 檔案 | `bank_29_yuantabank.py` |
| URL | https://www.yuantabank.com.tw/bank/bulletin/statutoryDisclosure/list.do |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問法定公開揭露頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 30. 永豐商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 30 |
| 檔案 | `bank_30_sinopac.py` |
| URL | https://bank.sinopac.com/sinopacBT/about/investor/financial-statement.html |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 新視窗處理 |

**流程**：
1. 訪問財報頁面
2. 點擊連結開啟新視窗
3. 在新視窗中取得 PDF URL
4. 使用 `download_pdf_from_url` 下載

---

### 31. 玉山商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 31 |
| 檔案 | `bank_31_esunbank.py` |
| URL | https://doc.twse.com.tw/server-java/t57sb01 |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 使用證交所公開資訊觀測站 |

**流程**：
1. 訪問證交所公開資訊觀測站
2. 提交表單搜尋玉山銀行 (代碼 5847)
3. 取得 PDF URL
4. 使用 `download_pdf_from_url` 下載

---

### 32. 凱基商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 32 |
| 檔案 | `bank_32_kgibank.py` |
| URL | https://www.kgibank.com.tw/zh-tw/about-us/financial-summary |
| 下載方式 | URL 直接下載 |
| 特殊處理 | JavaScript 處理 |

**流程**：
1. 訪問財務摘要頁面
2. 根據年份組成 PDF URL
3. 使用 `download_pdf_from_url` 下載

---

### 33. 星展(台灣)商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 33 |
| 檔案 | `bank_33_dbs.py` |
| URL | https://www.dbs.com.tw/personal-zh/legal-disclaimers-and-announcements.page |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 固定 URL 格式 |

**流程**：
1. 根據年份組成 PDF URL
2. 使用 `download_pdf_from_url` 下載

---

### 34. 台新國際商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 34 |
| 檔案 | `bank_34_taishinbank.py` |
| URL | https://www.taishinbank.com.tw/TSB/about-taishin/brief-introduction-to-the-bank/financeInfo |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問財務資訊頁面
2. 搜尋對應季度連結
3. 使用 `download_pdf_from_url` 下載

---

### 36. 安泰商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 36 |
| 檔案 | `bank_36_entiebank.py` |
| URL | https://www.entiebank.com.tw/entie/disclosure-financial |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問公開揭露頁面
2. 搜尋財報連結
3. 使用 `download_pdf_from_url` 下載

---

### 37. 中國信託商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 37 |
| 檔案 | `bank_37_ctbc.py` |
| URL | https://www.ctbcbank.com |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 固定 URL 格式 |

**流程**：
1. 直接組成 PDF URL（固定格式）
2. 使用 `download_pdf_from_url` 下載

**URL 格式**：
```
https://www.ctbcbank.com/content/dam/twrbo/pdf/aboutctbc/{year}Q{quarter}_CTBC.pdf
```

---

### 38. 樂天國際商業銀行

| 項目 | 內容 |
|------|------|
| 代碼 | 38 |
| 檔案 | `bank_38_rakutenbank.py` |
| URL | https://www.rakuten-bank.com.tw/portal/other/disclosure |
| 下載方式 | 點擊下載 |
| 特殊處理 | GraphQL API |

**流程**：
1. 呼叫 GraphQL API 取得文件列表
2. 搜尋對應季度的 PDF
3. 轉換 URL 格式
4. 使用 `expect_download` 下載

**特殊說明**：
- GraphQL API 返回 `cmspv.rakuten-bank.com.tw:9443/file/xxx.pdf`
- 實際下載 URL 為 `www.rakuten-bank.com.tw/cms-upload/file/xxx.pdf`

---

### 40. 連線商業銀行 (LINE Bank)

| 項目 | 內容 |
|------|------|
| 代碼 | 40 |
| 檔案 | `bank_40_linebank.py` |
| URL | https://corp.linebank.com.tw/zh-tw/company-financial |
| 下載方式 | URL 直接下載 |
| 特殊處理 | 無 |

**流程**：
1. 訪問公司財務頁面
2. 搜尋對應季度連結
3. 使用 `download_pdf_from_url` 下載

---

### 41. 將來商業銀行 (Next Bank)

| 項目 | 內容 |
|------|------|
| 代碼 | 41 |
| 檔案 | `bank_41_nextbank.py` |
| URL | https://www.nextbank.com.tw/disclosures/download/... |
| 下載方式 | URL 直接下載 |
| 特殊處理 | JavaScript 頁面 |

**流程**：
1. 訪問公開揭露頁面
2. 搜尋對應季度連結
3. 使用 `download_pdf_from_url` 下載

---

## 統計摘要

### 按下載方式分類

| 下載方式 | 數量 | 銀行代碼 |
|----------|------|----------|
| URL 直接下載 | 31 | 01-03, 05-17, 19-23, 25-37, 40-41 |
| 點擊下載 | 4 | 04, 24, 38 |
| JavaScript 特殊處理 | 3 | 04, 18, 32 |

### 需要特殊處理的銀行

| 特殊處理 | 銀行 |
|----------|------|
| GraphQL API | 38 樂天國際商業銀行 |
| iframe | 12 兆豐國際商業銀行 |
| 新視窗 | 27 聯邦商業銀行, 30 永豐商業銀行 |
| 證交所查詢 | 31 玉山商業銀行 |
| OCR 解析 | 20 匯豐(台灣)商業銀行, 21 瑞興商業銀行 |

### 固定 URL 格式的銀行

| 銀行 | URL 格式 |
|------|----------|
| 08 台北富邦銀行 | `/pdf/{year}_{quarter}.pdf` |
| 17 渣打國際商業銀行 | 固定格式 |
| 33 星展(台灣)商業銀行 | 固定格式 |
| 37 中國信託商業銀行 | `/aboutctbc/{year}Q{quarter}_CTBC.pdf` |

---

## 注意事項

1. **銀行代碼 14, 35, 39 不存在**：這些代碼未分配給任何銀行。

2. **PDF 格式**：
   - 大多數銀行提供文字型 PDF，可直接解析
   - 匯豐(台灣)商業銀行 (20) 和瑞興商業銀行 (21) 提供掃描式 PDF，需使用 OCR

3. **網站更新**：銀行官網可能隨時更新，若下載失敗需檢查：
   - 網站結構是否變更
   - URL 格式是否變更
   - 新季度資料是否已上線

4. **錯誤處理**：所有下載器都有錯誤處理機制，會返回適當的狀態碼：
   - `SUCCESS`: 下載成功
   - `ALREADY_EXISTS`: 檔案已存在
   - `NO_DATA`: 該季度尚無資料
   - `ERROR`: 下載錯誤
