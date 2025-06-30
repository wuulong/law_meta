# 法律元資料框架之系統架構與使用指南

## 1. 總覽

本系統「法律元資料框架」旨在將法律文本轉換為結構化、機器可讀的格式。整個處理流程分為兩個主要階段，由兩個核心 Jupyter Notebook 協調完成：

1.  **第一階段：基礎資料載入與初步處理 (`law_proc.ipynb`)**
    *   此階段為整個處理流程的**起點**。它負責從「全國法規資料庫」的原始 XML 檔案中讀取法規資料，進行初步的結構化處理，並將法規、法條等基本資訊載入到 PostgreSQL 資料庫中。隨後，它會更新法規的摘要及關鍵字等資訊。

2.  **第二階段：深度元資料生成與擴充 (`law_meta_loader.ipynb`)**
    *   在 `law_proc.ipynb` 完成基礎資料庫的建立與更新後，此階段利用大型語言模型（LLMs），特別是 Google 的 Gemini 模型，對法律文本進行深度分析。它根據預定義的 `法律語法形式化.md` 規範，生成五種詳細的元資料（法規、法律概念、層級關係、法律關係、法條分析），並將這些豐富的結構化資料以 JSON 格式儲存，同時更新至資料庫中。

這些結構化的元資料最終可用於多種目的，包括進階的法律分析、語意搜尋以及建立法律知識圖譜。

## 2. 系統架構

本系統由數個關鍵組件構成，這些組件相互作用以達成其目標：

**2.0. 系統架構 與 流程圖：**
```
graph TD
    subgraph "系統架構 System Architecture"
        A[輸入法律文件 .md 檔案] --> B(law_meta_loader.ipynb)
        C[規格文件 法律語法形式化.md] --> B
        D[全國法規資料庫 XML] --> E(law_proc.ipynb)
        E --> F(PostgreSQL 資料庫)
        B --> G[LLM Gemini]
        G --> H[暫存文字檔案 txt/ 目錄]
        H --> I[元資料 JSON 檔案 json/ 目錄]
        I --> F
        B --> F
        F -- 查詢/互動 --> J(A2A 代理)
        J --> F
    end

    subgraph "新法律處理流程 New Law Processing Flow"
        K[新法律 XML 檔案] --> L(law_proc.ipynb)
        L -- 基礎資料載入 --> M(PostgreSQL 資料庫)
        L -- 摘要/關鍵字匯入 --> M
        N[新法律 Markdown 檔案] --> O(law_meta_loader.ipynb)
        P[法律語法形式化.md] --> O
        O -- 提示生成 --> Q(LLM)
        Q -- 原始輸出 --> R[txt/ 目錄]
        R -- 解析 --> S[json/ 目錄]
        S -- 深度元資料同步 --> M
    end
```

**2.1. 核心組件：**

*   **法規資料處理 (`law_proc.ipynb`) - 流程起點：**
    *   此 Jupyter Notebook 是整個法律元資料處理流程的**第一步**。它主要負責處理來自「全國法規資料庫」的原始 XML 格式法律資料，並將其結構化、載入到記憶體中的管理物件，最終同步到 PostgreSQL 資料庫中。此步驟會填充資料庫中的基本法規和法條資訊，並在更新資料庫後，匯入摘要和關鍵字。
    *   **主要功能：**
        *   **XML 資料解析與結構化：** 從 XML 檔案中解析法規和命令的詳細資訊。
        *   **法律資料管理 (`LawMgr`)：** 將解析後的 XML 資料組織成易於程式存取的結構。
        *   **PostgreSQL 資料庫整合：** **主要負責初步填充法規和法條資料，並在更新資料庫後，匯入摘要和關鍵字**。
        *   **摘要和關鍵字匯入：** 從外部檔案讀取法規摘要和關鍵字並更新至資料庫。

