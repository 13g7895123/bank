import os
import requests
import time
from requests.packages import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def downloadData(name, value, year_check, quarter_check):
    if os.path.isfile(f'data/{year_check}Q{quarter_check}/{value}_{name}_{year_check}Q{quarter_check}.pdf'):
        print("exist")
        return 2
    else:
        # set proxy to make sure access the website successfully
        proxy = "XX.XX.X.XX:XXXXs"
        proxies = {
            "http": "http://" + proxy,
            "https": "http://" + proxy,
        }

    if quarter_check == 1:
            quarter_text = "第一季"
    elif quarter_check == 2:
            quarter_text = "第二季"
    elif quarter_check == 3:
            quarter_text = "第三季"
    elif quarter_check == 4:
            quarter_text = "第四季"

    options = Options()
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--headless")
    options.add_argument('--disable-gpu')
    options.page_load_strategy = 'eager'

        
    if name == '臺灣銀行':
        domain = "https://www.bot.com.tw"
        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/about/financial-statements/quarterly-report")
        time.sleep(5)
        content = BeautifulSoup(edge.page_source, "html5lib")

        table = content.find("app-document-download", class_="ng-star-inserted").find_all("div", class_="ng-star-inserted")
        check = 0
        for i in range(0, len(table)):
            if table[i].find("a") is not None:
                if f"個體財務報告 {year_check}年{quarter_text}" in table[i].find("a").get("title"):
                    link = table[i].find("a").get("href")
                    check = 1
                    break

        if check == 0:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check
        response = requests.get(f"{domain}/{link}", proxies=proxies)

    if name == '臺灣土地銀行':
        domain = "https://www.landbank.com.tw"
        response = requests.get(f"{domain}/Category/Items/財務業務資訊-財報", proxies=proxies)

        content = BeautifulSoup(response.text, "html.parser")
        table = content.find("table", summary="資產品質年度季報表").find("tr")  # get the table of data's year & quarter on the website

        year = int(table.text.split('年')[0])
        quarter = len(table.text.split()) - 1

        if (year != year_check) or (quarter != quarter_check):  # check whether the data we want is out or not
            return -1

        link = table.select("td")[quarter - 1].select_one("a").get("href")
        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == '合作金庫商業銀行':
        domain = "https://www.tcb-bank.com.tw"
        response = requests.get(f"{domain}/about-tcb/disclosure/bad-debt/asset-quality", proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find_all("li", class_="c-list__item")

        check = 0
        for i in range(0, len(table)):
            if f"{year_check}" in table[i].find("div", class_="c-list__title").getText() and quarter_text in table[i].find("div", class_="c-list__title").getText():
                check = 1
                link = table[i].find("a").get("href")
                break

            if check == 0:
                print("尚無資料")
                return -1

        year = year_check
        quarter = quarter_check
        response = requests.get(f"{domain}/{link}", proxies=proxies)

    if name == '第一商業銀行':
        domain = "https://www.firstbank.com.tw"
        response = requests.get(f"{domain}/sites/fcb/Statutory", proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("tbody")

        try:
            target = table.find("td", string=f"{year_check}年度{quarter_text}銀行重要財務業務資訊之補充揭露")
            temp = target.find_next_siblings("td")
            link = temp[1].find("a").get("href")
            response = requests.get(f"{link}", proxies=proxies)
        except:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check

    if name == '華南商業銀行':
        domain = "https://www.hncb.com.tw"
        sub_domain = "footer/public_disclosure#id=42a0b44a-78ef-4656-98df-844841fbaed5-content"
        response = requests.get(f"{domain}/{sub_domain}#tab_20b54c86-d743-44b2-aafb-e35e2ab65229", proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        div = content.find_all("div", class_="tab-pane fade in active")  # Get the table of data's year & quarter

        step1 = div[1].find_all("a", class_="btn-square btn-content")
        quarter = int(len(step1) / 2)
        tag = step1[-2].get("href")
        id = tag.split("#")[1]

        response = requests.get(f"{domain}/{sub_domain}{tag}", proxies=proxies)
        content = BeautifulSoup(response.text, "html5lib")
        step2 = content.find("div", id=f"{id}").find("a", class_="btn btn-lg btn-danger btn-block")
        year = int(step2.get("title").split("Q")[0].split("報告 - ")[1])

        if (year != year_check) or (quarter != quarter_check):
            return -1

        link = step2.get("href")
        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == "彰化商業銀行":
        domain = "https://www.bankchb.com"
        response = requests.get(f"{domain}/frontend/finance.jsp", proxies=proxies)

        content = BeautifulSoup(response.text, "html.parser")
        step1 = content.find("ul", class_="ul-itemss")
        quarter = len(step1.find_all("li", class_="ul-li-itemss"))

        year = int(step1.find("a").getText().split("國")[1].split("年")[0])
        if (year != year_check) or (quarter != quarter_check):
            return -1

        tag = step1.find("a").get("href")
        response = requests.get(f"{domain}/frontend/{tag}", proxies=proxies)
        content = BeautifulSoup(response.text, "html.parser")
        link = content.find("a", class_="editor_link").get("href")
        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == "上海商業儲蓄銀行":
        domain = "https://www.scsb.com.tw"
        response = requests.get(f"{domain}/content/about/about04_a_01.jsp", proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        year = int(content.find("div", class_="titleBlk_a h4").getText().split("年")[0])

        if year == year_check:
            table = content.find("div", class_="list-group downloadLister")
            try:
                link = table.find("a", title=f"開新視窗({quarter_text})法定財務業務資訊(PDF)").get("href")
                response = requests.get(f"{domain}/content/about/{link}", proxies=proxies)
            except:
                print("尚無資料")
                return -1
        else:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check

    if name == "台北富邦銀行":
        domain = "https://www.fubon.com"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
            'Referer': 'https://www.fubon.com/banking/about/' }
                
        response = requests.get(
            f"{domain}/banking/document/about/intro_FBB/TW/{year_check}Q{quarter_check}.pdf",headers=headers,proxies=proxies)

        if (response.url != f"{domain}/banking/document/about/intro_FBB/TW/{year_check}Q{quarter_check}.pdf"):
            return -1

        year = year_check
        quarter = quarter_check

    if name == "國泰世華商業銀行":
        domain = "https://www.cathaybk.com.tw"
        response = requests.get(f"{domain}/cathaybk/personal/about/news/announce/",proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("div", class_="cubre-m-download")
        target = table.find(string=f"{year_check}年度 {quarter_text}財務報告")

        if (target is not None):
            link = table.find("div", class_="cubre-o-action__item").find("a").get("href")
            response = requests.get(f"{domain}{link}", proxies=proxies)
        else:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check

    if name == "中國輸出入銀行":
        domain = "https://www.eximbank.com.tw"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
                    'Referer': 'https://www.eximbank.com.tw/zh-tw/FinanceInfo/Finance/Pages/default.aspx'}

        urllib3.disable_warnings()
        response = requests.get(
        f"{domain}/zh-tw/FinanceInfo/Pages/FinanceReports.aspx?year={year_check}Q{quarter_check}",headers=headers,proxies=proxies,verify=False)

        content = BeautifulSoup(response.text, 'html5lib')
        table = content.find_all("ul", class_="row_list")[3]

        if (table.getText().strip() == ''):
            print("尚無資料")
            return -1
        year = year_check
        quarter = quarter_check
        link = content.find_all("ul", class_="row_list")[3].find("a").get("href")
        response = requests.get(f"{domain}{link}",headers=headers,proxies=proxies,verify=False)

    if name == "高雄銀行":
        domain = "https://www.bok.com.tw"
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
                    'Referer': 'https://www.bok.com.tw'}

        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/-107")
        time.sleep(3)

        content = BeautifulSoup(edge.page_source, "html5lib")
        table = content.find_all("li", class_="files-download-item")  # get the table of data's year & quarter
        item = table[1].find("a")
        year = int(item.getText().split("年")[0].split(" ")[1])

        if len(item.getText()) >= 15:
            if item.getText().split("第")[1].split("季")[0] == "一":
                quarter = 1
            elif item.getText().split("第")[1].split("季")[0] == "二":
                quarter = 2
            elif item.getText().split("第")[1].split("季")[0] == "三":
                quarter = 3
            else:
                quarter = 4

        if (year != year_check) or (quarter != quarter_check):  # check whether the data we want is out or not
            print("尚無資料")
            return -1

        link = item.get("href")
        print(year)
        print(link)

        for i in range(0, 5):  # 連線不穩定，讓它多試幾次
            try:
                response = requests.get(f"{link}",headers=headers,proxies=proxies,verify=False)
                print(response.status_code)
            except:
                continue

            if response.status_code == 200:
                break

    if name == "兆豐國際商業銀行":
        domain = "https://www.megabank.com.tw"
        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/about/announcement/legal-disclosure/finance-report")
        content = BeautifulSoup(edge.page_source, "html5lib")

        table = content.find("tbody").find_all("tr")[1]
        target = table.find("a").get("title")

        if f"{year_check}年度{quarter_text}" in target:
            link = table.find("a").get("href")
        else:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check

        edge.get(f"{domain}{link}")
        time.sleep(3)

        content = BeautifulSoup(edge.page_source, "html5lib")
        table = content.find_all("table", class_="borderall")[2]
        link = table.find_all("td")[1].find("a").get("href")

        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == "花旗（台灣）銀行":
        domain = "https://www.citibank.com.tw"
        response = requests.get(f"{domain}/global_docs/chi/pressroom/financial_info/financial.htm", proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("td", class_="1b")  # get the table of data's year & quarter
        year = int(table.getText().split("/")[2]) - 1911
        quarter = int(int(table.getText().split("/")[0]) / 3)

        if (year != year_check) or (quarter != quarter_check):  # check whether the data we want is out or not
            return -1

        link = table.find("a").get("href")
        response = requests.get(f"{domain}/global_docs/chi/pressroom/financial_info/{link}",proxies=proxies)

    if name == "王道商業銀行":
        domain = "https://www.o-bank.com"
        response = requests.get(f"{domain}/common/regulation/regulation-financialreport",proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("ul", class_="w3-ul o-ul ul-2")  # get the table of data's year & quarter
        year = int(table.find_all("li")[0].getText().split()[0]) - 1911
        quarter = len(table.find_all("li"))

        if (year != year_check) or (quarter != quarter_check):
            return -1

        link = table.find_all("li")[0].find("a").get("href")
        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == "臺灣中小企業銀行":
        domain = "https://www.tbb.com.tw"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
                    'Referer': 'https://www.tbb.com.tw/web/guest/-/468/'}

        options.add_argument('--disable-blink-features=AutomationControlled')
        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/web/guest/-/468")
        time.sleep(6)

        content = BeautifulSoup(edge.page_source, "html5lib")

        if quarter_check == 4:
            quarter_text = "度"

        check = -1
        
        table = content.find("div", class_="l-download u-mb-4").find_all("a")
        for i in range(0, 4):
            if f"{year_check}" in table[i].get("title") and f"{quarter_text}" in table[i].get("title"):
                link = table[i].get("href")
                year = year_check
                quarter = quarter_check
                check = 1
                break

        if check != 1:
            print("尚無資料")
            return -1

        response = requests.get(f"{domain}{link}", headers=headers, proxies=proxies, verify=False)

    if name == "渣打國際商業銀行":
        domain = "https://av.sc.com"

        if (quarter_check == 1) or (quarter_check == 3):
            response = requests.get(f"{domain}/tw/content/docs/tw-fi-{year_check}q{quarter_check}.pdf", proxies=proxies)
        
        else:
            response = requests.get(f"{domain}/tw/content/docs/tw-earnings-{year_check}_h{quarter_check//2}.pdf",proxies=proxies)

        if response.status_code != 200:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check
    
    if name =="台中商業銀行" :
        domain ="https://www.tcbbank.com.tw"
        headers= {'user-Agent':'Mozilla/5.0(Windows NT10.0;Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/103.0.506.134 Safari/ 537.36 Edg/103.0.1264.71'
                 'Regerer:''https://www.tcbbank.com.tw/Intro/.B_01.html'}
        
        year = year_check
        quarter = quarter_check
        month = quarter*3
        if month < 10:
            month = str(month)
            month = '0'+ month
        else:
            month = str(month)
        
        response =requests.get(f"{domain}/tw/content/docs/tw-earnings-{year_check}_h{quarter_check//2}.pdf",proxies=proxies)

        if (response.status_code == 404):
            return -1

    if name == "京城商業銀行":
        domain = "https://customer.ktb.com.tw"
        response = requests.get(f"{domain}/new/about/8d88e237", proxies=proxies)
        content = BeautifulSoup(response.text, "html5lib")
        year = int(content.find("div", class_="ktbcontent").find("h3").getText().split("年")[0])
        table = content.find("table", class_="tftable")

        if (table.find_all("tr")[-quarter_check].find_all("td")[1].find_all("a") == []) or year != year_check:
            return -1

        quarter = quarter_check
        link = table.find_all("tr")[-quarter].find_all("td")[1].find("a").get("href")
        response = requests.get(f"{link}", proxies=proxies)

    if name == "匯豐(台灣)商業銀行":
        domain = "https://www.hsbc.com.tw"

        response = requests.get(f"{domain}/help/announcements/", proxies=proxies)
        content = BeautifulSoup(response.text, "html.parser")

        # 民國轉西元 (但不要覆蓋原本 year_check)
        year_check_ad = year_check + 1911  

        table = content.find_all("div", class_="O-SMARTSPCGEN-DEV M-CONTMAST-RW-RBWM links")
        title = table[3].find("a").get("data-event-name")

        if f"{year_check_ad}" in title and quarter_text in title:
            link = table[3].find("a").get("href")
            year = year_check
            quarter = quarter_check
        else:
            print("尚無資料")
            return -1

        response = requests.get(f"{link}", proxies=proxies)


    if name == "瑞興商業銀行":
        domain = "https://www.taipeistarbank.com.tw"
        response = requests.get(f"{domain}/StatutoryDisclosure/FinancialReports", proxies=proxies)
        content = BeautifulSoup(response.text, "html.parser")
        table = content.find("tbody").find_all("td", class_="tb_td")

        check = 0
        for td in table:
            title = td.find("a").getText()
            if f"{year_check}" in title and f"{quarter_text}" in title:
                year = year_check
                quarter = quarter_check
                link = td.find("a").get("href")
                check = 1
                break

        if check != 1:
            print("尚無資料")
            return -1

        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == "華泰商業銀行":
        domain = "https://www.hwataibank.com.tw"
        response = requests.get(f"{domain}/public/public02-01/", proxies=proxies)
        content = BeautifulSoup(response.text, "html5lib")
        table = content.find_all("div", class_="elementor-button-wrapper")  # 每個按鈕區塊

        check = 0
        for i in range(len(table)):
            a_tag = table[i].find("a")
            if a_tag:
                title = a_tag.get("title", "")
                if f"{year_check}" in title and f"{quarter_text}" in title:
                    link = a_tag.get("href")
                    year = year_check
                    quarter = quarter_check
                    check = 1
                    break

        if check != 1:
            print("尚無資料")
            return -1

        response = requests.get(f"{domain}{link}", proxies=proxies)

    if name == "臺灣新光商業銀行":
        domain = "https://www.skbank.com.tw"

        response = requests.get(f"{domain}/789.html", proxies=proxies)
        response.encoding = 'utf-8'
        content = BeautifulSoup(response.text, "html5lib")

        target = content.find("li", class_="control_me_li")
        title = target.get_text(strip=True)

        if f"{year_check}" in title and quarter_text in title:  # 檢查是否有該年度/季度資料
            step1 = target.find("a").get("href")
            if not step1.startswith("http"):
                step1 = f"{domain}{step1}"
            year = year_check
            quarter = quarter_check
        else:
            print("尚無資料")
            return -1

        response = requests.get(step1, proxies=proxies)
        response.encoding = 'utf-8'
        content = BeautifulSoup(response.text, "html5lib")

        if (quarter == 1) or (quarter == 3):
            link = content.find_all("li", class_="control_me_li")[6].find("a").get("href")
        elif (quarter == 2) or (quarter == 4):
            link = content.find("ol", class_="sena").find_all("li")[-1].find("a").get("href")

        if not link.startswith("http"):
            link = f"{domain}{link}"

        response = requests.get(link, proxies=proxies)

    if name == "陽信商業銀行":
        domain = "https://www.sunnybank.com.tw"

        response = requests.get(f"{domain}/net/Page/Smenu/4", proxies=proxies)
        content = BeautifulSoup(response.text, "html5lib")

        table = content.find("table", class_="table table-borderless")
        year_text = table.find("span").get_text(strip=True)
        target = table.find_all("a")
        check = 0

        if f"{year_check}" in year_text:
            for a in target:
                title = a.get_text(strip=True)
                if f"{quarter_text}" in title:
                    year = year_check
                    quarter = quarter_check
                    link = a.get("href")
                    if not link.startswith("http"):
                        link = f"{domain}{link}"
                    check = 1
                    break

        if check != 1:
            print("尚無資料")
            return -1

        response = requests.get(link, proxies=proxies)
        response.encoding = 'utf-8'
        content = BeautifulSoup(response.text, "html5lib")

        table = content.find("tbody").find("tr").find_all("td")
        year_text = table[0].get_text(strip=True)

        if f"{year_check}" in year_text and table[quarter_check].find("a") is not None:
            year = year_check
            quarter = quarter_check
            link = table[quarter_check].find("a").get("href")
            if not link.startswith("http"):
                link = f"{domain}{link}"
        else:
            print("尚無資料")
            return -1

        response = requests.get(link, proxies=proxies)

    if name == "板信商業銀行":
        domain = "https://www.bop.com.tw"

        response = requests.get(f"{domain}/Footer/Financial_Report?tni=110&refid=null", proxies=proxies)
        content = BeautifulSoup(response.text, "html5lib")

        table = content.find_all("table", class_="table table-hover")[1].find("tbody")
        target = table.find("tr").find_all("td")

        year_text = target[0].get_text(strip=True)
        a_tag = target[quarter_check].find("a")

        if f"{year_check}" in year_text and a_tag is not None:
            year = year_check
            quarter = quarter_check
            link = a_tag.get("href")
            if not link.startswith("http"):
                link = f"{domain}/{link.lstrip('/')}"
        else:
            print("尚無資料")
            return -1

        response = requests.get(link, proxies=proxies)


    if name == "三信商業銀行":
        domain = "https://www.cotabank.com.tw"

        response = requests.get(f"{domain}/web/public/expose/#tab-財務業務資訊", proxies=proxies)
        response.encoding = 'utf-8'

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("tbody").find("tr").find_all("td")

        year_text = table[0].get_text(strip=True)
        a_tag = table[quarter_check].find("a")

        if f"{year_check}" in year_text and a_tag is not None:
            year = year_check
            quarter = quarter_check
            link = a_tag.get("href")
            if not link.startswith("http"):
                link = f"{domain}{link}"
        else:
            print("尚無資料")
            return -1

        response = requests.get(link, proxies=proxies)



    if name == "聯邦商業銀行":
        domain = "https://www.ubot.com.tw"
        edge = webdriver.Edge(options=options)

        try:
            edge.get(f"{domain}/businessmsg")
            # 等待 tbody 出現，最多等 10 秒
            WebDriverWait(edge, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )

            content = BeautifulSoup(edge.page_source, "html5lib")
            table = content.find("tbody").find_all("tr")
            td_tag = table[quarter_check].find("td")
            a_tag = td_tag.find("a") if td_tag else None

            if a_tag is None:
                print("尚無資料")
                return -1

            year = year_check
            quarter = quarter_check
            link = a_tag.get("href")
            if not link.startswith("http"):
                link = f"{domain}{link}"

            response = requests.get(link, proxies=proxies)
        finally:
            edge.quit()



    if name == "遠東國際商業銀行":
        domain = "https://www.feib.com.tw"

        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/detail?id=349")
        time.sleep(6)

        content = BeautifulSoup(edge.page_source, "html5lib")
        target = content.find_all("select")[1].find_all("option")[-1]

        if f"{year_check}" in target.getText() and quarter_text in target.getText():
            year = year_check
            quarter = quarter_check
            link = target.get("value")
        else:
            print("尚無資料")
            return -1

        response = requests.get(f"{domain}{link}", proxies=proxies)


    if name == "元大商業銀行":
        domain = "https://www.yuantabank.com.tw"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
            'Referer': 'https://www.yuantabank.com.tw/bank/bulletin/statutoryDisclosure/list.do'
        }

        if quarter_check % 2 == 0:
            response = requests.get(
                f"{domain}/bank/bulletin/statutoryDisclosure/list.do?layer_id=26a83777c500000745d9",
                headers=headers,
                proxies=proxies
            )
            quarter_text = "上半年" if quarter_check == 2 else "年度個體"
        else:
            response = requests.get(
                f"{domain}/bank/bulletin/statutoryDisclosure/list.do?layer_id=26a836f2b60000019f0b",
                headers=headers,
                proxies=proxies
            )

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("div", class_="news")
        target = table.find_all("li")

        found = False
        for i in range(min(4, len(target))):
            a_text = target[i].find("a").getText()
            if f"{year_check}" in a_text and quarter_text in a_text:
                year = year_check
                quarter = quarter_check
                link = target[i].find("a").get("href")
                found = True
                break

        if not found:
            print("尚無資料")
            return -1

        response = requests.get(f"{link}", headers=headers, proxies=proxies)


    if name == "永豐商業銀行":
        domain = "https://bank.sinopac.com"

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.page_load_strategy = 'eager'
        edge = webdriver.Edge(options=options)

        try:
            edge.get(f"{domain}/sinopacBT/about/investor/financial-statement.html")
            time.sleep(5)
            edge.refresh()
            time.sleep(6)

            content = BeautifulSoup(edge.page_source, "html5lib")
            year = year_check + 1911

            table = content.find("ul", class_="sheet-list")
            target = table.find_all("a")
            check = 0

            for i in range(len(target)):
                text = target[i].getText()
                if quarter_check % 2 == 1 and f"{year}" in text and quarter_text in text and "合併財報" in text:
                    check = 1
                    break
                elif quarter_check % 2 == 0 and f"{year}" in text and quarter_text in text and "個體財報" in text:
                    check = 1
                    break

            if check == 0:
                print("尚無資料")
                return -1

            year = year_check
            quarter = quarter_check
            link = target[i].get("href")

            response = requests.get(f"{domain}{link}", proxies=proxies)
        finally:
            edge.quit()


    if name == "玉山商業銀行":
        domain = "https://doc.twse.com.tw"

        response = requests.get(
            f"{domain}/server-java/t57sb01?step=1&colorchg=1&co_id=5847&year={year_check}&seamon=&mtype=A&",
            proxies=proxies
        )

        content = BeautifulSoup(response.text, "html5lib")
        check = content.find("form")
        if check is None:
            print("尚無資料")
            return -1

        table = content.find_all("tbody")[1].find_all("tr")
        check_flag = 0
        for i in range(1, len(table)):
            target = table[i].find_all("td")
            text_quarter = target[1].getText()
            report_type = target[5].getText()

            if quarter_check % 2 == 1 and quarter_text in text_quarter and report_type == "IFRSs合併財報":
                file = target[7].getText()
                check_flag = 1
                break
            elif quarter_check % 2 == 0 and quarter_text in text_quarter and report_type == "IFRSs個體財報":
                file = target[7].getText()
                check_flag = 1
                break

        if check_flag != 1:
            print("尚無資料")
            return -1

        year = year_check
        quarter = quarter_check

        response = requests.get(
            f"{domain}/server-java/t57sb01?step=9&colorchg=1&kind=A&co_id=5847&filename={file}",
            proxies=proxies
        )

        content = BeautifulSoup(response.text, "html5lib")
        link = content.find("a").get("href")

        response = requests.get(f"{domain}{link}", proxies=proxies)

        

    if name == "凱基商業銀行":
        domain = "https://www.kgibank.com.tw"

        edge = webdriver.Edge(options=options)
        try:
            edge.get(f"{domain}/zh-tw/about-us/financial-summary")
            time.sleep(6)
            content = BeautifulSoup(edge.page_source, "html5lib")

            ad = year_check + 1911
            table = content.find_all("div", class_="slick-track")[1].find("div", class_="row")
            year_divs = table.find_all("div", class_="h3 ml-16")
            target_links = table.find_all("a")

            check_flag = 0
            for i in range(len(target_links)):
                year_text = year_divs[i].getText()
                if f"{ad}" in year_text and quarter_text in year_text:
                    if quarter_check % 2 == 1 and "合併財務報告" in year_text:
                        link = target_links[i].get("href")
                        check_flag = 1
                    elif quarter_check % 2 == 0 and "非合併財務報告" in year_text:
                        link = target_links[i].get("href")
                        check_flag = 1

                if check_flag == 1:
                    break

            if check_flag == 0:
                print("尚無資料")
                return -1

            year = year_check
            quarter = quarter_check

            response = requests.get(f"{domain}{link}", proxies=proxies)
        finally:
            edge.quit()

            
    if name == "星展(台灣)商業銀行":
        domain = "https://www.dbs.com.tw"

        # 依季度設定文字
        if quarter_check == 1:
            quarter_text = "1季"
        elif quarter_check == 2:
            quarter_text = "2季"
        elif quarter_check == 3:
            quarter_text = "3季"
        elif quarter_check == 4:
            quarter_text = "4季"

        edge = webdriver.Edge(options=options)
        try:
            edge.get(f"{domain}/personal-zh/legal-disclaimers-and-announcements.page")
            time.sleep(6)

            content = BeautifulSoup(edge.page_source, "lxml")
            table = content.find_all("div", class_="sc-1ebj2bl dpxttY")[3]

            # 根據季度選擇目標 a 標籤
            if quarter_check % 2 == 1:
                target = table.find("a", string=f"{year_check+1911}年{quarter_text}")
            else:
                if quarter_check == 2:
                    target = table.find("a", string=f"{year_check+1911}年06月")
                else:
                    target = table.find("a", string=f"{year_check+1911}年12月")

            if target is not None:
                link = target.get("href")
            else:
                print("尚無資料")
                return -1

            year = year_check
            quarter = quarter_check
            response = requests.get(f"{domain}{link}", proxies=proxies)
        finally:
            edge.quit()


    if name == "台新國際商業銀行":
        domain = "https://www.taishinbank.com.tw"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
            'Referer': 'https://www.taishinbank.com.tw/TSB/about-taishin/'
        }

        response = requests.get(
            f"{domain}/TSB/about-taishin/brief-introduction-to-the-bank/financeInfo",
            headers=headers,
            proxies=proxies
        )

        content = BeautifulSoup(response.text, "html5lib")
        table = content.find("div", class_="ts-comp-076 btn-two")
        year_divs = table.find_all("div", class_="text-block")
        target_divs = table.find_all("div", class_="btnnn")
        ad = year_check + 1911

        check = 0
        for i in range(len(target_divs)):
            if f"{ad}" in year_divs[i].getText() and f"Q{quarter_check}" in year_divs[i].getText():
                if "財務業務資訊" in year_divs[i].getText():
                    year = year_check
                    quarter = quarter_check
                    link = target_divs[i].find("a").get("href")
                    check = 1
                    break

        if check == 0:
            print("尚無資料")
            return -1

        response = requests.get(f"{domain}{link}", headers=headers, proxies=proxies)

    # if name == "日盛國際商業銀行":
    #     domain = "https://www.jihsunbank.com.tw"
    #     response = requests.get(f"{domain}/newsite/login/money/{year_check}-{quarter_check}.pdf",
    #                             proxies=proxies)
    #     if (response.status_code != 200):
    #         return -1
    #     else:
    #         year = year_check
    #         quarter = quarter_check

    if name == "安泰商業銀行":

        domain = "https://www.entiebank.com.tw"

        options.add_argument('--window-size=1920,1080')
        edge = webdriver.Edge(options=options)

        edge.get(f"{domain}/entie/disclosure-financial")
        time.sleep(6)

        edge.find_elements(By.CLASS_NAME, "tabsTitleName")[1].click()
        time.sleep(2)
        content = BeautifulSoup(edge.page_source, "html5lib")

        table = content.find("tbody").find_all("tr")[1].find_all("td")
        year = content.find("tbody").find_all("tr")[0].getText()

        check = 0
        for i in range(0, len(table)):
            if (f"{year_check}" in year 
                and quarter_text in table[i].find("a").getText()):
                year = year_check
                quarter = quarter_check
                link = table[i].find("a").get("href")
                check = 1
                break

        if (check == 0):
            print("尚無資料")
            return -1

        response = requests.get(f"{domain}{link}", proxies=proxies)


    if name == "中國信託商業銀行":

        domain = "https://www.ctbcbank.com"

        response = requests.get(f"{domain}/content/dam/twrbo/pdf/aboutctbc/"
                                f"{year_check}Q{quarter_check}_CTBC.pdf",
                                proxies=proxies)
        if (response.status_code != 200):
            return -1

        year = year_check
        quarter = quarter_check
    
    if name == "樂天國際商業銀行":

        return -1

        domain = "https://www.rakuten-bank.com.tw"

        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/portal/other/disclosure")
        time.sleep(6)

        edge.find_element(By.ID, "finance").click()
        time.sleep(3)

        content = BeautifulSoup(edge.page_source, "html5lib")
        table = content.find_all("div", class_="collapse-block-head")

        check = 0
        for i in range(0, 2):
            if (str(year_check) in table[i].find("div", "txt collapse-block-title").getText() and
                quarter_text in table[i].find("div", "txt collapse-block-title").getText()):
                check = 1
                year = year_check
                quarter = quarter_check
                edge.find_elements(By.CLASS_NAME, "download-btn")[i].click()
                break

        if (check != 1):
            edge.close()
            return -1

        time.sleep(3)

        edge.switch_to.window(edge.window_handles[1])
        link = edge.current_url

        edge.quit()

        response = requests.get(f"{link}", proxies=proxies)


    if name == "連線商業銀行":

        domain = "https://corp.linebank.com.tw"

        edge = webdriver.Edge(options=options)
        edge.get(f"{domain}/zh-tw/company-financial")
        time.sleep(6)

        content = BeautifulSoup(edge.page_source, "html5lib")
        time.sleep(1)
        table = content.find_all("div", class_="el-tabs__content")
        target = table[1].find_all("div", class_="attachments layout-row")

        check = 0
        for i in range(0, len(target)):
            if f"{year_check}" in target[i].find("a").get("title") and quarter_text in target[i].find("a").get("title"):
                check = 1
                year = year_check
                quarter = quarter_check
                link = target[i].find("a").get("href")
                # edge.find_element(By.XPATH, f"//*[@id='pane-financialAudit']/div/table/tbody/tr[{i+1}]/div[3]/a/img").click()
                # time.sleep(3)
                break

        if (check == 0):
            print("尚無資料")
            return -1

        response = requests.get(f"{link}", proxies=proxies)
        
    if name == "將來商業銀行":

        domain = "https://www.nextbank.com.tw"

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.46',
                'Referer': 'https://www.nextbank.com.tw'}

        response = requests.get(f"{domain}/disclosures/download/52831e76d4000000d9ee07510ffac025",
                                headers=headers, verify=False, proxies=proxies)

        content = BeautifulSoup(response.text, "html5lib")

        table = content.find(string="資產品質")
        target = content.find_all("b")

        check = 0
        for i in range(0, len(table)):
            if (f"{year_check}" in target[i].getText() and quarter_text in target[i].getText()):
                year = year_check
                quarter = quarter_check
                link = table[i].find("a").get("href")
                check = 1
                break

        if (check == 0):
            print("尚無資料")
            return -1

        response = requests.get(f"{link}",
                                headers=headers, verify=False, proxies=proxies)

        path = f'data/{year}Q{quarter}'

        if not os.path.isdir(path):
            os.makedirs(path)

        with open(f'data/{year}Q{quarter}/{value}_{name}_{quarter}.pdf', 'wb') as file:
            file.write(response.content)

        return 1
