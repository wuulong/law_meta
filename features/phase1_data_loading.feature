@FEAT-001
Feature: 階段一：載入法規原始資料與 LLM 生成資料

  @SCEN-001
  Scenario: 從 XML 檔案同步法規與法條至資料庫
    Given 一個包含多部法規的 XML 檔案 "data/law_sample.xml"
    And 一個空的目標資料庫
    When 執行 `law_proc.ipynb` 中的資料庫同步功能
    Then "laws" 資料表中應包含從 XML 解析出的法規紀錄
    And "articles" 資料表中應包含所有對應的法條紀錄

  @SCEN-002
  Scenario: 更新 XML 資料時保留 LLM 欄位
    Given 資料庫中已存在法規 "政府採購法"，其 "llm_summary" 欄位已有資料
    And 一個包含 "政府採購法" 更新內容的 XML 檔案 "data/law_sample_update.xml"
    When 執行 `law_proc.ipynb` 中的資料庫同步功能
    Then "laws" 資料表中 "政府採購法" 的 XML 衍生欄位應被更新
    And "laws" 資料表中 "政府採購法" 的 "llm_summary" 欄位應被保留

  @SCEN-003
  Scenario: 匯入 LLM 生成的法規摘要
    Given 資料庫中已存在法規 "政府採購法"
    And 一個位於 "data/summary_dir_law.md" 的摘要檔案，其中包含 "政府採購法" 的摘要
    When 執行 `law_proc.ipynb` 中的摘要匯入功能
    Then "laws" 資料表中 "政府採購法" 紀錄的 "llm_summary" 欄位應被更新

  @SCEN-004
  Scenario: 匯入 LLM 生成的法規關鍵字
    Given 資料庫中已存在法規 "政府採購法"
    And 一個位於 "data/keywords_law.csv" 的關鍵字檔案，其中包含 "政府採購法" 的關鍵字
    When 執行 `law_proc.ipynb` 中的關鍵字匯入功能
    Then "laws" 資料表中 "政府採購法" 紀錄的 "llm_keywords" 欄位應被更新

  @SCEN-005
  Scenario: 重建特定法規在資料庫中的所有內容
    Given 資料庫中已存在 "預算法" 的完整資料
    And 已準備好 "預算法" 的所有最新來源資料 (XML, 摘要, 關鍵字)
    When 執行 `law_proc.ipynb` 中針對 "預算法" 的重建功能
    Then 資料庫中所有與 "預算法" 相關的舊資料應被清除
    And 應使用最新的來源資料重新匯入 "預算法" 的所有內容