*   **元資料生成引擎 (`law_meta_loader.ipynb`) - 流程核心：**
    *   此 Jupyter Notebook 是流程的**第二步**，負責將已有的法律文本轉換為深度結構化的元資料，並管理這些元資料的生命週期，包括與資料庫的互動。
    *   **主要功能：**
        *   **大型語言模型 (LLM) 互動：** 根據 `法律語法形式化.md` 規範，生成提示並解析 LLM 回應，將其轉換為結構化 JSON。
        *   **元資料物件模型：** 定義 `LawMetadata` 和 `LawMetadataMgr` 類別，支援從 JSON 檔案讀寫及資料庫載入。
        *   **資料庫整合 (PostgreSQL)：** 將 LLM 生成的五種深度元資料同步（Upsert/Delete）到資料庫，擴充 `law_proc.ipynb` 建立的基礎資料。
        *   **元資料分析工具：** 提供基於深度元資料的關鍵字搜尋、類別篩選及圖表生成等分析功能。

*   **輸入法律文件（`.md` 檔案）：**
    *   這些是包含法律或法規原始文本的 Markdown 檔案（例如，`政府採購法.md`）。它們是 `law_meta_loader.ipynb` 的主要輸入。
*   **規格文件（`法律語法形式化.md`）：**
    *   這個關鍵的 Markdown 檔案定義了系統旨在提取的五種元資料的綱要和結構。它為大型語言模型提供了生成準確且一致元資料的框架和範例。
*   **元資料 JSON 檔案（`json/` 目錄）：**
    *   `law_meta_loader.ipynb` 的結構化輸出儲存在每個已處理法律的一組五個 JSON 檔案中。這些檔案是資料庫更新的來源，也是一個獨立的資料備份。
        *   `{law_name}_law_regulation.json`
        *   `{law_name}_legal_concepts.json`
        *   `{law_name}_hierarchy_relations.json`
        *   `{law_name}_law_relations.json`
        *   `{law_name}_law_articles.json`

*   **A2A 代理啟動與測試 (`a2a_bringup.ipynb`)：**
    *   此 Jupyter Notebook 的主要目的是啟動和測試一個結合了 LLM 和 MCP 客戶端的代理 (agent)，展示如何讓 LLM 透過 MCP 客戶端與 PostgreSQL 資料庫進行互動查詢。

*   **暫存文字檔案（`txt/` 目錄）：**
    *   此目錄用作暫存區。來自大型語言模型的原始文本輸出會先儲存在此處，然後再解析並轉換為 `json/` 目錄中的最終 JSON 檔案。

**2.2. 服務部署與容器化 (Service Deployment & Containerization)：**

本系統利用 Docker 和 Docker Compose 進行服務的容器化部署，確保環境的一致性和部署的便捷性。核心服務定義在 `docker-compose.yml` 中：

*   **`db` 服務 (PostgreSQL 資料庫)：**
    *   容器名稱：`lawmeta-pg`
    *   功能：持久化儲存所有結構化後的法律元資料，包括基礎資料和深度元資料。
*   **`a2a` 服務 (應用程式代理)：**
    *   容器名稱：`a2a`
    *   功能：作為應用程式代理，負責與 PostgreSQL 資料庫互動，並可能提供對外 API 服務。

**2.3. 新法律處理的資料流程：**

1.  **基礎資料載入與初步處理 (law_proc.ipynb)：**
    *   執行 `law_proc.ipynb`。
    *   Notebook 會讀取指定的法規 XML 檔案，並將其解析後更新至 PostgreSQL 資料庫。
    *   隨後，它會讀取對應的摘要與關鍵字檔案，並將這些資訊更新至資料庫。

2.  **深度元資料生成與擴充 (law_meta_loader.ipynb)：**
    *   在 `law_proc.ipynb` 完成基礎資料的載入與更新後，執行 `law_meta_loader.ipynb`。
    *   此 Notebook 會將法律文本（通常是 Markdown 檔案，例如 `new_law.md`）和 `法律語法形式化.md`（規格）上傳到 Gemini 大型語言模型。
    *   Notebook 向 LLM 傳送提示，生成五種類型的深度元資料。

