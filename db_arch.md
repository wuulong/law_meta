### **一、建議建立的 `VIEW` (視圖)**

視圖可以將複雜的 JOIN 操作或 JSONB 欄位的提取預先定義好，讓使用者或應用程式查詢時更簡潔。

1.  **`v_laws_overview` (法規概覽)**
    *   **目的**：提供法規的基本資訊、LLM 摘要和關鍵字，方便快速瀏覽和搜尋。
    *   **包含欄位**：`pcode`, `xml_law_name`, `xml_law_nature`, `xml_law_category`, `xml_latest_change_date`, `llm_summary`, `llm_keywords`。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_laws_overview AS
        SELECT
            id,
            pcode,
            xml_law_name,
            xml_law_nature,
            xml_law_category,
            xml_latest_change_date,
            llm_summary,
            llm_keywords
        FROM laws;
        ```

2.  **`v_articles_with_law_info` (法條與所屬法規資訊)**
    *   **目的**：將法條內容與其所屬法規的名稱、PCode 等資訊結合，方便查詢特定法條時能同時看到法規背景。
    *   **包含欄位**：`l.xml_law_name` (法規名稱), `l.pcode` (法規 PCode), `a.xml_article_number` (條號), `a.xml_article_content` (條文內容), `a.xml_chapter_section` (編章節)。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_articles_with_law_info AS
        SELECT
            a.id AS article_id,
            l.id AS law_id,
            l.xml_law_name,
            l.pcode,
            a.xml_article_number,
            a.xml_article_content,
            a.xml_chapter_section
        FROM articles a
        JOIN laws l ON a.law_id = l.id;
        ```

3.  **`v_law_metadata_extracted` (法規元數據提取)**
    *   **目的**：將 `laws.law_metadata` JSONB 欄位中常用的元數據（如主管機關、法律領域、公布日期等）提取為獨立欄位，方便直接查詢和過濾。
    *   **包含欄位**：`l.pcode`, `l.xml_law_name`, `l.law_metadata->>'主管機關'` AS `meta_competent_authority`, `l.law_metadata->'法規詳細類別'->>'法律領域'` AS `meta_law_domain`, `l.law_metadata->'法規時間軸'->>'公布日期'` AS `meta_publish_date`, `l.law_metadata->>'簡述'` AS `meta_summary_from_json`。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_law_metadata_extracted AS
        SELECT
            id,
            pcode,
            xml_law_name,
            law_metadata->>'主管機關' AS meta_competent_authority,
            law_metadata->'法規詳細類別'->>'法律領域' AS meta_law_domain,
            law_metadata->'法規時間軸'->>'公布日期' AS meta_publish_date,
            law_metadata->>'簡述' AS meta_summary_from_json
        FROM laws;
        ```

4.  **`v_article_legal_concepts_detail` (法條與法律概念詳情)**
    *   **目的**：顯示每個法條所關聯的法律概念及其定義，有助於理解法條中的專業術語。
    *   **包含欄位**：`l.xml_law_name`, `a.xml_article_number`, `a.xml_article_content`, `lc.name` AS `concept_name`, `lc.data->>'定義'` AS `concept_definition`。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_article_legal_concepts_detail AS
        SELECT
            l.xml_law_name,
            a.xml_article_number,
            a.xml_article_content,
            lc.name AS concept_name,
            lc.data->>'定義' AS concept_definition
        FROM articles a
        JOIN article_legal_concept alc ON a.id = alc.article_id
        JOIN legal_concepts lc ON alc.legal_concept_id = lc.id
        JOIN laws l ON a.law_id = l.id;
        ```

5.  **`v_law_relationships_readable` (可讀的法規關聯)**
    *   **目的**：將 `law_relationships` 表中的 ID 轉換為法規或法條的名稱和條號，使其更具可讀性。
    *   **包含欄位**：`lr.relationship_type`, `ml.xml_law_name` AS `main_law_name`, `ma.xml_article_number` AS `main_article_number`, `rl.xml_law_name` AS `related_law_name`, `ra.xml_article_number` AS `related_article_number`, `lr.data->>'關聯說明'` AS `relationship_description`。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_law_relationships_readable AS
        SELECT
            lr.relationship_type,
            ml.xml_law_name AS main_law_name,
            ma.xml_article_number AS main_article_number,
            rl.xml_law_name AS related_law_name,
            ra.xml_article_number AS related_article_number,
            lr.data->>'關聯說明' AS relationship_description
        FROM law_relationships lr
        LEFT JOIN laws ml ON lr.main_law_id = ml.id
        LEFT JOIN articles ma ON lr.main_article_id = ma.id
        LEFT JOIN laws rl ON lr.related_law_id = rl.id
        LEFT JOIN articles ra ON lr.related_article_id = ra.id;
        ```
6.  **`v_law_hierarchy_relationships_readable` (可讀的法規階層關係)**
    *   **目的**：將 `law_hierarchy_relationships` 表中的 `main_law_id` 和 `related_law_id` 轉換為法規名稱，使其階層關係更易於理解。
    *   **包含欄位**：`lhr.hierarchy_type`, `ml.xml_law_name` AS `main_law_name`, `rl.xml_law_name` AS `related_law_name`, `lhr.data->>'關聯說明'` AS `hierarchy_description`。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_law_hierarchy_relationships_readable AS
        SELECT
            lhr.hierarchy_type,
            ml.xml_law_name AS main_law_name,
            rl.xml_law_name AS related_law_name,
            lhr.data->>'關聯說明' AS hierarchy_description
        FROM law_hierarchy_relationships lhr
        JOIN laws ml ON lhr.main_law_id = ml.id
        JOIN laws rl ON lhr.related_law_id = rl.id;
        ```

