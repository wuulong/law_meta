@FEAT-004
Feature: 階段四：命令列工具，能夠利用下達不同參數，做到維護資料庫內資料的功能
  所有命令列參數都應支援長短兩種形式，例如 `--import-xml-list` 可使用 `-x`。

  @SCEN-019
  Scenario: 透過命令列工具匯入多個法規的 XML 資料，法規清單從檔案來
    Given 一個包含多個法規 XML 檔案路徑的清單檔案 "data/xml_sample.xml"
    And 資料庫中不存在清單中的法規
    When 執行命令列工具 `python law_cli.py --import-xml data/xml_sample.xml`
    Then "laws" 資料表中應包含從 XML 解析出的清單中所有法規紀錄
    And "articles" 資料表中應包含所有對應的法條紀錄

  @SCEN-020
  Scenario: 透過命令列工具更新多個法規的 LLM 摘要，法規清單從檔案來
    Given 資料庫中已存在多個法規
    And 一個包含多法規名稱與摘要內容的檔案 "data/summary_sample.md"
    When 執行命令列工具 `python law_cli.py --update-summary data/summary_sample.md` 或 `python law_cli.py -s data/law_summary.txt`
    Then "laws" 資料表中清單中所有法規紀錄的 "llm_summary" 欄位應被更新

  @SCEN-021
  Scenario: 透過命令列工具更新多個法規的 LLM 關鍵字，法規清單從檔案來
    Given 資料庫中已存在多個法規
    And 一個包含法規名稱與關鍵字檔案路徑對應的清單檔案 "data/keywords_sample.csv"
    When 執行命令列工具 `python law_cli.py --update-keywords data/keywords_sample.csv` 或 `python law_cli.py -k data/law_keyword_list.txt`
    Then "laws" 資料表中清單中所有法規紀錄的 "llm_keywords" 欄位應被更新

  @SCEN-022
  Scenario: 透過命令列工具從多個法規的 Markdown 檔案生成 Meta Data，法規清單從檔案來
    Given 一個包含法規名稱與 Markdown 檔案路徑對應的清單檔案 "data/law_tometa_list.txt"
    And 一份定義 Meta Data 結構的規格檔案 "法律語法形式化.md"
    When 執行命令列工具 `python law_cli.py --generate-meta-list data/law_tometa_list.txt` 或 `python law_cli.py -g data/law_markdown_list.txt`
    Then 應在 "json/" 目錄下生成清單中每個法規對應的五種 Meta Data JSON 檔案

  @SCEN-023
  Scenario: 透過命令列工具刪除多個法規的所有資料，法規清單從檔案來
    Given 資料庫中已存在多個法規
    And 一個包含要刪除法規名稱的清單檔案 "data/law_delete_list.txt"
    When 執行命令列工具 `python law_cli.py --delete-law-list data/law_delete_list.txt` 或 `python law_cli.py -d data/law_delete_list.txt`
    Then 資料庫中所有與清單中法規相關的紀錄應被清除 (laws, articles, legal_concepts, law_hierarchy_relationships, law_relationships)

  @SCEN-024
  Scenario: 透過命令列工具匯出多個法規的完整資料為 Markdown 檔案，法規清單從檔案來
    Given 資料庫中已存在多個法規的完整資料
    And 一個包含要匯出法規名稱的清單檔案 "data/law_tometa_list.txt"
    When 執行命令列工具 `python law_cli.py --export-law-list data/law_tometa_list.txt --output-dir output_dir` 或 `python law_cli.py -e data/law_export_list.txt output_dir/`
    Then "output_dir/" 目錄下應生成清單中每個法規對應的 Markdown 檔案，其中包含該法規的完整條文內容及相關 Meta Data (若有)

  @SCEN-025
  Scenario: 透過命令列工具執行資料庫完整性檢查並輸出報告
    Given 資料庫中已載入法規資料
    When 執行命令列工具 `python law_cli.py --check-integrity` 或 `python law_cli.py -c`
    Then 應輸出資料庫完整性檢查報告，包含各表格的資料量、空值比例等指標
    And 報告應儲存至預設的報告檔案路徑

  @SCEN-026
  Scenario: 透過命令列工具將已產生的 Meta Data 灌入資料庫，法規清單從檔案來
    Given 一個包含多個法規名稱的清單檔案 "data/law_tometa_list.txt"
    And "json/" 目錄下存在清單中每個法規對應的五種 Meta Data JSON 檔案
    When 執行命令列工具 `python law_cli.py --import-meta-list data/law_tometa_list.txt` 或 `python law_cli.py -m data/law_tometa_list.txt`
    Then 資料庫中對應法規的 `laws` 表格 `law_metadata` 欄位應被填入
    And 資料庫中對應法規的 `articles` 表格 `article_metadata` 欄位應被填入
    And 資料庫中對應法規的 `legal_concepts` 資料表應包含對應的法律概念
    And 資料庫中對應法規的 `law_hierarchy_relationships` 資料表應包含對應的階層關係
    And 資料庫中對應法規的 `law_relationships` 資料表應包含對應的關聯性資料
