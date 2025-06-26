-- PostgreSQL Schema for Unified Legal Data Tool

-- Drop existing tables if they exist (for a clean setup)
-- Be cautious with this in a production environment!
DROP TABLE IF EXISTS article_legal_concept CASCADE;
DROP TABLE IF EXISTS law_relationships CASCADE;
DROP TABLE IF EXISTS law_hierarchy_relationships CASCADE;
DROP TABLE IF EXISTS legal_concepts CASCADE;
DROP TABLE IF EXISTS articles CASCADE;
DROP TABLE IF EXISTS laws CASCADE;


-- 1. 法規資料表 (laws)
-- Stores core law information from XML, LLM outputs, and rich JSON metadata.
CREATE TABLE laws (
    id SERIAL PRIMARY PRIMARY KEY,                          -- 自動生成的唯一識別碼
    pcode VARCHAR(50) UNIQUE NOT NULL,              -- 法規PCode (from URL, e.g., A0000001), a reliable unique ID
    
    -- Fields directly from XML structure
    xml_law_nature VARCHAR(100),                    -- <法規性質> e.g., 憲法, 法律, 命令
    xml_law_name VARCHAR(255) NOT NULL,             -- <法規名稱>
    xml_law_url VARCHAR(512),                       -- <法規網址>
    xml_law_category VARCHAR(255),                  -- <法規類別> e.g., 行政＞勞動部＞組織目
    xml_latest_change_date DATE,                    -- <最新異動日期> (YYYYMMDD converted to DATE)
    xml_effective_date TEXT,                        -- <生效日期> (Can be complex, store as text or parse if consistently formatted)
    xml_effective_content TEXT,                     -- <生效內容>
    xml_abolition_mark TEXT,                        -- <廢止註記>
    xml_is_english_translated BOOLEAN,              -- <是否英譯註記> (Y/N converted to BOOLEAN)
    xml_english_law_name VARCHAR(512),              -- <英文法規名稱>
    xml_attachment TEXT,                            -- <附件 /> (Content or link)
    xml_history_content TEXT,                       -- <沿革內容>
    xml_preamble TEXT,                              -- <前言>

    -- LLM Generated Data
    llm_summary TEXT,                               -- LLM generated summary text
    llm_keywords TEXT,                              -- LLM generated keywords, concatenated into a single string

    -- Rich Metadata (as defined in 法律語法形式化.md)
    is_active BOOLEAN DEFAULT TRUE,
    law_metadata JSONB                              -- Stores the complete "Law Meta Data" JSON structure
);

COMMENT ON TABLE laws IS '儲存法規核心資訊(來自XML)、LLM生成資料以及豐富的JSON元數據 (Law Meta Data)';
COMMENT ON COLUMN laws.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN laws.pcode IS '法規PCode (來自法規網址中的pcode)，作為主要唯一識別碼';
COMMENT ON COLUMN laws.xml_law_nature IS 'XML來源: 法規性質';
COMMENT ON COLUMN laws.xml_law_name IS 'XML來源: 法規名稱';
COMMENT ON COLUMN laws.xml_law_url IS 'XML來源: 法規網址';
COMMENT ON COLUMN laws.xml_law_category IS 'XML來源: 法規類別';
COMMENT ON COLUMN laws.xml_latest_change_date IS 'XML來源: 最新異動日期';
COMMENT ON COLUMN laws.xml_effective_date IS 'XML來源: 生效日期';
COMMENT ON COLUMN laws.xml_effective_content IS 'XML來源: 生效內容';
COMMENT ON COLUMN laws.xml_abolition_mark IS 'XML來源: 廢止註記';
COMMENT ON COLUMN laws.xml_is_english_translated IS 'XML來源: 是否英譯註記';
COMMENT ON COLUMN laws.xml_english_law_name IS 'XML來源: 英文法規名稱';
COMMENT ON COLUMN laws.xml_attachment IS 'XML來源: 附件';
COMMENT ON COLUMN laws.xml_history_content IS 'XML來源: 沿革內容';
COMMENT ON COLUMN laws.xml_preamble IS 'XML來源: 前言';
COMMENT ON COLUMN laws.llm_summary IS 'LLM生成的法規摘要';
COMMENT ON COLUMN laws.llm_keywords IS 'LLM生成的關鍵字 (合併為單一字串)';
COMMENT ON COLUMN laws.law_metadata IS '儲存完整的法規元數據JSON內容 (依法律語法形式化.md)';

-- Indexes for laws table
CREATE INDEX idx_laws_pcode ON laws (pcode);
CREATE INDEX idx_laws_xml_law_name ON laws (xml_law_name); -- For searching by name
CREATE INDEX idx_laws_xml_law_category ON laws (xml_law_category);
CREATE INDEX idx_laws_llm_keywords_fts ON laws USING GIN (to_tsvector('simple', llm_keywords)); -- For full-text search on keywords
CREATE INDEX idx_laws_law_metadata_gin ON laws USING GIN (law_metadata); -- For querying JSONB


