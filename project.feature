Feature: 法規資料庫整合與管理
  此專案旨在建立一個全面的法規資料庫，整合來自多個來源的資料：
  1.  **來源一 (XML)**：來自政府開放資料的原始法規 XML 檔案。
  2.  **來源二 (LLM)**：由大型語言模型產生的法規摘要與關鍵字。
  3.  **來源三 (JSON)**：根據「法律語法形式化」規範所定義的結構化 Meta Data。

  資料處理分為兩個主要階段：
  - **第一階段 (law_proc.ipynb)**：處理來源一和來源二，將基本法規資料、摘要和關鍵字載入資料庫。
  - **第二階段 (law_meta_loader.ipynb)**：處理來源三，將結構化的 JSON Meta Data 載入資料庫。

# --- 第一階段 (law_proc.ipynb) ---

Feature: 階段一：載入法規原始資料與 LLM 生成資料

  Scenario: 從 XML 檔案同步法規與法條至資料庫
    Given 一個包含多部法規的 XML 檔案 "data/law_sample.xml"
    And 一個空的目標資料庫
    When 執行 `law_proc.ipynb` 中的資料庫同步功能
    Then "laws" 資料表中應包含從 XML 解析出的法規紀錄
    And "articles" 資料表中應包含所有對應的法條紀錄

  Scenario: 更新 XML 資料時保留 LLM 欄位
    Given 資料庫中已存在法規 "政府採購法"，其 "llm_summary" 欄位已有資料
    And 一個包含 "政府採購法" 更新內容的 XML 檔案 "data/law_sample_update.xml"
    When 執行 `law_proc.ipynb` 中的資料庫同步功能
    Then "laws" 資料表中 "政府採購法" 的 XML 衍生欄位應被更新
    And "laws" 資料表中 "政府採購法" 的 "llm_summary" 欄位應被保留

  Scenario: 匯入 LLM 生成的法規摘要
    Given 資料庫中已存在法規 "政府採購法"
    And 一個位於 "data/summary_dir_law.md" 的摘要檔案，其中包含 "政府採購法" 的摘要
    When 執行 `law_proc.ipynb` 中的摘要匯入功能
    Then "laws" 資料表中 "政府採購法" 紀錄的 "llm_summary" 欄位應被更新

  Scenario: 匯入 LLM 生成的法規關鍵字
    Given 資料庫中已存在法規 "政府採購法"
    And 一個位於 "data/keywords_law.csv" 的關鍵字檔案，其中包含 "政府採購法" 的關鍵字
    When 執行 `law_proc.ipynb` 中的關鍵字匯入功能
    Then "laws" 資料表中 "政府採購法" 紀錄的 "llm_keywords" 欄位應被更新

  Scenario: 重建特定法規在資料庫中的所有內容
    Given 資料庫中已存在 "預算法" 的完整資料
    And 已準備好 "預算法" 的所有最新來源資料 (XML, 摘要, 關鍵字)
    When 執行 `law_proc.ipynb` 中針對 "預算法" 的重建功能
    Then 資料庫中所有與 "預算法" 相關的舊資料應被清除
    And 應使用最新的來源資料重新匯入 "預算法" 的所有內容

# --- 第二階段 (law_meta_loader.ipynb) ---

Feature: 階段二：載入結構化 JSON Meta Data

  Scenario: 使用 LLM 從法規內文生成 Meta Data JSON 檔案
    Given 一個法規的 Markdown 檔案 "data/new_law.md"
    And 一份定義 Meta Data 結構的規格檔案 "法律語法形式化.md"
    When 執行 `law_meta_loader.ipynb` 的 Meta Data 生成功能
    Then 應在 "json/" 目錄下生成五個對應的 JSON 檔案:
      | json/new_law_law_regulation.json    |
      | json/new_law_law_articles.json      |
      | json/new_law_legal_concepts.json    |
      | json/new_law_hierarchy_relations.json |
      | json/new_law_law_relations.json     |

  Scenario: 載入一部法規的完整結構化 Meta Data
    Given 資料庫中已存在法規 "民法" 的基本資料
    And "json/" 目錄下存在對應 "民法" 的五種 Meta Data JSON 檔案:
      |
      | json/民法_law_regulation.json         |
      | json/民法_law_articles.json           |
      | json/民法_legal_concepts.json         |
      | json/民法_hierarchy_relations.json    |
      | json/民法_law_relations.json          |
    When 執行 `law_meta_loader.ipynb` 以載入 "民法" 的 Meta Data
    Then "laws" 資料表中 "民法" 紀錄的 "law_metadata" 欄位應被填入
    And "articles" 資料表中 "民法" 所有法條的 "article_metadata" 欄位應被填入
    And "legal_concepts" 資料表應包含 "民法" 的法律概念
    And "law_hierarchy_relationships" 資料表應包含 "民法" 的階層關係
    And "law_relationships" 資料表應包含 "民法" 的關聯性資料

  Scenario: 產生法規關係的視覺化圖表
    Given 系統中已載入 "民法" 與 "民法總則施行法" 的 Meta Data
    When 執行 `law_meta_loader.ipynb` 的視覺化功能
    Then 應生成一個 Mermaid 圖表，顯示 "民法" 與 "民法總則施行法" 之間的關係