7.  **`v_legal_concepts_overview` (法律概念概覽)**
    *   **目的**：提供法律概念的基本資訊，方便快速瀏覽和搜尋。
    *   **包含欄位**：`lc.name` (詞彙名稱), `lc.data->>'定義'` (定義), `lc.data->>'概念類別'` (概念類別), `lc.data->>'同義詞'` (同義詞)。
    *   **範例 SQL**：
        ```sql
        CREATE VIEW v_legal_concepts_overview AS
        SELECT
            id,
            name AS concept_name,
            data->>'定義' AS definition,
            data->>'概念類別' AS concept_category,
            data->>'同義詞' AS synonyms
        FROM legal_concepts;
        ```

### **二、建議建立的 `STORED PROCEDURE` / `FUNCTION` (儲存程序/函數)**

儲存程序或函數可以封裝更複雜的業務邏輯，例如多條件搜尋、獲取完整法規內容等。

1.  **`f_search_laws_by_keyword(p_keyword TEXT)` (依關鍵字搜尋法規)**
    *   **目的**：提供一個函數，可以根據關鍵字在法規名稱、LLM 摘要或 LLM 關鍵字中進行模糊搜尋。
    *   **輸入**：`p_keyword` (搜尋關鍵字)。
    *   **輸出**：符合條件的法規列表。
    *   **範例 SQL (PostgreSQL 函數)**：
        ```sql
        CREATE OR REPLACE FUNCTION f_search_laws_by_keyword(p_keyword TEXT)
        RETURNS SETOF laws AS $$
        BEGIN
            RETURN QUERY
            SELECT *
            FROM laws
            WHERE
                xml_law_name ILIKE '%' || p_keyword || '%' OR
                llm_summary ILIKE '%' || p_keyword || '%' OR
                llm_keywords ILIKE '%' || p_keyword || '%';
        END;
        $$ LANGUAGE plpgsql;
        ```
        *   **使用範例**：`SELECT * FROM f_search_laws_by_keyword('政府採購');`

2.  **`f_get_law_full_content(p_pcode VARCHAR)` (獲取法規完整內容)**
    *   **目的**：根據法規 PCode 獲取該法規的所有詳細資訊，包括其所有法條。
    *   **輸入**：`p_pcode` (法規 PCode)。
    *   **輸出**：法規主體資訊及一個包含所有法條的 JSON 陣列或多個結果集。
    *   **範例 SQL (PostgreSQL 函數，返回 JSONB)**：
        ```sql
        CREATE OR REPLACE FUNCTION f_get_law_full_content(p_pcode VARCHAR)
        RETURNS JSONB AS $$
        DECLARE
            law_data JSONB;
            articles_data JSONB;
        BEGIN
            SELECT to_jsonb(l.*) INTO law_data
            FROM laws l
            WHERE l.pcode = p_pcode;

            IF law_data IS NULL THEN
                RETURN NULL;
            END IF;

            SELECT jsonb_agg(to_jsonb(a.*) ORDER BY a.xml_article_number) INTO articles_data
            FROM articles a
            WHERE a.law_id = (SELECT id FROM laws WHERE pcode = p_pcode);

            RETURN jsonb_build_object(
                'law', law_data,
                'articles', COALESCE(articles_data, '[]'::jsonb)
            );
        END;
        $$ LANGUAGE plpgsql;
        ```
        *   **使用範例**：`SELECT f_get_law_full_content('A0000001');`

