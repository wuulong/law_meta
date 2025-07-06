開始執行資料庫檢查...
Connecting to PostgreSQL: lawdb@211.73.81.235:30198/lawdb...
Successfully connected to PostgreSQL.
--- 檢查 laws 表格資料完整性 (SCEN-010) ---
Database connection is active.
PASS: laws 表格包含 9841 筆紀錄。
PASS: laws 表格中所有紀錄的 pcode 和 xml_law_name 欄位皆不為空。
FAIL: laws 表格中有 9699 筆紀錄的 law_metadata 欄位為空或無效。 (其中 142 筆有值)

--- 檢查 articles 表格資料完整性 (SCEN-011) ---
Database connection is active.
PASS: articles 表格包含 188778 筆紀錄。
PASS: articles 表格中所有紀錄的 law_id 和 xml_article_number 欄位皆不為空。
FAIL: articles 表格中有 185222 筆紀錄的 article_metadata 欄位為空或無效。

--- 檢查 legal_concepts 表格資料完整性 (SCEN-012) ---
Database connection is active.
PASS: legal_concepts 表格包含 12549 筆紀錄。
PASS: legal_concepts 表格中所有紀錄的 law_id, code 和 name 欄位皆不為空。
PASS: legal_concepts 表格中所有紀錄的 data 欄位皆為有效的 JSONB 格式且不為空。

--- 檢查 law_hierarchy_relationships 表格資料完整性 (SCEN-013) ---
Database connection is active.
PASS: law_hierarchy_relationships 表格包含 553 筆紀錄。
PASS: law_hierarchy_relationships 表格中所有紀錄的 main_law_id, related_law_id 和 hierarchy_type 欄位皆不為空。
PASS: law_hierarchy_relationships 表格中所有紀錄的 data 欄位皆為有效的 JSONB 格式且不為空。

--- 檢查 law_relationships 表格資料完整性 (SCEN-014) ---
Database connection is active.
PASS: law_relationships 表格包含 2433 筆紀錄。
PASS: law_relationships 表格中所有紀錄的 relationship_type 欄位皆不為空。
PASS: law_relationships 表格中所有紀錄的 data 欄位皆為有效的 JSONB 格式且不為空。

--- 檢查特定法規 '政府採購法' 的資料一致性 (SCEN-015) ---
Database connection is active.
找到法規 '政府採購法' 的 ID: 9925
PASS: articles 表格中找到 123 筆與 '政府採購法' 相關的法條。
PASS: legal_concepts 表格中找到 6 筆與 '政府採購法' 相關的法律概念。
PASS: law_hierarchy_relationships 表格中找到 17 筆與 '政府採購法' 相關的階層關係。
PASS: law_relationships 表格中找到 14 筆與 '政府採購法' 相關的關聯性資料。
FAIL: 法規 '政府採購法' 的 llm_summary 或 llm_keywords 欄位為空。

--- 檢查摘要與關鍵字的缺漏情況並建立指標 (SCEN-016) ---
Database connection is active.
總法規數量: 9841
llm_summary 欄位為空的法規數量: 3008
llm_keywords 欄位為空的法規數量: 3454
llm_summary 欄位有值的法規比例: 69.43%
llm_keywords 欄位有值的法規比例: 64.90%

--- 檢查 Meta Data 灌入資料庫的完整性並建立指標 (SCEN-017) ---
Database connection is active.
總法規數量: 9841
總法條數量: 188778
總法律概念數量: 12549
總法規階層關係數量: 553
總法規關聯性資料數量: 2433
laws 表格中 law_metadata 欄位為空的法規數量: 9699，非空的法規數量：142
articles 表格中 article_metadata 欄位為空的法條數量: 185222
legal_concepts 表格中 data 欄位為空的法律概念數量: 0
law_hierarchy_relationships 表格中 data 欄位為空的階層關係數量: 0
law_relationships 表格中 data 欄位為空的關聯性資料數量: 0
articles 表格中包含的法規數量: 9841
legal_concepts 表格中包含的法規數量: 131
law_hierarchy_relationships 表格中包含的法規數量 (主法規或關聯法規): 357
law_relationships 表格中包含的法規數量 (主法規或關聯法規): 348
law_relationships 表格中包含的法規數量 (主法規): 131
law_hierarchy_relationships 表格中包含的法規數量 (主法規): 130
laws 表格中 law_metadata 欄位有值的法規比例: 1.44%
articles 表格中 article_metadata 欄位有值的法條比例: 1.88%
legal_concepts 表格中 data 欄位有值的法律概念比例: 100.00%
law_hierarchy_relationships 表格中 data 欄位有值的階層關係比例: 100.00%
law_relationships 表格中 data 欄位有值的關聯性資料比例: 100.00%

--- 檢查 Meta Data 遺漏法規列表 ---
articles 表格中沒有遺漏的法規。
legal_concepts 表格中遺漏的法規:

  - 行政訴訟法
  - 金融資產證券化條例
  - 臺灣地區與大陸地區人民關係條例
  - 行政罰法
  - 專利法
  - 證券投資信託及顧問法
  - 公司法
  - 商業事件審理法
  - 土地徵收條例
  - 家庭暴力防治法
  - 地方制度法
law_hierarchy_relationships 表格中遺漏的法規:
  - 印花稅法
  - 不動產證券化條例
  - 民事訴訟法施行法
  - 中華民國憲法增修條文
  - 職工福利金條例
  - 環境影響評估法
  - 警察職權行使法
  - 中央銀行法
law_relationships 表格中遺漏的法規:
  - 中華民國憲法增修條文

law_relationships 表格中 main_law_id 遺漏的法規:
  - 刑事訴訟法
  - 中華民國憲法增修條文
  - 兒童及少年性剝削防制條例
  - 香港澳門關係條例
  - 法官法
  - 公務員懲戒法
  - 國家公園法
  - 家庭暴力防治法
  - 中央銀行法
  - 地方制度法
  - 印花稅法

law_hierarchy_relationships 表格中 main_law_id 遺漏的法規:
  - 電子票證發行管理條例
  - 中央法規標準法
  - 中華民國憲法增修條文
  - 證券投資信託及顧問法
  - 不動產證券化條例
  - 著作權法
  - 期貨交易法
  - 行政罰法
  - 警察職權行使法
  - 兒童及少年性剝削防制條例
  - 香港澳門關係條例
  - 公務員懲戒法
  - 職工福利金條例
  - 環境影響評估法
  - 國家公園法
  - 家庭暴力防治法
  - 民事訴訟法施行法
  - 中央銀行法
  - 印花稅法
Disconnected from PostgreSQL.

部分資料庫檢查未通過，請檢查上述錯誤訊息。
