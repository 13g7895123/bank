程式內容介紹

1. Main.py :

輸入所需抓取的年分、季度( EX : 114Q1 )

輸入年、季度後在Data、Output資料夾中，製造當年、季度資料夾

1. get\_Date : 從各銀行網站抓取Main輸入的財報，下載成PDF並存在Data資料夾中當年度/季度資料夾

程式需修改處(IP需修改) **如可以請將這部分改掉** :

![](data:image/png;base64...)

PDF檔名名稱 : 序號\_銀行名稱＿年度季度

EX : 1\_台灣銀行\_114Q1

序號請看 [Bank.xlsx](bank.xlsx)

以下是各銀行官網需抓取報表

抓取**銀行個體**財報

![](data:image/png;base64...)

**資產品質**

![](data:image/png;base64...)

**重要財務資料**

![](data:image/png;base64...)

1. get\_report : 從get\_Date所抓取的財報中的”**資產品質**”資料複製到新Excel，並儲存在Output / 當年、季度資料夾

抓取下面紅框處資訊，並另存Excel，順序依照[Bank.xlsx](bank.xlsx)

產出結果如[Output\_Example](Output_Example.xlsx)

![](data:image/png;base64...)