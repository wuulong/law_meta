-- PostgreSQL Schema for Legal Syntax Formalization Data

-- 1. 法規資料表 (laws)
-- 儲存整部法規的巨觀概覽資訊 (Law Meta Data)
CREATE TABLE laws (
    id SERIAL PRIMARY KEY, -- 自動生成的唯一識別碼
    code VARCHAR(255) UNIQUE NOT NULL, -- 法規代號，唯一
    name VARCHAR(255) NOT NULL, -- 法規名稱
    data JSONB -- 儲存完整的法規 Meta Data JSON
);

COMMENT ON TABLE laws IS '儲存整部法規的巨觀概覽資訊 (Law Meta Data)';
COMMENT ON COLUMN laws.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN laws.code IS '法規代號，唯一識別';
COMMENT ON COLUMN laws.name IS '法規名稱';
COMMENT ON COLUMN laws.data IS '儲存完整的法規 Meta Data JSON 內容';

-- 索引加速查詢
CREATE INDEX idx_laws_code ON laws (code);
CREATE INDEX idx_laws_name ON laws (name);
-- GIN 索引支援 JSONB 內容查詢
CREATE INDEX idx_laws_data_gin ON laws USING GIN (data);


-- 2. 法條資料表 (articles)
-- 儲存每一條法條的詳細資訊 (Article Meta Data)
CREATE TABLE articles (
    id SERIAL PRIMARY KEY, -- 自動生成的唯一識別碼
    law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE, -- 指向所屬法規的外部鍵
    article_number VARCHAR(50) NOT NULL, -- 法條條號
    data JSONB, -- 儲存完整的法條 Meta Data JSON

    -- 確保同一法規內的法條號碼唯一
    UNIQUE (law_id, article_number)
);

COMMENT ON TABLE articles IS '儲存每一條法條的詳細資訊 (Article Meta Data)';
COMMENT ON COLUMN articles.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN articles.law_id IS '指向所屬法規的外部鍵';
COMMENT ON COLUMN articles.article_number IS '法條條號';
COMMENT ON COLUMN articles.data IS '儲存完整的法條 Meta Data JSON 內容';

-- 索引加速查詢特定法規的法條或按條號排序
CREATE INDEX idx_articles_law_article ON articles (law_id, article_number);
-- GIN 索引支援 JSONB 內容查詢
CREATE INDEX idx_articles_data_gin ON articles USING GIN (data);


-- 3. 法律概念資料表 (legal_concepts)
-- 儲存法律概念詞彙庫 (Legal Concept Meta Data)
CREATE TABLE legal_concepts (
    id SERIAL PRIMARY KEY, -- 自動生成的唯一識別碼
    code VARCHAR(255) UNIQUE NOT NULL, -- 法律概念代號，唯一
    name VARCHAR(255) NOT NULL, -- 詞彙名稱
    data JSONB -- 儲存完整的法律概念 Meta Data JSON
);

COMMENT ON TABLE legal_concepts IS '儲存法律概念詞彙庫 (Legal Concept Meta Data)';
COMMENT ON COLUMN legal_concepts.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN legal_concepts.code IS '法律概念代號，唯一識別';
COMMENT ON COLUMN legal_concepts.name IS '詞彙名稱';
COMMENT ON COLUMN legal_concepts.data IS '儲存完整的法律概念 Meta Data JSON 內容';

-- 索引加速查詢
CREATE INDEX idx_legal_concepts_code ON legal_concepts (code);
CREATE INDEX idx_legal_concepts_name ON legal_concepts (name);
-- GIN 索引支援 JSONB 內容查詢
CREATE INDEX idx_legal_concepts_data_gin ON legal_concepts USING GIN (data);


-- 4. 法規階層關係資料表 (law_hierarchy_relationships)
-- 描述法規之間的階層關係 (Law Hierarchy Relationship Meta Data)
CREATE TABLE law_hierarchy_relationships (
    id SERIAL PRIMARY KEY, -- 自動生成的唯一識別碼
    relationship_code VARCHAR(255) UNIQUE NOT NULL, -- 關係代號，唯一
    main_law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE, -- 主要法規的外部鍵
    related_law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE, -- 關聯法規的外部鍵
    hierarchy_type VARCHAR(100) NOT NULL, -- 階層關係類型，例如 "子法規"
    data JSONB -- 儲存完整的法規階層關係 Meta Data JSON
);

COMMENT ON TABLE law_hierarchy_relationships IS '描述法規之間的階層關係 (Law Hierarchy Relationship Meta Data)';
COMMENT ON COLUMN law_hierarchy_relationships.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN law_hierarchy_relationships.relationship_code IS '關係代號，唯一識別';
COMMENT ON COLUMN law_hierarchy_relationships.main_law_id IS '主要法規的外部鍵';
COMMENT ON COLUMN law_hierarchy_relationships.related_law_id IS '關聯法規的外部鍵';
COMMENT ON COLUMN law_hierarchy_relationships.hierarchy_type IS '階層關係類型，例如 "子法規"';
COMMENT ON COLUMN law_hierarchy_relationships.data IS '儲存完整的法規階層關係 Meta Data JSON 內容';

