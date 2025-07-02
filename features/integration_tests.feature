
@integration
Feature: 整合測試：命令列工具與實際資料庫/檔案系統的互動

  @SCEN-019-INT
  Scenario: 透過命令列工具匯入一個真實的法規 XML 資料
    Given 一個內容已知的法規 XML 檔案 "integration_test_law.xml" 和一個指向該檔案的清單檔案 "integration_test_list.txt"  
    And 一個乾淨且準備就緒的測試資料庫
    When 執行命令列工具匯入該清單檔案
    Then 資料庫的 "laws" 資料表中應包含 "中華民國憲法" 的紀錄
    And 資料庫的 "articles" 資料表中應包含 "中華民國憲法" 的 175 筆法條紀錄
    And 資料庫的 "laws" 資料表中應包含 "國家安全會議組織法" 的紀錄
    And 資料庫的 "articles" 資料表中應包含 "國家安全會議組織法" 的 16 筆法條紀錄

  @SCEN-020-INT
  Scenario: 透過命令列工具更新多個法規的 LLM 摘要，法規清單從檔案來 (整合測試)
    Given 資料庫中已存在多個法規
    And 一個內容已知的法規 XML 檔案 "data/xml_sample.xml" 和一個指向該檔案的清單檔案 "data/law_list.txt"
    When 執行命令列工具 `python law_cli.py --update-summary data/summary_sample.md`
    Then "laws" 資料表中清單中所有法規紀錄的 "llm_summary" 欄位應被更新
