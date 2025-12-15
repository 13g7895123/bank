#!/bin/bash
# ============================================================
# Production 建置腳本
# 
# 用途：從 refactor 目錄建置 production 版本
# 
# 使用方式：
#   ./build_production.sh [production_path]
#
# 設定檔：
#   config.json - 設定 production_path（優先於命令列參數）
#   參考 config.example.json 建立設定檔
#
# 參數：
#   production_path - production 目錄的絕對路徑（選填）
#                     預設值：與 refactor 同層的 production 目錄
#
# 優先順序（由高到低）：
#   1. config.json 中的 production_path
#   2. 命令列參數
#   3. 預設路徑
#
# 範例：
#   ./build_production.sh                           # 使用設定檔或預設路徑
#   ./build_production.sh /opt/bank/production      # 指定路徑（設定檔優先）
# ============================================================

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 取得腳本所在目錄（refactor 目錄）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFACTOR_DIR="$SCRIPT_DIR"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# 從 config.json 讀取設定
read_config() {
    if [ -f "$CONFIG_FILE" ]; then
        # 使用 python 解析 JSON（較可靠）
        if command -v python3 &> /dev/null; then
            python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('production_path', ''))" 2>/dev/null
        elif command -v python &> /dev/null; then
            python -c "import json; print(json.load(open('$CONFIG_FILE')).get('production_path', ''))" 2>/dev/null
        else
            # 簡易 grep 方式（備用）
            grep -oP '"production_path"\s*:\s*"\K[^"]+' "$CONFIG_FILE" 2>/dev/null || echo ""
        fi
    fi
}

# 設定 production 目錄路徑（優先順序：設定檔 > 命令列 > 預設）
CONFIG_PRODUCTION_PATH=$(read_config)

if [ -n "$CONFIG_PRODUCTION_PATH" ]; then
    PRODUCTION_DIR="$CONFIG_PRODUCTION_PATH"
    echo -e "${YELLOW}使用設定檔路徑：$CONFIG_FILE${NC}"
elif [ -n "$1" ]; then
    PRODUCTION_DIR="$1"
else
    # 預設路徑：refactor 的同層目錄
    PRODUCTION_DIR="$(dirname "$REFACTOR_DIR")/production"
fi

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}          Production 建置腳本${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "來源目錄：${GREEN}$REFACTOR_DIR${NC}"
echo -e "目標目錄：${GREEN}$PRODUCTION_DIR${NC}"
echo ""

# 確認是否繼續
read -p "是否繼續建置？(y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}建置已取消${NC}"
    exit 0
fi

# 建立或清空目標目錄
echo -e "\n${BLUE}[1/4] 準備目標目錄...${NC}"
if [ -d "$PRODUCTION_DIR" ]; then
    echo -e "${YELLOW}清空現有目錄...${NC}"
    rm -rf "$PRODUCTION_DIR"
fi
mkdir -p "$PRODUCTION_DIR"
echo -e "${GREEN}✓ 目標目錄已準備${NC}"

# 複製檔案（排除指定項目）
echo -e "\n${BLUE}[2/4] 複製檔案...${NC}"
rsync -av --progress \
    --exclude='data' \
    --exclude='docs' \
    --exclude='output' \
    --exclude='Output' \
    --exclude='tests' \
    --exclude='ARCHITECTURE.md' \
    --exclude='STATUS.md' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='build_production.sh' \
    "$REFACTOR_DIR/" "$PRODUCTION_DIR/"
echo -e "${GREEN}✓ 檔案複製完成${NC}"

# 生成精簡版 STATUS.md
echo -e "\n${BLUE}[3/4] 生成 STATUS.md...${NC}"

# 建立標題
cat > "$PRODUCTION_DIR/STATUS.md" << 'STATUSEOF'
# 銀行財報系統 - 各銀行狀態明細

STATUSEOF

# 從原始 STATUS.md 提取「各銀行狀態明細」區塊
# 包含：更新日期、表格、註解
sed -n '/^## 各銀行狀態明細/,/^---$/p' "$REFACTOR_DIR/STATUS.md" | head -n -1 >> "$PRODUCTION_DIR/STATUS.md"

echo -e "${GREEN}✓ STATUS.md 已生成${NC}"

# 建立必要的空目錄
echo -e "\n${BLUE}[4/4] 建立必要目錄...${NC}"
mkdir -p "$PRODUCTION_DIR/data"
mkdir -p "$PRODUCTION_DIR/Output"
echo -e "${GREEN}✓ 目錄結構已建立${NC}"

# 顯示建置結果
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}          建置完成！${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "Production 目錄結構："
echo ""
tree -L 2 "$PRODUCTION_DIR" 2>/dev/null || ls -la "$PRODUCTION_DIR"
echo ""
echo -e "檔案統計："
echo -e "  - Python 檔案：$(find "$PRODUCTION_DIR" -name "*.py" | wc -l) 個"
echo -e "  - 銀行下載器：$(find "$PRODUCTION_DIR/banks" -name "bank_*.py" 2>/dev/null | wc -l) 個"
echo ""
echo -e "${GREEN}建置完成！${NC}"
echo -e "Production 路徑：${BLUE}$PRODUCTION_DIR${NC}"
