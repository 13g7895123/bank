import os
import pandas as pd
import pdfplumber
import tabula
import os
import fitz_new as fitz
import numpy as np
import cv2
import re
import pytesseract


def call():

    while True:
        period = input("\n請輸入欲製作報表之季度 (ex:112Q1)，或是輸入exit結束程式: ")
        if len(period) == 5:
            break
        elif period == 'exit':
            return -1, -1, -1
        else:
            print()
            print("輸入格式錯誤!")
            print()

    quarter = int(period[4])
    tmp = period.split(period[3])
    year = int(tmp[0])

    while True:
        print()
        option = input("查詢單一銀行請輸入 1, 全部銀行請輸入 ALL): ")
        if (option != '1' and option != 'ALL'):
            print()
            print("輸入格式錯誤!")
            print()
        else:
            break

    return year, quarter, option


def continue_or_not(finish):
    again = 'T'
    while again != 'y' and again != 'n' and again != 'Y' and again != 'N':
        print()
        again = input("是否再查詢一家?(y/n):")
        print()
        if again == 'y' or again == 'Y':
            finish = 0
        elif again == 'n' or again == 'N':
            finish = 1
        else:
            print()
            print("輸入錯誤!")
            print()

    return finish


def find_page(start, end, pdf):

    search_text = '資產品質'
    page_id = -2
    print(start)
    for i in range(start, end, 1):
        contents = []
        pageObj = pdf.pages[i]
        contents = pageObj.extract_text().split()  # 切開

        for content in contents:  # 檢查目標文字有沒有在內容裡面
            if (search_text in content):
                page_id = i
                break

        if page_id != -2:
            break

    return page_id


def loadData(name, value, year, quarter, pid, count):

    ## 載入檔案 & 總頁數 ##
    try:
        with pdfplumber.open(f'data/{year}Q{quarter}/{value}_{name}_{year}Q{quarter}.pdf') as pdf:
            total_pages = len(pdf.pages)
            end = total_pages
            start = pid
            print(name)
            print("共", total_pages, "頁")
            if total_pages > 99 and count == 0:
                start = int(total_pages / 2)

            pageFound = find_page(start, end, pdf)

            return pageFound
    except:
        return -2


