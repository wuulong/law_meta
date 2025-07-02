#!/bin/bash

# ==============================================================================
# Script: update_laws.sh
# Description: 從 XML、摘要、關鍵字檔案，根據指定的法規名稱列表，
#              使用 law_cli.py 將法規資料完整更新至資料庫。
#              並包含匯出 Markdown、生成 Meta Data 及匯入 Meta Data 的步驟。
#              每個步驟都可以透過選項獨立控制是否執行。
#
# Usage: ./update_laws.sh [選項] [<xml_file>] [<summary_file>] [<keywords_file>] [<law_list_file>]
#
# Parameters:
#   <xml_file>:      包含所有法規內容的 XML 總表檔案路徑。 (預設: data/xml_sample.xml)
#   <summary_file>:  包含法規摘要的檔案路徑。 (預設: data/summary_law.md)
#   <keywords_file>: 包含法規關鍵字的檔案路徑。 (預設: data/keywords_law.csv)
#   <law_list_file>: 一個純文字檔，每行包含一個要處理的法規名稱。 (預設: data/law_tometa_list.txt)
#
# Options:
#   --skip-import-xml      跳過載入基礎資料 (XML)
#   --skip-update-summary  跳過更新摘要
#   --skip-update-keywords 跳過更新關鍵字
#   --skip-export-md       跳過匯出 Markdown
#   --skip-generate-meta   跳過生成 Meta Data (此步驟可能耗時較長且需要 GEMINI_API_KEY)
#   --skip-import-meta     跳過匯入 Meta Data
#
# Example:
#   ./update_laws.sh                                     # 使用所有預設值，執行所有步驟
#   ./update_laws.sh --skip-generate-meta                # 使用預設值，跳過生成 Meta Data
#   ./update_laws.sh my_laws.xml my_summary.md my_keywords.csv my_list.txt # 覆寫所有預設值
# ==============================================================================

# --- 變數設定 ---
CLI_SCRIPT="law_cli.py"
EXPORT_MD_DIR="output_dir"

# 預設檔案路徑
XML_FILE_DEFAULT="data/xml_sample.xml"
SUMMARY_FILE_DEFAULT="data/summary_law.md"
KEYWORDS_FILE_DEFAULT="data/keywords_law.csv"
LAW_LIST_FILE_DEFAULT="data/law_tometa_list.txt"

# --- 參數解析與選項設定 ---
SKIP_IMPORT_XML=false
SKIP_UPDATE_SUMMARY=false
SKIP_UPDATE_KEYWORDS=false
SKIP_EXPORT_MD=false
SKIP_GENERATE_META=false
SKIP_IMPORT_META=false

# 解析選項
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --skip-import-xml) SKIP_IMPORT_XML=true ;; 
        --skip-update-summary) SKIP_UPDATE_SUMMARY=true ;; 
        --skip-update-keywords) SKIP_UPDATE_KEYWORDS=true ;; 
        --skip-export-md) SKIP_EXPORT_MD=true ;; 
        --skip-generate-meta) SKIP_GENERATE_META=true ;; 
        --skip-import-meta) SKIP_IMPORT_META=true ;; 
        -*) # 處理未知選項
            echo "錯誤：未知選項 '$1'"
            echo "用法: $0 [選項] [<xml_file>] [<summary_file>] [<keywords_file>] [<law_list_file>]"
            exit 1
            ;;
        *) break ;; # 遇到非選項參數時停止解析選項
    esac
    shift
done

# 賦值主要參數 (如果命令列有提供，則覆蓋預設值)
# 檢查是否有提供部分參數但數量不對
if [[ "$#" -eq 0 ]]; then
    # 沒有提供任何檔案參數，使用所有預設值
    XML_FILE="$XML_FILE_DEFAULT"
    SUMMARY_FILE="$SUMMARY_FILE_DEFAULT"
    KEYWORDS_FILE="$KEYWORDS_FILE_DEFAULT"
    LAW_LIST_FILE="$LAW_LIST_FILE_DEFAULT"
elif [[ "$#" -eq 4 ]]; then
    # 提供了所有四個檔案參數
    XML_FILE="$1"
    SUMMARY_FILE="$2"
    KEYWORDS_FILE="$3"
    LAW_LIST_FILE="$4"
else
    # 提供了部分檔案參數，這是錯誤的
    echo "錯誤：如果提供檔案參數，必須提供全部 4 個，或不提供任何檔案參數以使用預設值。"
    echo "用法: $0 [選項] [<xml_file>] [<summary_file>] [<keywords_file>] [<law_list_file>]"
    exit 1
fi

# --- 檔案存在性檢查 ---
if [ ! -f "$CLI_SCRIPT" ]; then
    echo "錯誤：找不到核心腳本 '$CLI_SCRIPT'。請確認此腳本存在於目前目錄。"
    exit 1
fi
if [ ! -f "$XML_FILE" ]; then
    echo "錯誤：XML 檔案不存在於 '$XML_FILE'"
    exit 1
fi
if [ ! -f "$SUMMARY_FILE" ]; then
    echo "錯誤：摘要檔案不存在於 '$SUMMARY_FILE'"
    exit 1