-- 2. 法條資料表 (articles)
-- Stores core article information from XML and rich JSON article metadata.
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,                          -- 自動生成的唯一識別碼
    law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE, -- 指向所屬法規的外部鍵
    
    -- Fields directly from XML structure (within <法規內容>)
    xml_chapter_section VARCHAR(255),               -- <編章節>
    xml_article_number VARCHAR(50) NOT NULL,        -- <條號>
    xml_article_content TEXT,                       -- <條文內容>

    -- Rich Metadata (as defined in 法律語法形式化.md)
    article_metadata JSONB,                         -- Stores the complete "Article Meta Data" JSON structure

    UNIQUE (law_id, xml_article_number)             -- 確保同一法規內的法條號碼唯一
);

COMMENT ON TABLE articles IS '儲存法條核心資訊(來自XML)以及豐富的JSON元數據 (Article Meta Data)';
COMMENT ON COLUMN articles.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN articles.law_id IS '指向所屬法規的外部鍵';
COMMENT ON COLUMN articles.xml_chapter_section IS 'XML來源: 編章節';
COMMENT ON COLUMN articles.xml_article_number IS 'XML來源: 條號';
COMMENT ON COLUMN articles.xml_article_content IS 'XML來源: 條文內容';
COMMENT ON COLUMN articles.article_metadata IS '儲存完整的法條元數據JSON內容 (依法律語法形式化.md)';

-- Indexes for articles table
CREATE INDEX idx_articles_law_id_article_number ON articles (law_id, xml_article_number);
CREATE INDEX idx_articles_article_metadata_gin ON articles USING GIN (article_metadata);


-- 3. 法律概念資料表 (legal_concepts)
-- Stores legal concept vocabulary (Legal Concept Meta Data)
CREATE TABLE legal_concepts (
    id SERIAL PRIMARY KEY,                          -- 自動生成的唯一識別碼
    law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE, -- 指向所屬法規的外部鍵
    code VARCHAR(255) NOT NULL,                     -- 法律概念代號
    name VARCHAR(255) NOT NULL,                     -- 詞彙名稱
    data JSONB,                                     -- Stores the complete "Legal Concept Meta Data" JSON
    UNIQUE (law_id, code)                           -- 確保同一法規內的法律概念代號唯一
);

COMMENT ON TABLE legal_concepts IS '儲存法律概念詞彙庫 (Legal Concept Meta Data)';
COMMENT ON COLUMN legal_concepts.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN legal_concepts.law_id IS '指向所屬法規的外部鍵';
COMMENT ON COLUMN legal_concepts.code IS '法律概念代號，在同一法規內唯一';
COMMENT ON COLUMN legal_concepts.name IS '詞彙名稱';
COMMENT ON COLUMN legal_concepts.data IS '儲存完整的法律概念 Meta Data JSON 內容';

-- Indexes for legal_concepts table
CREATE INDEX idx_legal_concepts_code ON legal_concepts (code);
CREATE INDEX idx_legal_concepts_name ON legal_concepts (name);
CREATE INDEX idx_legal_concepts_law_id ON legal_concepts (law_id);
CREATE INDEX idx_legal_concepts_data_gin ON legal_concepts USING GIN (data);


-- 4. 法規階層關係資料表 (law_hierarchy_relationships)
-- Describes hierarchical relationships between laws (Law Hierarchy Relationship Meta Data)
CREATE TABLE law_hierarchy_relationships (
    id SERIAL PRIMARY KEY,                          -- 自動生成的唯一識別碼
    relationship_code VARCHAR(255) UNIQUE NOT NULL, -- 關係代號，唯一 (e.g., LH_政府採購法_政府採購法施行細則)
    main_law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE,       -- 主要法規的外部鍵
    main_law_name VARCHAR(255),                     -- 主要法規名稱 (新增)
    related_law_id INTEGER NOT NULL REFERENCES laws(id) ON DELETE CASCADE,    -- 關聯法規的外部鍵
    related_law_name VARCHAR(255),                  -- 關聯法規名稱 (新增)
    hierarchy_type VARCHAR(100) NOT NULL,           -- 階層關係類型，例如 "子法規"
    data JSONB                                      -- Stores the complete "Law Hierarchy Relationship Meta Data" JSON
);

COMMENT ON TABLE law_hierarchy_relationships IS '描述法規之間的階層關係 (Law Hierarchy Relationship Meta Data)';
COMMENT ON COLUMN law_hierarchy_relationships.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN law_hierarchy_relationships.relationship_code IS '關係代號，唯一識別';
COMMENT ON COLUMN law_hierarchy_relationships.main_law_id IS '主要法規的外部鍵';
COMMENT ON COLUMN law_hierarchy_relationships.related_law_id IS '關聯法規的外部鍵';
COMMENT ON COLUMN law_hierarchy_relationships.hierarchy_type IS '階層關係類型';
COMMENT ON COLUMN law_hierarchy_relationships.data IS '儲存完整的法規階層關係 Meta Data JSON 內容';

