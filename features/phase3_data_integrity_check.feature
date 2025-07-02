@FEAT-003
Feature: 階段三：檢查資料庫內的各個table 資料基本符合預期

  @SCEN-011
  Scenario: 檢查 laws 表格資料完整性
    Given 資料庫中已載入法規資料
    When 執行資料庫完整性檢查
    Then `laws` 表格應包含至少一筆紀錄
    And `laws` 表格中所有紀錄的 `pcode` 和 `xml_law_name` 欄位不應為空
    And `laws` 表格中所有紀錄的 `law_metadata` 欄位應為有效的 JSONB 格式且不為空

  @SCEN-012
  Scenario: 檢查 articles 表格資料完整性
    Given 資料庫中已載入法規資料
    When 執行資料庫完整性檢查
    Then `articles` 表格應包含至少一筆紀錄
    And `articles` 表格中所有紀錄的 `law_id` 和 `xml_article_number` 欄位不應為空
    And `articles` 表格中所有紀錄的 `article_metadata` 欄位應為有效的 JSONB 格式且不為空

  @SCEN-013
  Scenario: 檢查 legal_concepts 表格資料完整性
    Given 資料庫中已載入法律概念資料
    When 執行資料庫完整性檢查
    Then `legal_concepts` 表格應包含至少一筆紀錄
    And `legal_concepts` 表格中所有紀錄的 `law_id`、`code` 和 `name` 欄位不應為空
    And `legal_concepts` 表格中所有紀錄的 `data` 欄位應為有效的 JSONB 格式且不為空

  @SCEN-014
  Scenario: 檢查 law_hierarchy_relationships 表格資料完整性
    Given 資料庫中已載入法規階層關係資料
    When 執行資料庫完整性檢查
    Then `law_hierarchy_relationships` 表格應包含至少一筆紀錄
    And `law_hierarchy_relationships` 表格中所有紀錄的 `main_law_id`、`related_law_id` 和 `hierarchy_type` 欄位不應為空
    And `law_hierarchy_relationships` 表格中所有紀錄的 `data` 欄位應為有效的 JSONB 格式且不為空

  @SCEN-015
  Scenario: 檢查 law_relationships 表格資料完整性
    Given 資料庫中已載入法規關聯性資料
    When 執行資料庫完整性檢查
    Then `law_relationships` 表格應包含至少一筆紀錄
    And `law_relationships` 表格中所有紀錄的 `relationship_type` 欄位不應為空
    And `law_relationships` 表格中所有紀錄的 `data` 欄位應為有效的 JSONB 格式且不為空

  @SCEN-016
  Scenario: 檢查特定法規的資料一致性
    Given 資料庫中已載入法規 "政府採購法" 的完整資料
    When 執行資料庫一致性檢查
    Then "政府採購法" 在 `laws` 表格中的 `id` 應與其在 `articles`、`legal_concepts`、`law_hierarchy_relationships` 和 `law_relationships` 表格中的 `law_id` 關聯正確
    And "政府採購法" 的 `llm_summary` 和 `llm_keywords` 欄位不應為空

  @SCEN-017
  Scenario: 檢查摘要與關鍵字的缺漏情況並建立指標
    Given 資料庫中已載入法規資料
    When 執行摘要與關鍵字完整性檢查
    Then 應計算 `laws` 表格中 `llm_summary` 欄位為空的法規數量
    And 應計算 `laws` 表格中 `llm_keywords` 欄位為空的法規數量
    And 應計算 `laws` 表格中 `llm_summary` 欄位有值的法規比例
    And 應計算 `laws` 表格中 `llm_keywords` 欄位有值的法規比例
    And 應將這些指標記錄下來

  @SCEN-018
  Scenario: 檢查 Meta Data 灌入資料庫的完整性並建立指標
    Given 資料庫中已載入結構化 Meta Data
    When 執行 Meta Data 完整性檢查
    Then 應計算 `laws` 表格中 `law_metadata` 欄位為空的法規數量
    And 應計算 `articles` 表格中 `article_metadata` 欄位為空的法條數量
    And 應計算 `legal_concepts` 表格中 `data` 欄位為空的法律概念數量
    And 應計算 `law_hierarchy_relationships` 表格中 `data` 欄位為空的階層關係數量
    And 應計算 `law_relationships` 表格中 `data` 欄位為空的關聯性資料數量
    And 應計算 `laws` 表格中 `law_metadata` 欄位有值的法規比例
    And 應計算 `articles` 表格中 `article_metadata` 欄位有值的法條比例
    And 應計算 `legal_concepts` 表格中 `data` 欄位有值的法律概念比例
    And 應計算 `law_hierarchy_relationships` 表格中 `data` 欄位有值的階層關係比例
    And 應計算 `law_relationships` 表格中 `data` 欄位有值的關聯性資料比例
    And 應將這些指標記錄下來
