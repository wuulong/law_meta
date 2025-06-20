# 法律元資料框架之系統架構與使用指南

## 1. 總覽

本系統「法律元資料框架」旨在將原始法律資料（來自 XML 彙編、文字檔等）轉換為儲存於 PostgreSQL 資料庫中，包含豐富元資料的結構化格式。系統首先透過 `law_proc.ipynb` 進行初始資料擷取與處理，將法律基本資訊、法條全文、摘要和關鍵字載入資料庫。隨後，`law_meta_loader.ipynb` 利用大型語言模型（LLMs，如 Google Gemini）及預定義的 `法律語法形式化.md` 規範，為資料庫中的法律生成或更新詳細的結構化元資料（五種 JSON 類型）。這些元資料亦儲存在資料庫中，並可選擇性地匯出為 JSON 檔案。最終，這些結構化的法律資料可用於法律分析、搜尋、知識圖譜建立等多種應用。

系統的核心是兩個 Jupyter Notebooks (`law_proc.ipynb` 和 `law_meta_loader.ipynb`) 與一個中央 PostgreSQL 資料庫，它們共同協調資料的匯入、處理、元資料生成、儲存和管理。

## 2. 系統架構

本系統由數個關鍵組件構成，這些組件相互作用以達成其目標：

**2.1. 核心組件：**

*   **`law_proc.ipynb`（資料擷取與處理引擎）：**
    *   此 Jupyter Notebook 作為初始資料擷取和處理引擎。
    *   主要功能是解析 XML 法律彙編檔案（例如，`FalV.xml`, `MingLing.xml`）。
    *   將基本的法律資訊（如 PCode、法律名稱、相關URL、分類、日期等）、法條全文、以及從外部檔案讀取的法律摘要和關鍵字，填充到 PostgreSQL 資料庫中。
    *   關鍵功能包括 `synchronize_lawmgr_with_db`（同步法律資料到資料庫）、`import_law_summaries`（匯入法律摘要）和 `import_law_keywords`（匯入法律關鍵字）。
*   **`law_meta_loader.ipynb`（詳細元資料生成與管理引擎）：**
    *   此 Jupyter Notebook 負責為已存在於 PostgreSQL 資料庫中的法律生成和管理詳細的、結構化的元資料（五種 JSON 類型：regulation, legal concepts, hierarchy relations, law relations, law articles）。
    *   它主要與 `law_proc.ipynb` 載入到資料庫的法律資料互動。
    *   使用大型語言模型（LLMs，如 Gemini）和 `法律語法形式化.md` 規範來生成或更新這些詳細元資料。
    *   生成的元資料會被儲存/更新到 PostgreSQL 資料庫中（例如，儲存在 `laws` 表的 `law_metadata` 欄位，以及概念、關係等相關聯的表中），並且也可以匯出為 JSON 檔案。
    *   關鍵的資料庫互動功能包括 `upsert_law_metadata_to_db`（將元資料新增或更新到資料庫）、`load_lm_from_db`（從資料庫載入法律元資料）、以及 `delete_law_metadata_from_db`（從資料庫刪除法律元資料）。
*   **PostgreSQL 資料庫：**
    *   作為法律資料的中央儲存庫。
    *   儲存內容包括原始法律文本、法條、法律摘要、關鍵字，以及由 `law_meta_loader.ipynb` 生成的結構化元資料。
*   **輸入 XML 檔案（例如 `FalV.xml`, `MingLing.xml`）：**
    *   這些是 `law_proc.ipynb` 用於批次載入法律資料到資料庫的主要來源檔案。
*   **輸入摘要/關鍵字檔案：**
    *   這些是 `law_proc.ipynb` 用於豐富資料庫中法律記錄的文字檔（TXT）或 CSV 檔案。
*   **規格文件（`法律語法形式化.md`）：**
    *   此 Markdown 檔案定義了系統旨在提取的五種元資料的綱要和結構。它作為 `law_meta_loader.ipynb` 中大型語言模型生成詳細元資料時的指導規範。
*   **輸出 JSON 檔案（`json/` 目錄）：**
    *   由 `law_meta_loader.ipynb` 生成。這些檔案可以視為從資料庫匯出的詳細元資料，或是直接從 LLM 處理後的輸出。每個已處理的法律會對應一組五個 JSON 檔案：
        *   `{law_name}_law_regulation.json`：包含關於該法律本身的一般元資料。
        *   `{law_name}_legal_concepts.json`：列出並定義在該法律中找到的關鍵法律概念。
        *   `{law_name}_hierarchy_relations.json`：描述此法律與其他法律之間的層級關係。
        *   `{law_name}_law_relations.json`：詳細說明此法律或其條文與其他法律或條文的其他類型關係。
        *   `{law_name}_law_articles.json`：提供法律中每個條文的詳細、結構化分解。
*   **暫存文字檔案（`txt/` 目錄）：**
    *   此目錄主要由 `law_meta_loader.ipynb` 在與 LLM 互動生成元資料時使用。來自大型語言模型的原始文本輸出（通常在 JSON Markdown 區塊內）會先儲存在此處，然後再解析並轉換，最終儲存到 PostgreSQL 資料庫或 `json/` 目錄中的 JSON 檔案。