-- Indexes for law_hierarchy_relationships table
CREATE INDEX idx_law_hierarchy_main_law_id ON law_hierarchy_relationships (main_law_id);
CREATE INDEX idx_law_hierarchy_related_law_id ON law_hierarchy_relationships (related_law_id);
CREATE INDEX idx_law_hierarchy_type ON law_hierarchy_relationships (hierarchy_type);
CREATE INDEX idx_law_hierarchy_data_gin ON law_hierarchy_relationships USING GIN (data);


-- 5. 法規關聯性資料表 (law_relationships)
-- Describes external relationships between laws, articles-to-laws, articles-to-articles (Law Relationship Meta Data)
CREATE TABLE law_relationships (
    id SERIAL PRIMARY KEY,                          -- 自動生成的唯一識別碼
    code VARCHAR(255) UNIQUE NOT NULL,              -- 關係代號，唯一 (e.g., LR_政府採購法_9)
    relationship_type VARCHAR(100) NOT NULL,        -- 關聯類型，例如 "法條-法規"
    main_law_id INTEGER REFERENCES laws(id) ON DELETE CASCADE,          -- 主要法規的外部鍵 (可為 NULL)
    main_law_name VARCHAR(255),                     -- 主要法規名稱 (新增)
    main_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,  -- 主要法條的外部鍵 (可為 NULL)
    related_law_id INTEGER REFERENCES laws(id) ON DELETE CASCADE,       -- 關聯法規的外部鍵 (可為 NULL)
    related_law_name VARCHAR(255),                  -- 關聯法規名稱 (新增)
    related_article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE, -- 關聯法條的外部鍵 (可為 NULL)
    data JSONB                                      -- Stores the complete "Law Relationship Meta Data" JSON
);

COMMENT ON TABLE law_relationships IS '描述不同法規之間、法條與法規之間、法條與法條(跨法規)等的外部關聯性 (Law Relationship Meta Data)';
COMMENT ON COLUMN law_relationships.id IS '自動生成的唯一識別碼';
COMMENT ON COLUMN law_relationships.code IS '關係代號，唯一識別';
COMMENT ON COLUMN law_relationships.relationship_type IS '關聯類型';
COMMENT ON COLUMN law_relationships.main_law_id IS '主要法規的外部鍵 (若關聯涉及法規)';
COMMENT ON COLUMN law_relationships.main_article_id IS '主要法條的外部鍵 (若關聯涉及法條)';
COMMENT ON COLUMN law_relationships.related_law_id IS '關聯法規的外部鍵 (若關聯涉及法規)';
COMMENT ON COLUMN law_relationships.related_article_id IS '關聯法條的外部鍵 (若關聯涉及法條)';
COMMENT ON COLUMN law_relationships.data IS '儲存完整的法規關聯性 Meta Data JSON 內容';

-- Indexes for law_relationships table
CREATE INDEX idx_law_relationships_type ON law_relationships (relationship_type);
CREATE INDEX idx_law_relationships_main_law ON law_relationships (main_law_id);
CREATE INDEX idx_law_relationships_main_article ON law_relationships (main_article_id);
CREATE INDEX idx_law_relationships_related_law ON law_relationships (related_law_id);
CREATE INDEX idx_law_relationships_related_article ON law_relationships (related_article_id);
CREATE INDEX idx_law_relationships_data_gin ON law_relationships USING GIN (data);


-- 6. 法條-法律概念連接資料表 (article_legal_concept)
-- Junction table for many-to-many relationship between articles and legal concepts.
CREATE TABLE article_legal_concept (
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,      -- 指向法條的外部鍵
    legal_concept_id INTEGER NOT NULL REFERENCES legal_concepts(id) ON DELETE CASCADE, -- 指向法律概念的外部鍵
    PRIMARY KEY (article_id, legal_concept_id)                                  -- 聯合主鍵，確保每對關係唯一
);

COMMENT ON TABLE article_legal_concept IS '連接法條與法律概念的資料表，記錄法條使用了哪些法律概念 (多對多)';
COMMENT ON COLUMN article_legal_concept.article_id IS '指向法條的外部鍵';
COMMENT ON COLUMN article_legal_concept.legal_concept_id IS '指向法律概念的外部鍵';

-- Indexes for article_legal_concept table
CREATE INDEX idx_alc_article_id ON article_legal_concept (article_id);
CREATE INDEX idx_alc_legal_concept_id ON article_legal_concept (legal_concept_id);