3.  **`f_get_article_details_with_concepts(p_law_pcode VARCHAR, p_article_number VARCHAR)` (獲取法條詳情及相關概念)**
    *   **目的**：根據法規 PCode 和法條號碼，獲取該法條的詳細內容，並列出所有相關的法律概念及其定義。
    *   **輸入**：`p_law_pcode` (法規 PCode), `p_article_number` (法條號碼，例如 '第 1 條')。
    *   **輸出**：法條內容、所屬法規名稱及相關法律概念列表。
    *   **範例 SQL (PostgreSQL 函數，返回 JSONB)**：
        ```sql
        CREATE OR REPLACE FUNCTION f_get_article_details_with_concepts(
            p_law_pcode VARCHAR,
            p_article_number VARCHAR
        )
        RETURNS JSONB AS $$
        DECLARE
            article_info JSONB;
            concepts_info JSONB;
        BEGIN
            SELECT to_jsonb(a.*) || jsonb_build_object('law_name', l.xml_law_name) INTO article_info
            FROM articles a
            JOIN laws l ON a.law_id = l.id
            WHERE l.pcode = p_law_pcode AND a.xml_article_number = p_article_number;

            IF article_info IS NULL THEN
                RETURN NULL;
            END IF;

            SELECT jsonb_agg(to_jsonb(lc.*) || jsonb_build_object('definition', lc.data->>'定義')) INTO concepts_info
            FROM legal_concepts lc
            JOIN article_legal_concept alc ON lc.id = alc.legal_concept_id
            WHERE alc.article_id = (SELECT id FROM articles WHERE law_id = (SELECT id FROM laws WHERE pcode = p_law_pcode) AND xml_article_number = p_article_number);

            RETURN jsonb_build_object(
                'article', article_info,
                'legal_concepts', COALESCE(concepts_info, '[]'::jsonb)
            );
        END;
        $$ LANGUAGE plpgsql;
        ```
        *   **使用範例**：`SELECT f_get_article_details_with_concepts('A0000001', '第 1 條');`
這些 `VIEW` 和 `FUNCTION` 可以大大提升您法規資料庫的可用性，讓資料查詢和應用開發更加便捷。您可以根據實際的查詢模式和業務需求，進一步擴展和優化這些視圖和函數。

4.  **`f_search_laws_by_category(p_category TEXT)` (依類別搜尋法規)**
    *   **目的**：根據法規類別進行搜尋，例如「行政＞勞動部＞組織目」。
    *   **輸入**：`p_category` (法規類別)。
    *   **輸出**：符合條件的法規列表。
    *   **範例 SQL (PostgreSQL 函數)**：
        ```sql
        CREATE OR REPLACE FUNCTION f_search_laws_by_category(p_category TEXT)
        RETURNS SETOF laws AS $$
        BEGIN
            RETURN QUERY
            SELECT *
            FROM laws
            WHERE xml_law_category ILIKE '%' || p_category || '%';
        END;
        $$ LANGUAGE plpgsql;
        ```
        *   **使用範例**：`SELECT * FROM f_search_laws_by_category('行政＞勞動部');`

5.  **`f_search_articles_by_content(p_keyword TEXT)` (依內容搜尋法條)**
    *   **目的**：在法條內容中進行模糊搜尋。
    *   **輸入**：`p_keyword` (搜尋關鍵字)。
    *   **輸出**：符合條件的法條列表，包含所屬法規資訊。
    *   **範例 SQL (PostgreSQL 函數)**：
        ```sql
        CREATE OR REPLACE FUNCTION f_search_articles_by_content(p_keyword TEXT)
        RETURNS TABLE(
            law_name VARCHAR,
            pcode VARCHAR,
            article_number VARCHAR,
            article_content TEXT,
            chapter_section VARCHAR
        ) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                l.xml_law_name,
                l.pcode,
                a.xml_article_number,
                a.xml_article_content,
                a.xml_chapter_section
            FROM articles a
            JOIN laws l ON a.law_id = l.id
            WHERE a.xml_article_content ILIKE '%' || p_keyword || '%';
        END;
        $$ LANGUAGE plpgsql;
        ```
        *   **使用範例**：`SELECT * FROM f_search_articles_by_content('中華民國');`

6.  **`f_get_legal_concepts_for_law(p_pcode VARCHAR)` (獲取某法規的所有法律概念)**
    *   **目的**：根據法規 PCode，列出該法規中所有被引用的法律概念。
    *   **輸入**：`p_pcode` (法規 PCode)。
    *   **輸出**：該法規中所有法律概念的列表。
    *   **範例 SQL (PostgreSQL 函數)**：
        ```sql
        CREATE OR REPLACE FUNCTION f_get_legal_concepts_for_law(p_pcode VARCHAR)
        RETURNS SETOF legal_concepts AS $$
        BEGIN
            RETURN QUERY
            SELECT DISTINCT lc.*
            FROM legal_concepts lc
            JOIN article_legal_concept alc ON lc.id = alc.legal_concept_id
            JOIN articles a ON alc.article_id = a.id
            JOIN laws l ON a.law_id = l.id
            WHERE l.pcode = p_pcode;
        END;
        $$ LANGUAGE plpgsql;
        ```
        *   **使用範例**：`SELECT * FROM f_get_legal_concepts_for_law('A0000001');`