fi
if [ ! -f "$KEYWORDS_FILE" ]; then
    echo "錯誤：關鍵字檔案不存在於 '$KEYWORDS_FILE'"
    exit 1
fi
if [ ! -f "$LAW_LIST_FILE" ]; then
    echo "錯誤：法規名稱列表檔案不存在於 '$LAW_LIST_FILE'"
    exit 1
fi

# --- 確保匯出目錄存在 ---
mkdir -p "$EXPORT_MD_DIR"
if [ $? -ne 0 ]; then
    echo "錯誤：無法建立匯出目錄 '$EXPORT_MD_DIR'。程序中止。"
    exit 1
fi

# --- 主處理流程 ---
echo "=== 開始法規資料庫完整更新程序 ==="
echo "使用 XML 檔案: $XML_FILE"
echo "使用摘要檔案: $SUMMARY_FILE"
echo "使用關鍵字檔案: $KEYWORDS_FILE"
echo "使用法規名稱列表: $LAW_LIST_FILE"
echo "匯出 Markdown 至: $EXPORT_MD_DIR"
echo "===================================="
echo ""

# 步驟 1: 從 XML 載入基礎法規資料 (根據法規名稱列表)
if [ "$SKIP_IMPORT_XML" = false ]; then
    echo "[1/6] 載入基礎資料 (from XML) ..."
    python3 "$CLI_SCRIPT" --import-xml "$XML_FILE" --law-list "$LAW_LIST_FILE"
    if [ $? -ne 0 ]; then
        echo "錯誤：從 XML 載入基礎資料失敗。程序中止。"
        exit 1
    fi
    echo "      -> 成功。"
else
    echo "[1/6] 跳過載入基礎資料 (from XML)。"
fi
echo ""

# 步驟 2: 更新法規摘要 (根據法規名稱列表)
if [ "$SKIP_UPDATE_SUMMARY" = false ]; then
    echo "[2/6] 更新摘要 (from Summary File) ..."
    python3 "$CLI_SCRIPT" --update-summary "$SUMMARY_FILE" --law-list "$LAW_LIST_FILE"
    if [ $? -ne 0 ]; then
        echo "錯誤：更新摘要失敗。程序中止。"
        exit 1
    fi
    echo "      -> 成功。"
else
    echo "[2/6] 跳過更新摘要。"
fi
echo ""

# 步驟 3: 更新法規關鍵字 (處理整個關鍵字檔案)
if [ "$SKIP_UPDATE_KEYWORDS" = false ]; then
    echo "[3/6] 更新關鍵字 (from Keywords File) ..."
    python3 "$CLI_SCRIPT" --update-keywords "$KEYWORDS_FILE"
    if [ $? -ne 0 ]; then
        echo "錯誤：更新關鍵字失敗。程序中止。"
        exit 1
    
    fi
    echo "      -> 成功。"
else
    echo "[3/6] 跳過更新關鍵字。"
fi
echo ""

# 步驟 4: 從 DB 匯出法規為 Markdown
if [ "$SKIP_EXPORT_MD" = false ]; then
    echo "[4/6] 從資料庫匯出法規為 Markdown ..."
    python3 "$CLI_SCRIPT" --export-law-list "$LAW_LIST_FILE" --output-dir "$EXPORT_MD_DIR"
    if [ $? -ne 0 ]; then
        echo "錯誤：匯出 Markdown 失敗。程序中止。"
        exit 1
    fi
    echo "      -> 成功。"
else
    echo "[4/6] 跳過匯出 Markdown。"
fi
echo ""

# 步驟 5: 準備 Meta Data 生成列表檔案並生成 Meta Data
if [ "$SKIP_GENERATE_META" = false ]; then

    # 生成 Meta Data (此步驟可能耗時較長且需要 GEMINI_API_KEY)
    echo "      -> 生成 Meta Data (此步驟可能耗時較長且需要 GEMINI_API_KEY) ..."
    python3 "$CLI_SCRIPT" --generate-meta-list "$GEN_META_LIST_FILE"
    if [ $? -ne 0 ]; then
        echo "錯誤：生成 Meta Data 失敗。程序中止。"
        exit 1
    fi
    echo "      -> 成功。"
else
    echo "[5/6] 跳過生成 Meta Data。"
fi
echo ""

# 步驟 6: 匯入 Meta Data
if [ "$SKIP_IMPORT_META" = false ]; then
    echo "[6/6] 匯入 Meta Data ..."
    # 注意：law_cli.py --import-meta-list 預期的是 law_list_file，其中包含法規名稱
    # 它會根據這些名稱去 tmp/meta_data_temp/ 目錄下尋找對應的 JSON 檔案。
    python3 "$CLI_SCRIPT" --import-meta-list "$LAW_LIST_FILE"
    if [ $? -ne 0 ]; then
        echo "錯誤：匯入 Meta Data 失敗。程序中止。"
        exit 1
    fi
    echo "      -> 成功。"
else
    echo "[6/6] 跳過匯入 Meta Data。"
fi
echo ""

echo "=== 所有法規處理完畢，程序成功結束。 ==="
exit 0
