"""
台中商業銀行 (18) - Taichung Commercial Bank
網址: https://www.tcbbank.com.tw/Site/intro/finReport/finReport.aspx
"""
from .base import BaseBankDownloader, DownloadResult, DownloadStatus
from playwright.sync_api import Page


class TaichungBankDownloader(BaseBankDownloader):
    """台中商業銀行下載器"""
    
    bank_name = "台中商業銀行"
    bank_code = 18
    bank_url = "https://www.tcbbank.com.tw/Site/intro/finReport/finReport.aspx"
    headless = True  # 預設無頭模式，失敗時自動重試有頭模式
    
    def _number_to_chinese_year(self, year: int) -> str:
        """將民國年轉換為中文年度，例如 114 -> 一百一十四"""
        chinese_digits = {
            0: '零', 1: '一', 2: '二', 3: '三', 4: '四',
            5: '五', 6: '六', 7: '七', 8: '八', 9: '九'
        }
        
        if year >= 100:
            hundred = year // 100
            remainder = year % 100
            
            result = chinese_digits[hundred] + '百'
            
            if remainder == 0:
                pass  # 整百，不需要加零
            elif remainder < 10:
                result += '零' + chinese_digits[remainder]
            else:
                ten = remainder // 10
                one = remainder % 10
                if ten == 1:
                    result += '一十'
                else:
                    result += chinese_digits[ten] + '十'
                if one > 0:
                    result += chinese_digits[one]
            
            return result
        else:
            # 小於 100 的處理
            if year < 10:
                return chinese_digits[year]
            else:
                ten = year // 10
                one = year % 10
                result = chinese_digits[ten] + '十'
                if one > 0:
                    result += chinese_digits[one]
                return result
    
    def _download(self, page: Page, year: int, quarter: int) -> DownloadResult:
        quarter_text = self.get_quarter_text(quarter)
        
        # 將民國年轉為中文，例如 114 -> 一百一十四
        chinese_year = self._number_to_chinese_year(year)
        year_title = f"{chinese_year}年度"  # 例如：一百一十四年度
        
        # 季度對應文字
        quarter_names = {
            1: "第一季",
            2: "第二季",
            3: "第三季",
            4: "第四季"
        }
        target_quarter = quarter_names[quarter]
        
        # 前往財報頁面
        page.goto(self.bank_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # 在 table tbody 中找到對應年度的 tr
        pdf_url = None
        
        # 找所有 tr 元素
        tr_elements = page.locator("table tbody tr").all()
        
        for tr in tr_elements:
            # 找 tr > td
            td = tr.locator("td").first
            if td.count() == 0:
                continue
            
            # td 底下有多個 div
            # 第一個 div 中有一個 div.year-title
            # 第二個 div 包含季度下載
            td_divs = td.locator("> div").all()
            
            if len(td_divs) < 2:
                continue
            
            # 第一個 div 中找 year-title
            first_div = td_divs[0]
            year_title_div = first_div.locator("div[class*='year-title']")
            
            if year_title_div.count() == 0:
                continue
            
            year_text = year_title_div.first.inner_text().strip()
            
            if year_title not in year_text:
                continue
            
            # 找到對應年度，現在找第二個 div（包含季度下載連結）
            quarters_div = td_divs[1]
            
            # 找各季度的 div
            quarter_divs = quarters_div.locator("> div").all()
            
            for q_div in quarter_divs:
                q_text = q_div.inner_text().strip()
                
                if target_quarter in q_text:
                    # 找到目標季度，取得 a 元素
                    a_elements = q_div.locator("a").all()
                    
                    if len(a_elements) >= 1:
                        # 如果有多個 a 元素，使用第一個
                        href = a_elements[0].get_attribute("href")
                        if href:
                            if href.startswith("http"):
                                pdf_url = href
                            else:
                                pdf_url = f"https://www.tcbbank.com.tw{href}"
                            break
            
            if pdf_url:
                break
        
        if not pdf_url:
            return DownloadResult(
                status=DownloadStatus.NO_DATA,
                message=f"找不到 {year}年{quarter_text} ({year_title} {target_quarter}) 的下載連結"
            )
        
        # 導向 PDF URL 並使用 JavaScript fetch 下載
        try:
            self.ensure_dir(year, quarter)
            file_path = self.get_file_path(year, quarter)
            
            # 先導向 PDF URL
            page.goto(pdf_url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            
            # 使用 JavaScript fetch 取得 PDF 內容 (以 base64 形式)
            import base64
            result = page.evaluate('''
                async () => {
                    try {
                        const response = await fetch(window.location.href);
                        const blob = await response.blob();
                        const reader = new FileReader();
                        return new Promise((resolve, reject) => {
                            reader.onloadend = () => resolve(reader.result);
                            reader.onerror = reject;
                            reader.readAsDataURL(blob);
                        });
                    } catch (e) {
                        return 'Error: ' + e.message;
                    }
                }
            ''')
            
            if result and result.startswith('data:'):
                # 提取 base64 部分並解碼
                base64_data = result.split(',')[1]
                content = base64.b64decode(base64_data)
                
                # 檢查是否為 PDF
                if content[:4] == b'%PDF':
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    
                    return DownloadResult(
                        status=DownloadStatus.SUCCESS,
                        message="下載成功",
                        file_path=file_path
                    )
                else:
                    return DownloadResult(
                        status=DownloadStatus.ERROR,
                        message="非 PDF 格式"
                    )
            else:
                return DownloadResult(
                    status=DownloadStatus.ERROR,
                    message=f"JavaScript fetch 失敗: {result[:100] if result else 'No result'}"
                )
        except Exception as e:
            return DownloadResult(
                status=DownloadStatus.ERROR,
                message=f"下載失敗: {str(e)}"
            )
