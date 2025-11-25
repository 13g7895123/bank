from get_Data import *
from get_report import *

from concurrent.futures import ThreadPoolExecutor


finish = 0  # control the searching loop. 1 for stop the loop
count = 0   # is used to initial the sheet

# 讀取銀行資料
lst = pd.read_excel("bank.xlsx")
bank_list = {lst.iat[i, 0]: [lst.iat[i, 1], lst.iat[i, 2], lst.iat[i, 5]] for i in range(len(lst))}

action = input("\n欲下載財報請輸入 1, 欲製作報表請輸入 2：")

while finish == 0:

    if action == '1':  # 下載檔案模式
        count += 1
        if count == 1:
            tmp_sheet = []

        year, quarter, option = call()  # 輸入年季，以及選擇下載種類

        if option == -1:
            break

        elif option == '1':  # 只下載指定的銀行財報
            while True:
                print("\n銀行名稱簡稱：")
                print(list(bank_list.keys()))
                bank = input("\n請輸入欲查詢資產狀況之銀行簡稱 (ex:台企)：")

                try:
                    name, value = bank_list[bank][1], bank_list[bank][0]
                    break
                except KeyError:
                    print("\n簡稱輸入錯誤！")

            begin = time.time()
            try:
                check = downloadData(name, value, year, quarter)
            except:
                check = -1

            if check == -1:
                print("\n此銀行尚無指定季度的資料，或是已有新的季度資料")
                print("\n請查看：", bank_list[bank][1], " ", bank_list[bank][2])
                count -= 1
                continue

            if check == 1:
                print("下載完成")
            end = time.time()
            finish = continue_or_not(finish)  # 詢問是否要繼續搜尋

        elif option == 'ALL':  # 下載全部銀行的財報
            args = []
            skip = 0
            begin = time.time()

            for i in range(len(lst)):
                name = lst.iat[i, 2]
                value = lst.iat[i, 1]
                args.append([name, value, year, quarter])

            with ThreadPoolExecutor(max_workers=20) as executor:
                for item in args:
                    executor.submit(downloadData, item[0], item[1], item[2], item[3])

            end = time.time()
            finish = 1
            print("\n-------------財報下載結束-------------\n")

            # 檢查哪些銀行沒有檔案
            files = os.listdir(f"data/{year}Q{quarter}")
            if len(files) != 38:
                for i in range(38):
                    file_path = f"data/{year}Q{quarter}/{lst.iat[i, 1]}_{lst.iat[i, 2]}_{year}Q{quarter}.pdf"
                    if not os.path.isfile(file_path):
                        print(lst.iat[i, 2], ", ", lst.iat[i, 5])
                        skip += 1
                print(f"\n{year}Q{quarter} 的資料夾中沒有以上 {skip} 家銀行的資料")

    elif action == '2':  # 製作報表模式
        begin = time.time()
        tmp_sheet = []
        args = []
        season = input("\n請輸入要製作的報表季度 (ex: 112Q1)：")
        print("\n-------------製作中-------------")

        year = int(season[0:3])
        quarter = int(season[4])

        for i in range(38):
            name = lst.iat[i, 2]
            value = lst.iat[i, 1]
            args.append([name, value, year, quarter])

        count = 0  # '資產品質'已經找到第幾次
        for item in args:
            temp = make_sheet(tmp_sheet, item[0], item[1], item[2], item[3], count)
            save_sheet(temp, year, quarter)

        finish = 1
        end = time.time()

    else:
        print("輸入錯誤!")
        action = input("\n欲下載財報請輸入 1, 欲製作報表請輸入 2：")

print("--------結束--------")
print("共花了 {:.2f} 秒".format(end - begin))
