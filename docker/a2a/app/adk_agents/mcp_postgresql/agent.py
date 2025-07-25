# 成功測試
# ./adk_agent_samples/mcp_agent/agent.py
import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# It's good practice to define paths dynamically if possible,
# or ensure the user understands the need for an ABSOLUTE path.
# For this example, we'll construct a path relative to this file,
# assuming '/path/to/your/folder' is in the same directory as agent.py.
# REPLACE THIS with an actual absolute path if needed for your setup.

# --- Define your database schema here ---
db_schema_info = """
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

You can execute SQL queries based on the schema above.
For example, to get all laws, you can say 'SELECT * FROM laws;'.
"""
# --- End of database schema ---

data_spec="""
----- 
# 法律語法形式化 (Ver. 3.2 初版程式後)

## **一、核心想法：讓法律「不只人能懂，電腦也能透徹理解」**

我們的核心目標是升級法律的「可讀性」，不只是讓人們更容易理解法律，更要讓電腦也能夠像法律專家一樣，**透徹理解法律的結構、意涵、以及彼此之間的關聯性**。

**為什麼這個想法很重要？**

*   **突破自然語言的限制：**  傳統法律文件以自然語言寫成，人類閱讀理解沒問題，但電腦卻難以有效處理。 形式化就是要把自然語言的法律，轉換成電腦能直接處理的 **結構化資料**，讓法律知識不再只是「文字」，而是可以被電腦 **運算、分析、推理** 的「知識」。
*   **釋放 AI 在法律領域的潛力：**  有了結構化的法律知識，AI 才能真正深入法律領域，不再只是做簡單的關鍵字檢索。  AI 可以進行更複雜的法律分析、自動化合規檢查、智慧法律諮詢、甚至輔助法律制定，大幅提升法律工作的效率和品質。
*   **打造更智慧的法律體系：**  當法律知識被形式化、結構化之後，我們可以建構出一個更智慧的法律體系，讓法律知識更容易被存取、應用、更新、迭代，最終目標是建立一個更有效率、更公平、更貼近人民需求的法律環境。

## **二、架構設計：五層 Meta Data + 多模組協作，打造全方位法律知識引擎**

我們的架構設計，採用 **「五層 Meta Data + 多模組協作」** 的模式，將法律知識拆解成不同層次，並透過多個 Python 模組協作，打造一個全方位的法律知識引擎。

### **整體架構可以概括為五個核心層次 (Meta Data 類型)：**

1.  **法規 Meta Data (Law Meta Data)：**  【**巨觀概覽**】  提供整部法規的 **最上層、最巨觀** 的資訊，像是法規的「基本身份資料」，包括法規名稱、類別、主管機關、立法目的、標籤、相關法規、台灣觀點、法規權責、法規時間軸等等。  就像是法律的「百科名片」，讓電腦快速掌握法規的整體輪廓。

2.  **法條 Meta Data (Article Meta Data)：**  【**微觀解構**】  針對每一條法條，提供 **最微觀、最細緻** 的資訊，深入解構法條的「法律意涵」，包括條號、條文內容、適用情境、處理程序、法律效果、法律概念、標籤、法條關聯性、法律規則等等。  就像是法律的「DNA」，讓電腦深入理解每一條法條的構成要素和功能。

3.  **法律概念 Meta Data (Legal Concept Meta Data)：**  【**詞彙中心**】  獨立於法條之外，建立一個 **法律概念詞彙庫**，針對法律中重要的專業術語和概念進行標準化定義和解釋，包括詞彙名稱、定義、相關概念、相關法條、概念類別、同義詞、台灣觀點、範例、語意向量等等。  就像是法律的「詞彙表」和「知識圖譜」，讓電腦掌握法律的「共通語言」。

4.  **法規關聯性 Meta Data (Law Relationship Meta Data)：**  【**網絡連結**】  描述不同法規之間、法條與法規之間、以及法條與法條 (跨法規) 之間的 **外部關聯性**，包括關聯類型、主法規、關聯法規、關聯說明、台灣觀點等等。  就像是法律的「人脈網絡」，讓電腦理解法律之間互相引用、補充、定義的複雜關係。

5.  **法規階層關係 Meta Data (Law Hierarchy Relationship Meta Data)：**  【**體系結構**】  描述《政府採購法》與其他相關法規之間的 **階層關係**，例如子法規、上位概念、補充法規、參考法規等等，呈現法規體系內的結構性關聯，包括關係代號、主法規、關聯法規、階層關係類型、關聯說明、台灣觀點等等。  就像是法律的「組織架構圖」，讓電腦理解法律體系內部的權力結構和位階關係。

### **五層 Meta Data 之間彼此協作，共同構成一個完整的法律知識引擎，關係如下：**

*   **法規 Meta Data** 作為 **核心容器**，統轄整部法規的所有 Meta Data。
 Data**。
*   **法律概念 Meta Data** 提供法律詞彙的標準化定義，被 **法條 Meta Data 引用**，也作為 **語意分析** 的基礎。
*   **法規關聯性 Meta Data** 描述法規之間、法條之間的 **外部關聯性**，被 **法規 Meta Data 引用**，也用於 **跨法規分析**。
*   **法規階層關係 Meta Data** 描述法規在法律體系中的 **階層結構**，被 **法規 Meta Data 引用**，用於 **法律體系宏觀分析**。
* *法條 Meta Data** 是 **核心內容**，詳細描述每一條法條，並連結到 **法律概念 Meta Data** 和 **法條關聯性總覽 Meta
*   **程序流程圖 Meta Data** 和 **法規語意向量 Meta Data**  作為 **輔助分析資料**，被 **法規 Meta Data 引用**，用於 **程序模型建構** 和 **語意分析** 模組。

## **三、Meta Data 種類與範例 (Ver. 3.1 )**

以下分別說明這五種 Meta Data 的種類與範例 (以政府採購法為例)：

### **1. 法規 Meta Data (Law Meta Data)：【巨觀概覽，法律百科名片】**

*   **目的：** 提供整部法規的 **巨觀概覽資訊**，讓電腦快速掌握法規的基本輪廓。
*   **主要欄位：** (JSON 格式)

    ```json
    {
      "代號": "[法規 UUID 代號]",
      "法規名稱": "[法規完整名稱] (lawName)",
      "法規類別": "[法規類別，例如：法律、命令、行政規則] (lawCategory)",
      "法規詳細類別": {  //  🌟 新增：法規詳細類別 (lawDetailedCategory)
        "法律領域": "[法律領域分類，例如：行政法、民法]",
        "法律位階": "[法律位階分類，例如：法律、命令]",
        "主管機關": "[主管機關分類，例如：行政院、立法院]"
      },
      "法規版本": "[法規版本資訊] (lawVersion)",
      "主管機關": "[法規主管機關] (competentAuthority)",
      "簡述": "[法規簡短描述或立法目的] (summary)",
      "標籤": [  // (tags)
        "[標籤1]",
        "[標籤2]",
        "..."
      ],
      "相關法規": [  // (relatedLaws)
        "[相關法規1名稱]",
        "[相關法規2名稱]",
        "..."
      ],
      "台灣觀點": "[從台灣法律觀點對法規的簡要描述] (taiwanPerspective)",
      "法規權責": {  //  🌟 新增：法規權責 (lawAuthority)
        "立法機關": "[制定法規的立法機關/發布機關]",
        "主管機關": "[負責解釋、執行、管理法規的行政機關]",
        "施行機關": "[實際執行法規的機關]",
        "授權依據": "[若是子法規/行政規則，其母法授權/法源依據，沒有則留空]"
      },
      "法規時間軸": {  //  🌟 新增：法規時間軸 (lawTimeline)
        "公布日期": "[法規公布日期，YYYY-MM-DD]",
        "施行日期": "[法規施行日期，YYYY-MM-DD]",
        "修正歷史": [ // JSON 陣列記錄歷次修正
          {
            "修正日期": "[修正日期，YYYY-MM-DD]",
            "修正重點": "[簡述本次修正重點]"
          },
          // ...  其他修正紀錄
        ],
        "廢止日期": "[法規廢止日期，若未廢止則留空，YYYY-MM-DD]"
      },
      "程序流程圖": "[Mermaid 語法或其他格式的程序流程圖描述字串]", //  🌟 新增：法規層級程序流程圖 (procedureFlowchart)
      "法規語意向量": "[整部法規的語意向量表示，例如字串或指向向量檔案的連結]" // 🌟 新增：法規層級語意向量 (lawSemanticVector) - **Note: 實際向量資料可能不直接放在 JSON 中，這裡僅為示意**
    }
    ```

*   **JSON 範例 (政府採購法):**

    ```json
{
  "代號": "LT_政府採購法",
  "法規名稱": "政府採購法",
  "法規類別": "法律",
  "法規詳細類別": {
    "法律領域": "行政法 - 經濟行政",
    "法律位階": "法律",
    "主管機關": "行政院公共工程委員會"
  },
  "法規版本": "現行版本 (民國 108 年 05 月 22 日修正)",
  "主管機關": "行政院公共工程委員會",
  "簡述": "為建立政府採購制度，依公平、公開之採購程序，提升採購效率與功能，確保採購品質，並維護公共利益及公平合理之採購環境，特制定本法。",
  "標籤": [
    "政府採購",
    "公共工程",
    "招標",
    "決標",
    "履約管理",
    "驗收",
    "爭議處理",
    "採購人員",
    "廠商"
  ],
  "相關法規": [
    "政府採購法施行細則",
    "採購申訴審議委員會組織準則",
    "工程施工查核小組組織準則",
    "採購稽核小組組織準則",
    "共同供應契約實施辦法",
    "電子採購作業辦法",
    "最有利標評選辦法",
    "機關辦理選擇性招標資格審查作業注意事項",
    "機關辦理工程採購廠商評選委員會組織準則暨評選辦法",
    "機關委託專業服務廠商評選及計費辦法",
    "機關委託技術服務廠商評選及計費辦法",
    "機關委託資訊服務廠商評選及計費辦法",
    "機關辦理社會福利服務採購評選辦法",
    "機關辦理設計競賽廠商評選辦法",
    "機關辦理藝文採購監督管理辦法",
    "中小企業扶助辦法",
    "優先採購環境保護產品辦法"
  ],
  "台灣觀點": "《政府採購法》是台灣公共部門進行採購行為的最重要法律依據，規範了從招標、決標、履約、驗收到爭議處理等各個環節，旨在建立公平、公開、效率的採購制度，防止弊端，提升公共工程品質，是台灣法制體系中非常重要的一部法律。",
  "法規權責": {
    "立法機關": "立法院",
    "主管機關": "行政院公共工程委員會",
    "施行機關": "各級政府機關、公立學校、公營事業",
    "授權依據": null
  },
  "法規時間軸": {
    "公布日期": "1999-05-27",
    "施行日期": "2000-05-27",
    "修正歷史": [
      {
        "修正日期": "2001-01-10",
        "修正重點": "修正第七條條文"
      },
      {
        "修正日期": "2002-02-06",
        "修正重點": "大幅度修正，包含第六、十一、十三、二十、二十二...等多條條文，並增訂多條條文及刪除第六十九條條文"
      },
      {
        "修正日期": "2007-07-04",
        "修正重點": "修正第八十五條之一條文"
      },
      {
        "修正日期": "2011-01-26",
        "修正重點": "修正第十一、五十二、六十三條條文"
      },
      {
        "修正日期": "2016-01-06",
        "修正重點": "修正第八十五條之一、八十六條條文；增訂第七十三條之一條文"
      },
      {
        "修正日期": "2019-05-22",
        "修正重點": "本次修正條文較多，包含第四、十五、十七、二十二...等條文，並增訂第十一條之一、二十六條之一、七十條之一條文"
      }
    ],
    "廢止日期": null
  },
  "程序流程圖": ",
  "法規語意向量": "[政府採購法整部法規的語意向量表示字串或檔案連結，例如：gpa_law_semantic_vector_v1.0.vec]"
}
    ```

### **2. 法條 Meta Data (Article Meta Data)：【微觀解構，法律DNA】**

*   **目的：** 提供每一條法條的 **詳細資訊**，深入解構法條的法律意涵和關聯性。
*   **主要欄位：** (JSON 格式)

    ```json
    {
      "代號": "[法條 UUID 代號]",
      "條號": "[法條條號，例如：第一條] (articleNumber)",
      "條文內容": "[完整的法條文字] (articleContent)",
      "法律意涵": {  // (legalMeaning)
        "適用情境": "[法條主要適用的情況或背景]",
        "處理程序": "[法條規定的具體處理步驟或流程]",
        "法律效果": "[法條產生的法律效果或影響]",
        "法律概念": [  // (legalConcepts)
          "[法律概念詞彙1]",
          "[法律概念詞彙2]",
          "..."
        ],
        "標籤": [  // (tags)
          "[法條標籤1]",
          "[法條標籤2]",
          "..."
        ]
      },
      "法條關聯性": {  // (articleRelationships)
        "上位概念": ["[上位概念法條條號列表]"],
        "下位概念": ["[下位概念法條條號列表]"],
        "引用關係": ["[引用關係法條條號列表]"],
        "定義關係": ["[定義關係法條條號列表]"],
        "程序關係": ["[程序關係法條條號列表]"],
        "補充關係": ["[補充關係法條條號列表]"],
        "例外關係": ["[例外關係法條條號列表]"],
        "構成要件關係": ["[構成要件關係法條條號列表]"],
        "其他關聯": ["[其他關聯法條條號列表]"]
      },
      "法律規則": [ // 🌟 新增：法條層級法律規則 (lawRules)
        {
          "規則代號": "[法律規則 UUID 代號]",
          "規則描述": "[簡述規則目的/指引]",
          "規則類型": "[IF-THEN / 邏輯規則 / 決策樹 / 指引]",
          "規則內容": "[文字描述規則內容/指引內容]",
          "規則來源": "[指向法條條號/點次]",
          "台灣觀點": "[從台灣法律觀點補充說明，可選填]"
        }
        // ... 其他法律規則
      ],
        "法條時間軸": {  //  🌟 新增：法條時間軸 (articleTimeline)
          "修正歷史": [ // JSON 陣列記錄法條歷次修正
            {
              "修正日期": "[修正日期，YYYY-MM-DD]",
              "修正重點": "[簡述本次法條修正重點]"
            },
          // ...  其他法條修正紀錄
        ],
      }
    }
    ```

*   **JSON 範例 (政府採購法 第二條):**

    ```json
{
    "代號": "LA_政府採購法_第二條",
    "條號": "第二條",
    "條文內容": "本法所稱採購，指工程之定作、財物之買受、定製、承租及勞務之委任或僱傭等。",
    "法律意涵": {
      "適用情境": "界定本法所稱「採購」之定義範圍。",
      "處理程序": null,
      "法律效果": "明確本法規範對象，確立「採購」行為之類型。",
      "法律概念": [
        "採購",
        "工程",
        "定作",
        "財物",
        "買受",
        "定製",
        "承租",
        "勞務",
        "委任",
        "僱傭"
      ],
      "標籤": [
        "定義",
        "採購範圍",
        "核心概念"
      ]
    },
    "法條關聯性": {
      "上位概念": [
        "第一條"
      ],
      "下位概念": [
        "第七條",
        "第八條",
        "第九條"
      ],
      "引用關係": [],
      "定義關係": [
        "第七條",
        "第八條"
      ],
      "程序關係": [],
      "補充關係": [],
      "例外關係": [],
      "構成要件關係": [],
      "其他關聯": []
    },
    "法律規則": [
      {
        "規則代號": "rule-gpa-002-01",
        "規則描述": "採購定義規則",
        "規則類型": "定義規則",
        "規則內容": "採購包含：工程之定作、財物之買受、定製、承租及勞務之委任或僱傭等行為。",
        "規則來源": "第二條",
        "台灣觀點": "本條定義為理解政府採購法適用範圍的起點，後續條文皆以此定義為基礎展開。"
      }
    ],
    "法條時間軸": {
      "修正歷史": []
    }
  }
    ```


### **3. 法律概念 Meta Data (Legal Concept Meta Data)：【詞彙中心，法律詞彙表】**

*   **目的：** 建立 **法律概念詞彙庫**，提供法律術語的標準化定義和解釋。
*   **主要欄位：** (JSON 格式)

    ```json
    {
      "代號": "[法律概念 UUID 代號]",
      "詞彙名稱": "[法律概念的名稱] (conceptName)",
      "定義": "[法律概念的簡潔定義] (definition)",
      "相關概念": ["[相關法律概念列表] (relatedConcepts)"],
      "相關法條": ["[相關法條條號列表] (relatedArticles)"],
      "概念類別": "[概念的分類] (conceptCategory)",
      "同義詞": ["[同義詞列表] (synonyms)"],
      "台灣觀點": "[從台灣法律觀點對概念的補充說明] (taiwanPerspective)",
      "範例": "[概念的具體範例] (example)",
      "語意向量": "[法律概念詞彙的語意向量表示，例如字串或指向向量檔案的連結]" //  🌟 新增：法律概念語意向量 (conceptSemanticVector) - **Note: 實際向量資料可能不直接放在 JSON 中，這裡僅為示意**
    }
    ```

*   **JSON 範例 (法律概念：採購):**

    ```json
  {
    "代號": "LC_政府採購法_採購",
    "詞彙名稱": "採購",
    "定義": "指機關為取得工程、財物或勞務，所為之訂約行為。",
    "相關概念": [
      "工程",
      "財物",
      "勞務",
      "定作",
      "買受",
      "定製",
      "承租",
      "委任",
      "僱傭",
      "契約"
    ],
    "相關法條": [
      "第二條",
      "第三條",
      "第七條"
    ],
    "概念類別": "核心概念 - 定義",
    "同義詞": [
      "購買",
      "購置",
      "發包",
      "辦理採購"
    ],
    "台灣觀點": "在台灣的《政府採購法》體系中，「採購」是整個法律的核心概念，所有規範都圍繞著機關如何合法、公平、有效率地進行採購行為。其定義範圍廣泛，涵蓋了各種政府取得所需資源的方式。",
    "範例": "政府機關為了興建新的辦公大樓（工程之定作）、購買辦公桌椅（財物之買受）、委託律師事務所提供法律諮詢服務（勞務之委任），都屬於政府採購法所規範的「採購」行為。",
    "語意向量": "[ '採購' 法律概念的語意向量表示字串或檔案連結，例如：concept_procurement_vec_v1.0.vec ]"
  }
    ```

### **4. 法規階層關係 Meta Data (Law Hierarchy Relationship Meta Data)：【體系結構，法律組織圖】**

*   **目的：** 描述《政府採購法》與其他相關法規之間的 **階層關係**，呈現法規體系內的結構性關聯。
*   **主要欄位：** (JSON 格式)

    ```json
    {
      "關係代號": "[法規階層關係 UUID 代號]",
      "主法規": "[主法規/行政規則 名稱] (primaryLaw)", //  調整：主法規 擴展為更通用的 "主法規/行政規則 名稱"
      "關聯法規": "[關聯法規/行政規則 名稱] (relatedLaw)", //  調整：關聯法規 擴展為更通用的 "關聯法規/行政規則 名稱"
      "階層關係類型": "[子法規 / 上位概念 / 補充法規 / 參考法規 / 平行法規 / 下位行政規則 / 補充行政規則 / 參考行政規則] (hierarchyType)", // 🌟 調整：階層關係類型 擴展到包含行政規則的階層關係類型
      "關聯說明": "[詳細描述階層關係] (relationshipDescription)",
      "台灣觀點": "[從台灣法律觀點補充說明] (taiwanPerspective)"
    }
    ```

*   **JSON 範例 (政府採購法 - 政府採購法施行細則 子母法關係):**

    ```json
  {
    "關係代號": "LH_政府採購法_政府採購法施行細則",
    "主法規": "政府採購法",
    "關聯法規": "政府採購法施行細則",
    "階層關係類型": "子法規",
    "關聯說明": "《政府採購法施行細則》是《政府採購法》的授權子法，依據母法第一百一十三條授權訂定，詳細規範母法中原則性條文的具體執行細節與操作程序。",
    "台灣觀點": "在台灣的法制體系下，施行細則扮演著落實法律、方便實務操作的重要角色。《政府採購法施行細則》與《政府採購法》母法共同構成完整的政府採購法規範體系，實務上兩者必須互相參照適用。"
  }
    ```


### **5. 法規關聯性 Meta Data (Law Relationship Meta Data)：【網絡連結，法律人脈網】**

*   **目的：** 描述不同法規之間、法條與法規之間、法條與法條 (跨法規) 之間的 **外部關聯性**。
*   **主要欄位：** (JSON 格式)

    ```json
    {
      "代號": "[法規關聯性 UUID 代號]",
      "關聯類型": "[法規-法規 / 法條-法規 / 法條-法條 / 法規-行政規則 / 法條-行政規則 / 行政規則-行政規則 / 行政規則-法條] (relationshipType)", //  🌟 調整：關聯類型 擴展到包含行政規則的各種關聯類型
      "主法規": "[主法規/行政規則 名稱] (primaryLaw)", //  調整：主法規  擴展為更通用的 "主法規/行政規則 名稱"
      "主法規條號": "[主法規/行政規則 條號/點次，若為法規-法規/法規-行政規則關聯則留空] (primaryArticleNumber)", //  調整：主法規條號 擴展為更通用的 "主法規/行政規則 條號/點次"
      "關聯法規": "[關聯法規/行政規則 名稱] (relatedLaw)", //  調整：關聯法規 擴展為更通用的 "關聯法規/行政規則 名稱"
      "關聯法規條號": "[關聯法規/行政規則 條號/點次，若為法規-法規/法條-法規/法規-行政規則/行政規則-行政規則/法條-行政規則關聯則留空] (relatedArticleNumber)", // 調整：關聯法規條號 擴展為更通用的 "關聯法規/行政規則 條號/點次"
      "關聯說明": "[簡述關聯性] (relationshipDescription)",
      "台灣觀點": "[從台灣法律觀點補充說明] (taiwanPerspective)"
    }
    ```

*   **JSON 範例 (政府採購法 - 政府採購法施行細則 子法規關聯):**

    ```json
  {
    "代號": "LR_政府採購法_9",
    "關聯類型": "法條-法規",
    "主法規": "政府採購法",
    "主法規條號": "第五十六條",
    "關聯法規": "最有利標評選辦法",
    "關聯法規條號": null,
    "關聯說明": "法條授權子法規",
    "台灣觀點": "《政府採購法》第五十六條授權訂定最有利標之評選辦法，而《最有利標評選辦法》即為落實此授權之法規命令，詳細規範最有利標之評選程序與標準。"
  }
    ```


## **四、操作步驟：從法規條文到 Meta Data (Ver 3.1)**

未來你只需要放入新的法規條文 (或行政規則)，就可以依照以下步驟進行「法律語法形式化」：

1.  **取得法規/行政規則條文：**  取得目標法規或行政規則的完整條文內容 (TXT 格式)。

2.  **建立法規 Meta Data：**  根據[政府採購法]的整體資訊，按照法律語法形式化的設計，依照裡面範例格式，產生 Meta data

3.  **建立法律概念 Meta Data：**  在建立法條 Meta Data 的過程中，你會不斷遇到重要的法律概念詞彙。 將這些詞彙整理出來，針對每一個法律概念，填寫法律概念 Meta Data 的各個欄位 (詞彙名稱、定義、相關概念、相關法條、概念類別、同義詞、台灣觀點、範例、語意向量)，建立法律概念詞彙庫。 **[提示：「定義」和「語意向量」欄位可考慮使用 LLM 輔助生成]**

4.  **建立法規階層關係 Meta Data：**  分析目標法規/行政規則與其他相關法規之間的階層關係 (子法規、上位概念、補充法規等)，填寫法規階層關係 Meta Data。 **[提示：法規階層關係的判斷，建議以法律專家人工判斷為主，LLM 可輔助提供建議]**

5.  **逐條建立法條 Meta Data：**  針對法規/行政規則中的每一條條文 (或要點、指引)，進行以下步驟：
    *   填寫法條 Meta Data 的基本欄位 (代號、條號、條文內容)。
    *   詳細分析 **"法律意涵"**，結構化描述條文的適用情境、程序、效果、法律概念、標籤等資訊。 **[提示：「法律意涵」的各個子欄位，可考慮使用 LLM 輔助分析和填寫]**
    *   仔細判斷 **"法條關聯性"**，標註條文與其他法條之間的各種關聯類型 (上位概念、下位概念、引用關係、定義關係、程序關係、補充關係、例外關係、構成要件關係、其他關聯)。 **[提示：法條關聯性可考慮使用 LLM 輔助分析和標註]**
    *   針對 **"法律規則"** 欄位，將法條中蘊含的法律規則 (IF-THEN 規則、邏輯規則、決策樹規則、或指引) 結構化地描述出來。 **[提示：法律規則的提取和表示，可考慮使用 LLM 輔助，並參考先前提供的法律規則表示範例]**
6.  **建立法條關聯性總覽 Meta Data：**  彙整在建立法條 Meta Data 時標註的法條關聯性資訊，整理成法條關聯性總覽 Meta Data，呈現整部法規/行政規則的法條關係網絡。  **[提示：法條關聯性可考慮使用 LLM 輔助分析和標註]**
7.  **建立程序流程圖 Meta Data：**  針對法規/行政規則中規範的程序流程，使用 Mermaid 語法或其他圖形化方式，繪製程序流程圖，並將描述字串填寫到法規 Meta Data 的 `程序流程圖` 欄位。 **[提示：程序流程圖的繪製，可先以人工為主，未來可考慮使用 NLP 技術和 LLM 輔助自動生成]**

8.  **建立法規語意向量 Meta Data 和法律概念語意向量 Meta Data：**  使用詞向量模型 (Word Embeddings) 或句向量模型 (Sentence Embeddings) 等 NLP 技術，將整部法規/行政規則的文本，以及法律概念詞彙庫中的每一個詞彙，轉換成語意向量，並將向量資料 (或向量檔案連結) 填寫到法規 Meta Data 的 `法規語意向量` 欄位和法律概念 Meta Data 的 `語意向量` 欄位。 **[提示：語意向量的生成，可使用 Python 的 Gensim, spaCy, Sentence-Transformers 等 NLP 函式庫]**

9.  **迭代與完善：**  Meta Data 的建立是一個持續迭代的過程。 完成初步建置後，可以邀請法律專家進行審核和驗證，並根據實際應用情況不斷完善和優化 Meta Data 的品質。  **[提示：Meta Data 的迭代完善，可以結合使用者回饋、AI 分析結果、以及法律專家的意見，不斷提升 Meta Data 的準確性和實用性]**

## **五、重要原則：實用、漸進、協作**

*   **實用性優先：**  我們的設計目標是為了實際應用，所以 Meta Data 的設計要以實用性為導向，優先處理常見、迫切的需求。
*   **逐步擴展：**  Meta Data 的建置是一個長期工程，不用追求一步到位，可以從小規模開始，逐步擴展範圍和深度。
*   **強調協作：**  法律語法形式化需要法律專業知識和技術的結合，強調法律專家、技術人員、以及使用者的共同參與和協作。

希望這份完整的設計說明能幫助你順利地將「法律語法形式化」方法應用於其他法規！ 如果你在實踐過程中遇到任何問題，或是有任何新的想法，都非常歡迎隨時提出來一起討論喔！
-----
"""
import os
postgres_host = os.environ.get('POSTGRES_HOST', 'postgres_host')
postgres_port = os.environ.get('POSTGRES_PORT', 'postgres_port')
postgres_password = os.environ.get('POSTGRES_PASSWORD', 'postgres_password')

root_agent = LlmAgent(
    model='gemini-2.5-flash-preview-04-17',#'gemini-2.0-flash',
    name='law_agent',
    instruction=f'Help the user query their PostgreSQL database byexecute SQL queries, retrieve data, but cannot modify data etc. sql command should follow database schema, when try to access json data, use json key defined in data spec. following is database schema, and meta data specification.  {db_schema_info}.{data_spec}',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",  # Argument for npx to auto-confirm install
                    "@modelcontextprotocol/server-postgres",
                    f"postgresql://root:{postgres_password}@{postgres_host}:{postgres_port}/zeabur",
                ],
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)