3.  **儲存與同步：**
    *   LLM 的回應會先暫存於 `txt/` 目錄，然後解析為 `json/` 目錄中的 JSON 檔案。
    *   最後，執行 `law_meta_loader.ipynb` 中的資料庫同步功能，將這些 JSON 檔案的內容更新至 PostgreSQL 資料庫中，完成整個流程。

**2.4. 測試與規格 (Testing & Specification)：**

本專案採用行為驅動開發 (BDD) 方法來定義系統功能和進行測試。

*   **功能描述檔案 (`.feature` 檔案)：**
    *   `project.feature` 和 `project_updated.feature` 使用 Gherkin ��法描述了系統應有的功能和行為。
*   **步驟定義 (`features/steps/steps.py`)：**
    *   此檔案包含了實現 `.feature` 檔案中行為描述的 Python 程式碼。

## 3. 使用指南

**3.1. 設定環境：**

*   確保已安裝 Python 及 Docker。
*   安裝必要的函式庫：`google-generativeai`、`psycopg2-binary` 等。
*   設定您的 `GEMINI_API_KEY` 作為環境變數。

**3.2. 處理新法律（完整流程）：**

1.  **執行 `law_proc.ipynb`：**
    *   開啟 `law_proc.ipynb`。
    *   依照 Notebook 中的指示，設定要處理的法規名稱。
    *   執行相關儲存格，將法規的 XML 解析後更新至資料庫，並載入摘要與關鍵字。
2.  **執行 `law_meta_loader.ipynb`：**
    *   將法規文本準備成 `.md` 檔案。
    *   開啟 `law_meta_loader.ipynb`。
    *   設定 `law_name` 變數。
    *   執行 LLM 生成的儲存格，產生 `json/` 檔案。
    *   執行資料庫同步的儲存格，將 `json/` 檔案的內容更新到資料庫.

**3.3. 管理與查詢現有元資料：**

*   `LawMetadataMgr` 類別可以從 `json/` 目錄或資料庫載入元資料。
*   Notebook 中提供了關鍵字搜尋、篩選、圖表生成等查詢範例。

**3.4. 主要 Python 類別：**

*   **`LawMetadata`**：代表單一法律的所有��度元資料。
*   **`LawMetadataMgr`**：管理 `LawMetadata` 物件的集合，支援從 JSON 或資料庫載入。

## 4. 主要功能

*   **兩階段處理流程：** 先載入基礎資料，再由 LLM 生成深度元資料，流程清晰。
*   **大型語言模型驅動的元資料提取：** 利用 Gemini 根據正式規格從原始法律文本中生成結構化元資料。
*   **全面的元資料綱要：** 擷取五種不同類型的法律元資料。
*   **資料持久性：** 將生成的元資料儲存在 JSON 檔案及 PostgreSQL 資料庫中。
*   **模組化元資料管理：** Python 類別允許載入、存取、修改和儲存元資料。

## 5. 目錄結構摘要

*   **`/` (根目錄)：**
    *   `law_proc.ipynb`：**流程起點**，用於載入基礎法規資料，並更新摘要與關鍵字。
    *   `law_meta_loader.ipynb`：**流程核心**，用於生成深度元資料，並更新至資料庫。
    *   `法律語法形式化.md`：元資料規格。
*   **`data/`：** 包含原始法律文本、摘要、關鍵字等資料檔案，以及法律的來源 Markdown 檔案（`*.md`）。
*   **`docker/`：** 包含 Docker 相關配置檔案，用於服務部署與容器化。
*   **`json/`：** 包含所有最終的結構化 JSON 元資料檔案。
*   **`txt/`：** LLM 原始文本輸出的暫存空間。
*   **`features/`：** BDD 測試相關檔案。

本文件提供了系統架構和使用的概況。有關更詳細的範例和具體的實作細節，請參閱 `law_proc.ipynb` 和 `law_meta_loader.ipynb` 筆記本中的註解和程式碼。



