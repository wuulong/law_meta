#!/bin/bash
# This script contains example commands extracted from features/phase4_cli_tools.feature

# @SCEN-019: 透過命令列工具匯入多個法規的 XML 資料，法規清單從檔案來
echo "--- Running SCEN-019 ---"
python law_cli.py --import-xml data/xml_sample.xml --law-list data/law_list_for_xml_import.txt
echo ""

# @SCEN-020: 透過命令列工具更新多個法規的 LLM 摘要，法規清單從檔案來
echo "--- Running SCEN-020 ---"
python law_cli.py --update-summary data/summary_sample.md --law-list data/law_list_for_summary_update.txt
echo ""

# @SCEN-021: 透過命令列工具更新多個法規的 LLM 關鍵字，法規清單從檔案來
echo "--- Running SCEN-021 ---"
python law_cli.py --update-keywords data/keywords_sample.csv --law-list data/law_list_for_keywords_update.txt
echo ""

# @SCEN-024: 透過命令列工具匯出多個法規的完整資料為 Markdown 檔案，法規清單從檔案來
echo "--- Running SCEN-024 ---"
python law_cli.py --export-law-list data/law_export_list.txt --output-dir output
echo ""

# @SCEN-022: 透過命令列工具從多個法規的 Markdown 檔案生成 Meta Data，法規清單從檔案來
echo "--- Running SCEN-022 ---"
python law_cli.py --generate-meta-list --law-list data/law_tometa_list.txt
echo ""

# @SCEN-026: 透過命令列工具將已產生的 Meta Data 灌入資料庫，法規清單從檔案來
echo "--- Running SCEN-026 ---"
python law_cli.py --import-meta-list --law-list data/law_list_import_meta.txt
echo ""

# @SCEN-023: 透過命令列工具刪除多個法規的所有資料，法規清單從檔案來
echo "--- Running SCEN-023 ---"
python law_cli.py --delete-law-list data/law_delete_list.txt
echo ""

# @SCEN-027: 透過命令列工具，將法規 md 檔，用 LLM 生成摘要，匯出格式要跟現在摘要範例一樣，命令列參數需提供 law_list.txt
echo "--- Running SCEN-027 ---"
python law_cli.py --generate-summary-from-md --law-list data/law_list_generate_summary.txt --summary-example-file output/summary_sample.md --output-dir output
python law_cli.py --update-summary output/all_laws_summary.md --law-list data/law_list_generate_summary.txt
echo ""

# @SCEN-028: 透過命令列工具從法規 Markdown 檔案生成 LLM 關鍵字
echo "--- Running SCEN-028 ---"
python law_cli.py --generate-keywords-from-md --law-list data/law_list_generate_keywords.txt --output-file output/keywords_sample.csv
python law_cli.py --update-keywords output/keywords_sample.csv --law-list data/law_list_generate_keywords.txt
echo ""