def make_sheet(sheet, name, value, year, quarter, count):

    subjects = ['01_企業金融_擔保',
                '02_企業金融_無擔保',
                '03_消費金融_住宅抵押貸款',
                '04_消費金融_現金卡',
                '05_消費金融_小額純信用貸款',
                '06_消費金融_其他_擔保',
                '07_消費金融_其他_無擔保',
                '08_合計']

    quarter_text = 'Q' + str(quarter)

    obj = ['擔', '擔', '住宅', '現', '小額', '擔', '無', '合']  # 財報項目關鍵字

    pid = 0
    idx = 0
    try:
        if value == 20 or value == 21:
            pdfDoc = fitz.open(f'data/{year}Q{quarter}/{value}_{name}_{year}Q{quarter}.pdf')
            for pg in range(pdfDoc.page_count):
                page = pdfDoc[pg]
                rotate = int(0)
                print(pg)
                zoom_x = 1.33333333
                zoom_y = 1.33333333
                mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # 判斷存放圖片的文件夾是否存在；若圖片文件夾不存在就創建
                if not os.path.exists(f"./data/{year}Q{quarter}/{value}_{year}Q{quarter}/"):
                    os.makedirs(f"./data/{year}Q{quarter}/{value}_{year}Q{quarter}/")

                pix.writeIMG(
                    f"./data/{year}Q{quarter}/{value}_{year}Q{quarter}/{value}_{year}Q{quarter}" + '_' + str(pg) + '.png',
                    1, 95
                )
                src = f'./data/{year}Q{quarter}/{value}_{year}Q{quarter}/{value}_{year}Q{quarter}' + '_' + str(pg) + '.png'
                file = cv2.imread(src, 1)
                after = cv2.resize(file, (file.shape[1] * 3, file.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
                text = pytesseract.image_to_string(after, lang='chi_tra')
                print(text)
                if "業務" in text and "小額" in text:
                    idx = pg
                    break
        else:
            # 直到找到目標表格為止
            while pid != -2:
                th = 0
                # 尋找表格在第幾頁
                idx = loadData(name, value, year, quarter, pid, count)
                table = tabula.read_pdf(
                    f'data/{year}Q{quarter}/{value}_{name}_{year}Q{quarter}.pdf',
                    encoding="utf-8",
                    pages=f'{idx + 1}'
                )

                if table != []:
                    # 避免選錯表格
                    if len(table[0].loc[0]) < 6:
                        th = 1
                        try:
                            test = len(table[1].loc[0])
                        except:
                            th = 0

                    for j in range(0, len(table[th])):
                        if type(table[th].loc[j][0]) is str:
                            if '業務合計' in table[th].loc[j][0]:
                                pid = -2
                                break
                        elif type(table[th].loc[j][1]) is str:
                            if '業務合計' in table[th].loc[j][1]:
                                pid = -2
                                break

                if (pid == -2):
                    break
                pid = idx + 1
                count = count + 1

            print(table)

    except:  # 檔案讀取錯誤就會自動跳過
        for i in range(0, 8):
            amount = ""
            total = ""
            ratio = ""
            if (value < 10):
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'0{value}_{name}']
            else:
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'{value}_{name}']
            sheet.append(row)

        return sheet

    # ========= 分支一：value 為 20 或 21（影像辨識處理） =========
    if value == 20 or value == 21:
        src = f'./data/{year}Q{quarter}/{value}_{year}Q{quarter}/{value}_{year}Q{quarter}' + '_' + str(idx) + '.png'
        file = cv2.imread(src, 1)
        after = cv2.resize(file, (file.shape[1] * 3, file.shape[0] * 3), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
        rows, cols = binary.shape
        scale = 40

        # 辨識表格橫線
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_col = cv2.dilate(eroded, kernel, iterations=1)

        # 辨識表格縱線
        scale = 20
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_row = cv2.dilate(eroded, kernel, iterations=1)

        bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)

        # 表格輪廓
        merge = cv2.add(dilated_col, dilated_row)

        # 去框留下內容
        merge2 = cv2.subtract(binary, merge)

        # 瘦線條
        new_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        erode_image = cv2.morphologyEx(merge2, cv2.MORPH_OPEN, new_kernel)

        merge3 = cv2.add(erode_image, bitwise_and)

        # cv2.imshow('after', merge3)
        # 疊罩辨識結果，以下兩行也要取消
        # cv2.imshow('after', merge3)
        # 疊罩辨識結果，以下兩行也要取消註解，不然會卡住
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        ys, xs = np.where(bitwise_and > 0)

        y_point_arr = []
        x_point_arr = []

        i = 0
        sort_x_point = np.sort(xs)
        for i in range(len(sort_x_point) - 1):
            if sort_x_point[i + 1] - sort_x_point[i] > 4:
                x_point_arr.append(sort_x_point[i])
                i = i + 1
        x_point_arr.append(sort_x_point[i])

        i = 0
        sort_y_point = np.sort(ys)
        for i in range(len(sort_y_point) - 1):
            if (sort_y_point[i + 1] - sort_y_point[i] > 4):
                y_point_arr.append(sort_y_point[i])
                i = i + 1
        y_point_arr.append(sort_y_point[i])

        data = [[] for i in range(len(y_point_arr))]
        for i in range(len(y_point_arr) - 1):
            for j in range(len(x_point_arr) - 1):
                cell = merge3[y_point_arr[i]:y_point_arr[i + 1], x_point_arr[j]:x_point_arr[j + 1]]
                text1 = pytesseract.image_to_string(cell, lang="chi_tra")  # 辨識繁體中文模式

                # 去除特殊符號
                text1 = re.findall(r'[^*/?\\|<>\\"\(\n]', text1, re.S)
                text1 = "".join(text1)
                print('圖片訊息：' + text1)
                data[i].append(text1)
                j = j + 1
            i = i + 1

        # 兩段起始欄位設定（保留原始兩段；與你提供內容一致）
        if value == 20:
            start = 2
        else:
            start = 3

        if value == 20:
            start = 2
        else:
            start = 3

        for i in range(0, len(subjects)):
            for j in range(0, 3):
                target = data[i + start][start + j]

                target = str(target)
                print(target)
                if target == '':
                    target = "0"
                if "$" in target:
                    target = target.replace("$", "8")
                if "S" in target:
                    target = target.replace("S", "8")
                if "." in target and len(target) > 4 and j == 2:
                    target = target[0:4]
                if j < 2:
                    target = target.replace(".", "").replace(",", "")

                if j == 0:
                    amount = int(target)
                elif j == 1:
                    total = int(target)
                elif j == 2:
                    ratio = float(target)

            if (value < 10):
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'0{value}_{name}']
            else:
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'{value}_{name}']
            sheet.append(row)

        return sheet

    # ========= 分支二：表格讀取不到（table is None） =========
    elif (table is None):  # 表格讀取不到就會留白跳過
        for i in range(0, 8):
            amount = ""
            total = ""
            ratio = ""
            if (value < 10):
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'0{value}_{name}']
            else:
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'{value}_{name}']
            sheet.append(row)

        return sheet

    # ========= 分支三：一般文字解析（pdfplumber + 字串處理） =========
    else:
        with pdfplumber.open(f'data/{year}Q{quarter}/{value}_{name}_{year}Q{quarter}.pdf') as pdf:
            pageObj = pdf.pages[idx]
            contents = pageObj.extract_text().split()

        print("\n---------------------------")
        print(contents)
        current = 0
        print(value)

        for i in range(0, len(obj)):
            find = 0  # 目標項目編號
            for k in range(current, int(len(contents) * 0.9)):

                if i == 2 and value == 11:
                    # 高雄銀行才有的怪異現象
                    obj[i] = '住宅'

                if (obj[i] in contents[k]):
                    location = k
                    for j in range(1, 12):

                        if contents[location + j].count("$") > 1:
                            tmp = contents[location + j].replace("$", " ").split()
                            contents.insert(location + j + 1, tmp[1])
                            contents[location + j] = tmp[0]
                            target = contents[location + j].replace("$", "").replace(",", "")

                        elif (contents[location + j + 1][0] == '-' and len(contents[location + j + 1]) > 1):
                            contents[location + j] = contents[location + j] + contents[location + j + 1]
                            contents.pop(location + j + 1)
                            target = contents[location + j].replace("$", "").replace(",", "")

                        else:
                            target = contents[location + j].replace("$", "").replace(",", "")

                        if target == "-" or target == "-%" or target == "%":
                            target = '0'

                        if target == "-" or target == "-%" or target == "%":
                            target = '0'

                        if (find <= 1):
                            try:
                                dummy = int(target)
                            except:
                                continue
                        elif (find > 1):
                            try:
                                dummy = float(target.replace("%", ""))
                            except:
                                continue

                        # 為了解決表格讀取後的格式問題
                        if (len(target) == 1 and type(dummy) is int and dummy != 0):
                            if (find == 0 and "%" not in contents[location + j + 2]) or (find == 1 and "%" not in contents[location + j + 1]):
                                element = contents[location + j + 1].replace("$", "").replace(",", "")
                                contents[location + j] = str(dummy) + element
                                dummy = int(str(dummy) + element)
                                contents.pop(location + j + 1)

                        find = find + 1

                        if i == 0 and find == 1:
                            if ((len(contents[location]) == 1 and "." in contents[location + j + 1]) or len(contents[location + j]) > 2):
                                find = find - 1
                                continue

                        if (find == 1):
                            amount = dummy
                        elif (find == 2):
                            total = dummy
                        elif (find == 3):
                            ratio = dummy

                        if find == 3:
                            break
                    if find == 3:
                        break

            if (find == 0):  # 該銀行沒有該目標項目的話就顯示，例如:無現金卡
                amount = "-----"
                total = "-----"
                ratio = "-----"
            else:
                current = k + 2

            if (value < 10):
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'0{value}_{name}']
            else:
                row = [year, quarter_text, subjects[i], amount, total, ratio, f'{value}_{name}']
            sheet.append(row)

        return sheet


def save_sheet(sheet, year, quarter):

    titles = ['資料年度', '季度', '業務別項目', '逾期放款金額(單位：仟元)', '放款總額(單位：仟元)', '逾放比率', '銀行名稱']

    name = "ALL"

    path = f'output/{year}Q{quarter}'

    if not os.path.isdir(path):
        os.makedirs(path)

    result = pd.DataFrame(sheet, columns=titles)
    result.to_excel(f'output/{year}Q{quarter}/{name}.xlsx', index=False)
    print("save Successfully")
