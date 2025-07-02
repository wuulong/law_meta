@FEAT-002
Feature: 階段二：載入結構化 JSON Meta Data

  @SCEN-007
  Scenario: 透過命令列工具載入多個法規的完整結構化 Meta Data
    Given 一個包含多個法規名稱的清單檔案 "data/law_tometa_list.txt"
    And "json/" 目錄下存在清單中每個法規對應的五種 Meta Data JSON 檔案
    When 執行命令列工具 `python law_cli.py --load-meta-list data/law_tometa_list.txt`
    Then 資料庫中清單中所有法規的 `laws` 表格 `law_metadata` 欄位應被填入
    And 資料庫中清單中所有法規的 `articles` 表格 `article_metadata` 欄位應被填入
    And 資料庫中清單中所有法規的 `legal_concepts` 資料表應包含對應的法律概念
    And 資料庫中清單中所有法規的 `law_hierarchy_relationships` 資料表應包含對應的階層關係
    And 資料庫中清單中所有法規的 `law_relationships` 資料表應包含對應的關聯性資料

  @SCEN-008
  Scenario: 載入一部法規的完整結構化 Meta Data
    Given 資料庫中已存在法規 "民法" 的基本資料
    And "json/" 目錄下存在對應 "民法" 的五種 Meta Data JSON 檔案:
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

  @SCEN-009
  Scenario: 產生法規關係的視覺化圖表
    Given 系統中已載入 "民法" 與 "民法總則施行法" 的 Meta Data
    When 執行 `law_meta_loader.ipynb` 的視覺化功能
    Then 應生成一個 Mermaid 圖表，顯示 "民法" 與 "民法總則施行法" 之間的關係

  @SCEN-010
  Scenario: 從既有法規匯出法規，以供後續 meta data 生成
    Given 資料庫中已存在法規 "預算法" 的完整資料
    When 執行 `law_meta_loader.ipynb` 的法規匯出功能
    Then 應在 "data/" 目錄下生成 "預算法.md" 檔案，其中包含 "預算法" 的完整條文內容