**2.2. 資料處理與元資料生成流程：**

**步驟 1：初始批次匯入（使用 `law_proc.ipynb`）**
*   開發者準備 XML 法律彙編檔案（例如 `FalV.xml`）。
*   執行 `law_proc.ipynb`。
*   該 Notebook 解析 XML 檔案。
*   它將法律資料（法律、法條）同步到 PostgreSQL 資料庫。
*   （可選）執行 `import_law_summaries` 和 `import_law_keywords` 功能，將額外的法律摘要和關鍵字載入到資料庫中。

**步驟 2：詳細元資料生成/更新（使用 `law_meta_loader.ipynb`）**
*   開發者在資料庫中按 PCode 等唯一識別碼選定一個需要處理詳細元資料的法律。
*   設定 `law_meta_loader.ipynb` 以處理此特定法律。
*   可以使用 `LawMetadataMgr.load_lm_from_db()` 從資料庫載入該法律現有的元資料。
*   **若使用 LLM 生成元資料：**
    *   Notebook 為 LLM 準備必要的輸入（例如，從資料庫讀取的法律文本、`法律語法形式化.md`）。
    *   與 Gemini API 互動以生成五種類型的結構化元資料。
    *   生成的元資料（可暫時儲存在 `txt/` 和 `json/` 目錄中）隨後透過 `LawMetadataMgr` 的 `upsert_law_metadata_to_db()` 功能被新增或更新到 PostgreSQL 資料庫。此操作會更新相關的表和 JSONB 欄位。
*   **若管理現有元資料：**
    *   可以從資料庫載入元資料，進行修改，然後存回資料庫。

**步驟 3：輸出/取用**
*   結構化的元資料可直接在 PostgreSQL 資料庫中進行查詢。
*   `law_meta_loader.ipynb` 也可以將這些元資料匯出為每個法律對應的五個 JSON 檔案。

## 3. 使用指南

本系統的操作涉及兩個主要的 Jupyter Notebooks (`law_proc.ipynb` 和 `law_meta_loader.ipynb`) 以及 PostgreSQL 資料庫。

**3.1. 設定環境：**

*   確保已安裝 Python 和 PostgreSQL。
*   安裝必要的 Python 函式庫：
    *   對於 `law_proc.ipynb`：`psycopg2-binary` (或其他 PostgreSQL 驅動程式)，`lxml` (用於 XML 解析) 等。
    *   對於 `law_meta_loader.ipynb`：`google-generativeai` (用於 Gemini API)，`psycopg2-binary`，`json`，`re`，`os` 等。
    *   (請參閱各 Notebook 內的詳細相依性說明)
*   設定 PostgreSQL 資料庫，並確保網路連線和使用者權限正確。
*   若要使用 LLM 功能，設定您的 `GEMINI_API_KEY` 作為環境變數。

**3.2. 初始批次資料匯入 (使用 `law_proc.ipynb`)：**

1.  **準備輸入檔案：**
    *   將法律彙編 XML 檔案 (例如 `FalV.xml`, `MingLing.xml`) 放置於可存取的位置。
    *   （可選）準備法律摘要和關鍵字的文字檔或 CSV 檔案。
2.  **設定並執行 `law_proc.ipynb`：**
    *   開啟 `law_proc.ipynb`。
    *   設定資料庫連線參數。
    *   指定輸入 XML 檔案的路徑。
    *   執行 Notebook 中的相關儲存格以：
        *   解析 XML 檔案。
        *   使用 `synchronize_lawmgr_with_db` 功能將法律基本資料、法條等同步到 PostgreSQL 資料庫。
        *   （可選）執行 `import_law_summaries` 和 `import_law_keywords` 功能匯入額外資料。
3.  **驗證：** 檢查 PostgreSQL 資料庫，確認法律資料已成功匯入。

**3.3. 詳細元資料生成與管理 (使用 `law_meta_loader.ipynb`)：**

1.  **選擇目標法律：** 在資料庫中確定一個或多個需要生成或更新詳細元資料的法律 (例如，透過其 PCode)。
2.  **設定 `law_meta_loader.ipynb`：**
    *   開啟 `law_meta_loader.ipynb`。
    *   設定資料庫連線參數。
    *   在 Notebook 中指定目標法律的 PCode(s)。
3.  **執行操作：**
    *   **載入現有元資料 (若有)：** 可使用 `LawMetadataMgr.load_lm_from_db(pcode)` 從資料庫載入現有元資料進行檢視或修改。
    *   **使用 LLM 生成新元資料：**
        *   確保 `法律語法形式化.md` 已準備好並可供 Notebook 存取。
        *   執行相關儲存格以：
            *   從資料庫提取法律文本作為 LLM 的輸入。
            *   與 Gemini API 互動，根據 `法律語法形式化.md` 生成五種結構化元資料。
            *   （可選）生成的 LLM 文字輸出可暫存於 `txt/` 目錄。
            *   使用 `LawMetadataMgr.upsert_law_metadata_to_db()` 將生成或更新的元資料儲存回 PostgreSQL 資料庫。
    *   **修改並儲存元資料：** 對於已載入的元資料，可以直接在 Notebook 中修改 Python 物件，然後使用 `upsert_law_metadata_to_db()` 將變更存回資料庫。
    *   **刪除元資料：** 可使用 `LawMetadataMgr.delete_law_metadata_from_db(pcode)` 從資料庫中刪除特定法律的元資料。
    *   **匯出 JSON 檔案 (可選)：** 可以使用 `LawMetadata.to_json_files()` 或類似功能將資料庫中的元資料匯出為 JSON 檔案到 `json/` 目錄。
