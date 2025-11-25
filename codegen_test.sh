#!/bin/bash
# Playwright Codegen 測試腳本
# 用於錄製各銀行的操作步驟

cd /home/jarvis/project/bonus/bank
source .venv/bin/activate

echo "=========================================="
echo "Playwright Codegen 銀行測試工具"
echo "=========================================="
echo ""
echo "使用方式："
echo "  1. 執行後會開啟瀏覽器"
echo "  2. 手動操作找到財報下載連結"
echo "  3. 點擊下載連結"
echo "  4. 關閉瀏覽器後，程式碼會自動生成"
echo ""
echo "選擇要測試的銀行："
echo "  1.  臺灣銀行"
echo "  2.  臺灣土地銀行"
echo "  4.  第一商業銀行"
echo "  5.  華南商業銀行"
echo "  9.  國泰世華商業銀行"
echo "  11. 高雄銀行"
echo "  12. 兆豐國際商業銀行"
echo "  13. 花旗（台灣）銀行"
echo "  16. 臺灣中小企業銀行"
echo "  18. 台中商業銀行"
echo "  20. 匯豐(台灣)商業銀行"
echo "  22. 華泰商業銀行"
echo "  23. 臺灣新光商業銀行"
echo "  24. 陽信商業銀行"
echo "  27. 聯邦商業銀行"
echo "  28. 遠東國際商業銀行"
echo "  30. 永豐商業銀行"
echo "  32. 凱基商業銀行"
echo "  33. 星展(台灣)商業銀行"
echo "  38. 樂天國際商業銀行"
echo "  40. 連線商業銀行"
echo "  41. 將來商業銀行"
echo ""
read -p "請輸入銀行代碼: " bank_code

case $bank_code in
    1)  url="https://www.bot.com.tw/tw/"; name="臺灣銀行" ;;
    2)  url="https://www.landbank.com.tw/"; name="臺灣土地銀行" ;;
    4)  url="https://www.firstbank.com.tw/"; name="第一商業銀行" ;;
    5)  url="https://www.hnfhc.com.tw/"; name="華南商業銀行" ;;
    9)  url="https://www.cathaybk.com.tw/"; name="國泰世華商業銀行" ;;
    11) url="https://www.bok.com.tw/"; name="高雄銀行" ;;
    12) url="https://www.megabank.com.tw/"; name="兆豐國際商業銀行" ;;
    13) url="https://www.citigroup.com/"; name="花旗銀行" ;;
    16) url="https://www.tbb.com.tw/"; name="臺灣中小企業銀行" ;;
    18) url="https://www.tcbbank.com.tw/"; name="台中商業銀行" ;;
    20) url="https://www.hsbc.com.tw/"; name="匯豐銀行" ;;
    22) url="https://www.hwataibank.com.tw/"; name="華泰商業銀行" ;;
    23) url="https://www.skbank.com.tw/"; name="臺灣新光商業銀行" ;;
    24) url="https://www.sunnybank.com.tw/"; name="陽信商業銀行" ;;
    27) url="https://www.ubot.com.tw/"; name="聯邦商業銀行" ;;
    28) url="https://www.feib.com.tw/"; name="遠東國際商業銀行" ;;
    30) url="https://bank.sinopac.com/"; name="永豐商業銀行" ;;
    32) url="https://www.kgibank.com.tw/"; name="凱基商業銀行" ;;
    33) url="https://www.dbs.com.tw/"; name="星展銀行" ;;
    38) url="https://www.rakuten-bank.com.tw/"; name="樂天國際商業銀行" ;;
    40) url="https://corp.linebank.com.tw/"; name="連線商業銀行" ;;
    41) url="https://www.nextbank.com.tw/"; name="將來商業銀行" ;;
    *)  echo "無效的銀行代碼"; exit 1 ;;
esac

output_file="codegen_output/bank_${bank_code}_${name}.py"
mkdir -p codegen_output

echo ""
echo "=========================================="
echo "正在開啟: $name"
echo "URL: $url"
echo "輸出檔案: $output_file"
echo "=========================================="
echo ""
echo "請在瀏覽器中操作找到財報下載連結..."
echo "完成後關閉瀏覽器，程式碼會自動儲存"
echo ""

playwright codegen --target python-async "$url" -o "$output_file"

echo ""
echo "=========================================="
echo "錄製完成！"
echo "程式碼已儲存到: $output_file"
echo "=========================================="