-- 索引加速按主法規、關聯法規或關係類型查詢
CREATE INDEX idx_law_hierarchy_main_law_id ON law_hierarchy_relationships (main_law_id);
CREATE INDEX idx_law_hierarchy_related_law_id ON law_hierarchy_relationships (related_law_id);
CREATE INDEX idx_law_hierarchy_type ON law_hierarchy_relationships (hierarchy_type);
-- GIN 索引支援 JSONB 內容查詢
CREATE INDEX idx_law_hierarchy_data_gin ON law_hierarchy_relationships USING GIN (data);


-- 5. 法規關聯性資料表 (law_relationships)
-- 描述不同法規之間、法條與法規之間、法條與法條 (跨法規) 之間的外部關聯性 (Law Relationship Meta Data)
CREATE TABLE law_relationships (
    id SERIAL PRIMARY KEY, -- 自動生成的唯一識別碼
    code VARCHAR(255) UNIQUE NOT NULL, -- 關係代號，唯一
    relationship_type VARCHAR(100) NOT NULL, -- 關聯類型，例如 "法條-法規"
    main_law_id INTEGER REFERENCES laws(id) ON DELETE CASCADE, -- 主要法規的外部鍵 (可為 NULL)
    main_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE, -- 主要法條的外部鍵 (可為 NULL)
    related_law_id INTEGER REFERENCES laws(id) ON DELETE CASCADE, -- 關聯法規的外部鍵 (可為 NULL)
    related_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE, -- 關聯法條的外部鍵 (可為 NULL)
    data JSONB -- 儲存完整的法規關聯性 Meta Data JSON
);

COMMENT ON TABLE law_relationships IS '描述不同法規之間、法條與法規之間、法條與法條 (跨法規) 之間的外部關聯性 (Law Relationship Meta Data)';
COMMENT ON COLUMN law_relationships.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN law_relationships.code IS '關係代號，唯一識別';
COMMENT ON COLUMN law_relationships.relationship_type IS '關聯類型，例如 "法條-法規"';
COMMENT ON COLUMN law_relationships.main_law_id IS '主要法規的外部鍵 (如果關聯類型涉及法規)';
COMMENT ON COLUMN law_relationships.main_article_id IS '主要法條的外部鍵 (如果關聯類型涉及法條)';
COMMENT ON COLUMN law_relationships.related_law_id IS '關聯法規的外部鍵 (如果關聯類型涉及法規)';
COMMENT ON COLUMN law_relationships.related_article_id IS '關聯法條的外部鍵 (如果關聯類型涉及法條)';
COMMENT ON COLUMN law_relationships.data IS '儲存完整的法規關聯性 Meta Data JSON 內容';

-- 索引加速按關聯類型或涉及的法規/法條查詢
CREATE INDEX idx_law_relationships_type ON law_relationships (relationship_type);
CREATE INDEX idx_law_relationships_main_law ON law_relationships (main_law_id);
CREATE INDEX idx_law_relationships_main_article ON law_relationships (main_article_id);
CREATE INDEX idx_law_relationships_related_law ON law_relationships (related_law_id);
CREATE INDEX idx_law_relationships_related_article ON law_relationships (related_article_id);
-- GIN 索引支援 JSONB 內容查詢
CREATE INDEX idx_law_relationships_data_gin ON law_relationships USING GIN (data);


-- 6. 法條-法律概念連接資料表 (article_legal_concept)
-- 記錄法條與法律概念之間的「使用」關係 (多對多關係)
CREATE TABLE article_legal_concept (
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE, -- 指向法條的外部鍵
    legal_concept_id INTEGER NOT NULL REFERENCES legal_concepts(id) ON DELETE CASCADE, -- 指向法律概念的外部鍵

    -- 聯合主鍵，確保每對關係唯一
    PRIMARY KEY (article_id, legal_concept_id)
);

COMMENT ON TABLE article_legal_concept IS '連接法條與法律概念的資料表，記錄法條使用了哪些法律概念';
COMMENT ON COLUMN article_legal_concept.article_id IS '指向法條的外部鍵';
COMMENT ON COLUMN article_legal_concept.legal_concept_id IS '指向法律概念的外部鍵';

-- 索引加速按法條或法律概念查詢關聯
CREATE INDEX idx_article_legal_concept_article_id ON article_legal_concept (article_id);
CREATE INDEX idx_article_legal_concept_legal_concept_id ON article_legal_concept (legal_concept_id);