4.  **驗證：** 檢查 PostgreSQL 資料庫確認元資料已更新，或檢查 `json/` 目錄（如果執行了匯出）。

**3.4. 主要 Python 類別 (主要在 `law_meta_loader.ipynb` 中使用)：**

*   **`LawMetadata`**：
    *   代表單一法律的所有五種結構化元資料。
    *   `from_db_record()`: (假設) 類別方法，用於從資料庫記錄載入元資料。
    *   `to_json_files()`: 將元資料匯出為 JSON 檔案的方法。
    *   `renew_id()`: 標準化和更新元資料中唯一識別碼的方法。
    *   (可能包含其他與資料庫互動或資料轉換相關的方法)
*   **`LawMetadataMgr`**：
    *   管理 `LawMetadata` 物件的集合，並協調與資料庫的互動。
    *   `load_lm_from_db(pcode)`: 從資料庫載入特定法律的元資料。
    *   `upsert_law_metadata_to_db(law_metadata_obj)`: 將單一法律的元資料新增或更新到資料庫。
    *   `delete_law_metadata_from_db(pcode)`: 從資料庫刪除特定法律的元資料。
    *   (可能包含批次處理資料庫操作的方法)

**3.5. 資料查詢與取用：**

*   主要透過 PostgreSQL 資料庫進行結構化查詢。
*   `law_meta_loader.ipynb` 可能包含一些使用 Python 查詢和分析資料庫中元資料的範例。
*   匯出的 JSON 檔案可用於離線分析或與其他系統整合。

## 4. 主要功能

*   **批次資料匯入與處理：** `law_proc.ipynb` 能夠從 XML 檔案批次匯入法律資料，並處理摘要與關鍵字檔案，將基礎資料載入 PostgreSQL 資料庫。
*   **大型語言模型驅動的詳細元資料生成：** `law_meta_loader.ipynb` 利用 Gemini 等 LLMs，根據 `法律語法形式化.md` 規範，為已存於資料庫的法律生成詳細的結構化元資料。
*   **資料庫中心化儲存：** PostgreSQL 資料庫作為核心，儲存所有法律文本、法條、摘要、關鍵字以及由 `law_meta_loader.ipynb` 生成的五種結構化元資料。
*   **全面的元資料綱要：** 系統定義並擷取五種主要類型的法律元資料：法規概述、法律概念、層級結構、法律間關係以及詳細的條文分解。
*   **彈性的元資料管理：** `law_meta_loader.ipynb` 中的 Python 類別支援從資料庫載入、更新元資料，並將其存回資料庫，同時也支援匯出為 JSON 檔案。
*   **ID 管理：** 系統包含為不同元資料元素生成和更新唯一 ID 的功能，確保資料一致性。
*   **條文批次處理（LLM）：** `law_meta_loader.ipynb` 在透過 LLM 生成條文元資料時，能分塊處理長篇法律文件。
*   **資料庫查詢與輸出：** 結構化資料可直接在 PostgreSQL 中查詢，亦可透過 `law_meta_loader.ipynb` 匯出為 JSON 檔案。
*   **可擴展性：** 以 Python、PostgreSQL 和結構化 JSON/資料庫綱要為基礎，有利於未來擴展分析工具與應用。

## 5. 目錄結構摘要

*   **`/` (根目錄)：**
    *   `law_proc.ipynb`：資料擷取與初始處理筆記本。
    *   `law_meta_loader.ipynb`：詳細元資料生成與管理筆記本。
    *   `法律語法形式化.md`：元資料規格文件。
    *   `*.xml`：輸入的法律彙編 XML 檔案（例如 `FalV.xml`），供 `law_proc.ipynb` 使用。
    *   （可選）包含法律摘要或關鍵字的 `*.txt` 或 `*.csv` 檔案，供 `law_proc.ipynb` 使用。
    *   `sw_arch.md`：本文件。
*   **`json/`：** （可選）包含由 `law_meta_loader.ipynb` 從資料庫匯出的 JSON 元資料檔案。主要元資料儲存於 PostgreSQL 資料庫。
*   **`txt/`：** 主要由 `law_meta_loader.ipynb` 在與 LLM 互動生成元資料時使用，作為儲存原始文本輸出的暫存空間，處理後資料主要存入資料庫。

本文件提供了系統架構和使用的概況。有關更詳細的範例和具體的實作細節，請參閱 `law_proc.ipynb` 和 `law_meta_loader.ipynb` 筆記本中的註解和程式碼。
