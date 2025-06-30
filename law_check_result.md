✦ law_check.py 腳本已執行完畢。

  檢查結果摘要：


   * laws 表格資料完整性 (SCEN-010)：
       * laws 表格包含 9844 筆紀錄，pcode 和 xml_law_name 欄位皆不為空。
       * 失敗：有 9831 筆紀錄的 law_metadata 欄位為空或無效。
   * articles 表格資料完整性 (SCEN-011)：
       * articles 表格包含 188927 筆紀錄，law_id 和 xml_article_number 欄位皆不為空。
       * 失敗：有 185125 筆紀錄的 article_metadata 欄位為空或無效。
   * legal_concepts 表格資料完整性 (SCEN-012)：
       * 通過：legal_concepts 表格包含 303 筆紀錄，所有欄位皆符合預期。
   * law_hierarchy_relationships 表格資料完整性 (SCEN-013)：
       * 通過：law_hierarchy_relationships 表格包含 54 筆紀錄，所有欄位皆符合預期。
   * law_relationships 表格資料完整性 (SCEN-014)：
       * 通過：law_relationships 表格包含 56 筆紀錄，所有欄位皆符合預期。
   * 特定法規 '政府採購法' 的資料一致性 (SCEN-015)：
       * 政府採購法 的關聯資料（articles, legal_concepts, law_hierarchy_relationships, law_relationships）檢查通過。
       * 失敗：政府採購法 的 llm_summary 或 llm_keywords 欄位為空。
   * 摘要與關鍵字的缺漏情況並建立指標 (SCEN-016)：
       * 總法規數量：9844
       * llm_summary 欄位為空的法規數量：2903 (約 29.49% 為空)
       * llm_keywords 欄位為空的法規數量：3452 (約 35.07% 為空)
       * llm_summary 欄位有值的法規比例：70.51%
       * llm_keywords 欄位有值的法規比例：64.93%
   * Meta Data 灌入資料庫的完整性並建立指標 (SCEN-017)：
       * laws 表格中 law_metadata 欄位有值的法規比例：0.13%
       * articles 表格中 article_metadata 欄位有值的法條比例：2.01%
       * legal_concepts 表格中 data 欄位有值的法律概念比例：100.00%
       * law_hierarchy_relationships 表格中 data 欄位有值的階層關係比例：100.00%
       * law_relationships 表格中 data 欄位有值的關聯性資料比例：100.00%

  總結：


  大部分的資料完整性檢查都通過了，但主要的問題點在於 laws 表格和 articles 表格中的 law_metadata 和 article_metadata
  欄位有大量的空值或無效值，這表示 Meta Data 的匯入可能不完整。此外，政府採購法
  的摘要或關鍵字欄位也為空，且整體法規的摘要和關鍵字填充率不高。


  這些結果顯示，在 Meta Data 的生成和匯入方面，以及 LLM 生成的摘要和關鍵字方面，還有改進的空間。