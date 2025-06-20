# 開發者使用手冊：法律元資料框架 (how_to_use.md)

## 1. 前言

本文件為開發者提供如何使用「法律元資料框架」的實務指南。建議在閱讀本文件前，先熟悉 `sw_arch.md` 中描述的系統架構。本手冊將著重於具體的操作步驟、程式碼的運用以及系統的客製化與擴展。

## 2. 開發環境設定

確保您的開發環境符合以下要求：

*   **Python 版本：** 建議使用 Python 3.8 或更高版本。
*   **PostgreSQL 資料庫：**
    *   需要一個運行中的 PostgreSQL 伺服器。
    *   確保已建立系統所需的資料庫，並且擁有相關的登入憑證 (使用者名稱、密碼、主機、埠號)。
*   **必要的 Python 套件：**
    *   `google-generativeai`：用於與 Google Gemini API 互動 (主要由 `law_meta_loader.ipynb` 使用)。
    *   `psycopg2-binary`：PostgreSQL 的 Python 適配器，用於兩個筆記本與資料庫的連接。
    *   `lxml`：用於解析 XML 檔案 (主要由 `law_proc.ipynb` 使用)。
    *   `json`：處理 JSON 資料。
    *   `re`：使用正規表示式進行文本處理。
    *   `os`：與作業系統互動，如檔案路徑處理。
    *   您可以透過 pip 安裝：
        ```bash
        pip install google-generativeai psycopg2-binary lxml
        ```
*   **API 金鑰設定 (若使用 LLM 功能)：**
    *   若要使用 `law_meta_loader.ipynb` 中的 LLM 功能，您必須擁有一個 Google Gemini API 金鑰。
    *   將金鑰設定為環境變數 `GEMINI_API_KEY`。例如，在 Linux/macOS 的 shell 中：
        ```bash
        export GEMINI_API_KEY="您的API金鑰"
        ```
        或在 Windows PowerShell 中：
        ```powershell
        $Env:GEMINI_API_KEY="您的API金鑰"
        ```
        建議將此設定加入您的 shell 設定檔（如 `.bashrc`, `.zshrc`）或在啟動 Jupyter Notebook 的環境中設定。

## 3. 核心流程：資料庫建置與元資料管理

本節說明如何使用 `law_proc.ipynb` 和 `law_meta_loader.ipynb` 兩個核心筆記本來建構法規資料庫並管理其詳細元資料。

**3.1. 使用 `law_proc.ipynb` 建構與同步基礎法規資料庫**

此筆記本是系統的第一步，用於批次處理原始法規資料，並將其載入 PostgreSQL 資料庫。

**3.1.1. 輸入準備：**

*   **主要輸入 XML 檔案：**
    *   準備來自「全國法規資料庫」的 XML 彙編檔案，例如 `FalV.xml` (法規內容) 和 `MingLing.xml` (命令內容)。這些檔案應包含結構化的法規資訊。
    *   將這些 XML 檔案放置於專案根目錄或 `law_proc.ipynb` 可存取之路徑。
*   **可選摘要檔案：**
    *   例如 `summary_dir_law.md` 或其他文字檔案，其中包含法規的摘要資訊。摘要檔案的格式需與筆記本中的解析邏輯相符。
*   **可選關鍵字檔案：**
    *   例如 `keywords_law.csv` 或其他 CSV/文字檔案，包含法規的關鍵字。檔案格式需與筆記本中的解析邏輯相符。

**3.1.2. 環境與組態設定：**

*   **資料庫連線：** 在 `law_proc.ipynb` 筆記本的相關儲存格中，正確設定 PostgreSQL 資料庫的連線參數，包括：
    *   `DB_HOST`
    *   `DB_PORT`
    *   `DB_NAME`
    *   `DB_USER`
    *   `DB_PASSWORD`
*   確保 PostgreSQL 伺服器正在運行，且指定的資料庫已建立。

**3.1.3. 執行步驟：**

1.  **開啟 `law_proc.ipynb`。**
2.  **執行初始化儲存格：** 載入必要的函式庫和輔助函數。
3.  **設定資料庫連線：** 執行設定資料庫連線參數的儲存格。
4.  **解析 XML 檔案：**
    *   執行初始化 `LawMgr` 物件的儲存格 (例如 `lawmgr = LawMgr(db_params)`）。
    *   執行呼叫 `parse_xml_withobj(lawmgr, xml_file_path, law_type)` 的儲存格，其中 `xml_file_path` 指向您的 `FalV.xml` 或 `MingLing.xml`，`law_type` 指定法規類型。對每個主要 XML 檔案執行此步驟。
5.  **同步至資料庫：**
    *   執行呼叫 `synchronize_lawmgr_with_db(lawmgr)` 的儲存格。此步驟會將解析自 XML 的法規、法條等資訊寫入 PostgreSQL 資料庫。
6.  **匯入摘要 (可選)：**
    *   若有摘要檔案，執行呼叫 `import_law_summaries(lawmgr, summary_file_path)` 的儲存格。
7.  **匯入關鍵字 (可選)：**
    *   若有關鍵字檔案，執行呼叫 `import_law_keywords(lawmgr, keyword_file_path)` 的儲存格。

**3.1.4. 預期成果：**

*   PostgreSQL 資料庫中的相關表格 (例如 `laws`, `articles` 等) 被成功填充了來自 XML 的法規資料、法條全文，以及選擇性匯入的摘要和關鍵字。

**3.2. 使用 `law_meta_loader.ipynb` 產生與管理詳細元資料**

此筆記本用於處理已存在於 PostgreSQL 資料庫中 (通常由 `law_proc.ipynb` 匯入) 的法規，為其生成或管理詳細的五種類型元資料。

**3.2.1. 識別目標法規：**

*   您需要指定要處理的法規。這通常是透過法規的 PCode (唯一識別碼) 來完成，該 PCode 應已存在於資料庫中。
*   在 `law_meta_loader.ipynb` 中，找到設定目標法規 PCode 的變數，例如 `law_pcode_to_load`。

**3.2.2. 從資料庫載入資料：**

*   執行初始化 `LawMetadataMgr` 並設定資料庫連線的儲存格。
*   若要載入特定法規的現有元資料 (如果先前已生成並儲存)，使用以下方式：
    ```python
    # 假設 lmmgr 是已初始化的 LawMetadataMgr 物件並已連接資料庫
    law_pcode_to_load = "PCODE12345" # 替換為實際的 PCode
    lm_from_db = lmmgr.load_lm_from_db(law_pcode_to_load=law_pcode_to_load)
    if lm_from_db:
        print(f"成功從資料庫載入 {law_pcode_to_load} 的元資料。")
        # 現在 lm_from_db 物件（一個 LawMetadata 實例）包含了該法規的元資料
    else:
        print(f"在資料庫中找不到 {law_pcode_to_load} 的元資料。")
    ```

**3.2.3. 基於 LLM 的元資料生成 (若適用)：**

*   如果目標法規在資料庫中只有基本資訊，而您需要首次為其生成詳細的五種元資料：
    *   **設定目標：** 設定 `law_pcode_to_load` (或相關變數) 以識別資料庫中的法規。筆記本邏輯應能根據 PCode 從資料庫提取法規全文和其他必要資訊作為 LLM 的輸入。
    *   **規格文件：** 確保 `法律語法形式化.md` 可用，因為它指導 LLM 的生成過程。
    *   **LLM 互動：**
        *   執行相關儲存格以啟動 Gemini API client。
        *   如果系統設計為仍上傳檔案給 LLM (例如 `法律語法形式化.md`)，則 `client.files.upload()` 相關程式碼依然適用。法規本文可能直接從資料庫字串傳遞給 LLM，或也暫存為檔案上傳。
        *   執行生成各類元資料 (非法條、法條) 的儲存格。LLM 的原始回應會先儲存到 `txt/` 目錄下的暫存檔案。
    *   **儲存至資料庫：**
        *   從 `txt/` 檔案解析出 JSON 內容後，最主要的步驟是將這些新生成的元資料透過 `LawMetadataMgr` 的 `upsert_law_metadata_to_db(law_metadata_object)` 方法儲存到 PostgreSQL 資料庫。

**3.2.4. 管理元資料：**

*   **新增/更新元資料：**
    *   無論是新生成的元資料，還是從資料庫載入後修改的元資料，都使用 `lmmgr.upsert_law_metadata_to_db(lm_object)` 將其儲存回資料庫。`lm_object` 應為一個 `LawMetadata` 的實例。
*   **刪除元資料：**
    *   若要從資料庫中刪除特定法規的詳細元資料，可使用 `lmmgr.delete_law_metadata_from_db(pcode="PCODE_TO_DELETE")`。

**3.2.5. JSON 檔案匯出 (可選)：**

*   如果您需要將資料庫中的元資料匯出為 JSON 檔案 (例如用於備份、分享或離線分析)：
    *   先使用 `load_lm_from_db()` 將元資料載入到一個 `LawMetadata` 物件。
    *   然後使用該物件的 `to_json_files(output_prefix="json/EXPORTED_LAW_NAME")` 方法。
    ```python
    # lm_from_db 是已從資料庫載入的 LawMetadata 物件
    if lm_from_db:
        lm_from_db.to_json_files(output_prefix=f"json/{lm_from_db.law_name}_export")
        print(f"已將 {lm_from_db.law_name} 的元資料匯出至 json/ 目錄。")
    ```

**3.3. 驗證輸出：**

*   **主要儲存：** 主要在 PostgreSQL 資料庫中驗證資料是否正確寫入或更新。可使用資料庫客戶端工具查詢。
*   **中繼輸出 (`txt/`)：** `txt/` 目錄中的檔案仍可用於偵錯 LLM 的具體產出。
*   **可選 JSON 輸出 (`json/`)：** 若執行了匯出，檢查 `json/` 目錄。

## 4. 操作與管理既有元資料

`LawMetadata` 和 `LawMetadataMgr` 類別（主要在 `law_meta_loader.ipynb` 中使用）協助開發者與儲存於 PostgreSQL 資料庫中的元資料互動。

**4.1. `LawMetadata` 類別 (代表單一法規的完整元資料)：**

*   此類別的實例通常由 `LawMetadataMgr` 從資料庫查詢結果轉換而來，或在生成新元資料後準備寫入資料庫前創建。
*   **從 JSON 檔案載入 (用於外部/舊有資料)：**
    *   `LawMetadata.from_json_files(**filepaths)`：此方法主要用於載入外部提供的 JSON 檔案，或系統改版前已存在的 JSON 檔案。在新的資料庫中心流程中，主要透過 `LawMetadataMgr.load_lm_from_db()` 取得資料。
    ```python
    # 範例：載入一組外部 JSON 檔案
    # law_name_external = "外部法規"
    # dir_json_external = "external_json_source/"
    # external_filepaths = {
    #     "law_regulation": f"{dir_json_external}/{law_name_external}_law_regulation.json",
    #     # ... 其他四個檔案
    # }
    # lm_external = LawMetadata.from_json_files(**external_filepaths)
    # if lm_external:
    #     # 可以考慮將此外部資料匯入資料庫
    #     # lmmgr.upsert_law_metadata_to_db(lm_external)
    #     pass
    ```
*   **存取元資料內容：**
    *   一旦 `LawMetadata` 物件被實例化 (無論是從資料庫載入或新生成)，其屬性 (`law_regulation`, `legal_concepts` 等) 皆可如字典或列表般存取。
    ```python
    # lm_from_db 是已從資料庫載入的 LawMetadata 物件
    if lm_from_db:
        print("法規名稱:", lm_from_db.law_regulation.get("法規名稱"))
        if lm_from_db.legal_concepts:
            print("第一個法律概念:", lm_from_db.legal_concepts[0].get("詞彙名稱"))
    ```
*   **更新 ID (`renew_id()`)：**
    *   在將新的或修改過的元資料儲存到資料庫之前，呼叫 `renew_id()` 以確保所有內部 ID 的唯一性和一致性。
    ```python
    if lm_to_upsert: # 假設 lm_to_upsert 是一個準備要儲存的 LawMetadata 物件
        lm_to_upsert.renew_id()
        # lmmgr.upsert_law_metadata_to_db(lm_to_upsert)
    ```
*   **匯出為 JSON 檔案 (`to_json_files()`)：**
    *   將 `LawMetadata` 物件的內容匯出為五個 JSON 檔案。這通常用於備份、分享，或當需要檔案格式時。
    ```python
    if lm_from_db: # 從資料庫載入的 LawMetadata 物件
        lm_from_db.to_json_files(output_prefix=f"json_export/{lm_from_db.law_name}")
    ```

**4.2. `LawMetadataMgr` 類別 (管理多個法規的元資料並與資料庫互動)：**

*   **初始化與資料庫連線：**
    *   `LawMetadataMgr` 初始化時需要傳入資料庫連線參數。
    ```python
    # db_params 包含 DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    # lmmgr = LawMetadataMgr(db_conn_params=db_params)
    # 筆記本中通常會有 lmmgr = LawMetadataMgr(db_conn=conn) 這樣的程式碼，conn 是已建立的資料庫連線
    ```
*   **從資料庫載入法規元資料 (`load_lm_from_db()`)：**
    *   此為從 PostgreSQL 資料庫獲取特定法規之詳細元資料的主要方法。
    ```python
    # law_pcode = "PCODE00001"
    # lm_instance = lmmgr.load_lm_from_db(law_pcode_to_load=law_pcode)
    # if lm_instance:
    #    # 對 lm_instance 進行操作
    #    pass
    ```
*   **新增或更新元資料至資料庫 (`upsert_law_metadata_to_db()`)：**
    *   將一個 `LawMetadata` 物件的內容寫入或更新到資料庫中。
    ```python
    # new_lm 是新生成或修改過的 LawMetadata 物件
    # lmmgr.upsert_law_metadata_to_db(new_lm)
    ```
*   **從資料庫刪除法規元資料 (`delete_law_metadata_from_db()`)：**
    *   根據 PCode 刪除法規的詳細元資料。
    ```python
    # pcode_to_remove = "PCODE00002"
    # lmmgr.delete_law_metadata_from_db(pcode=pcode_to_remove)
    ```
*   **從 JSON 檔案載入 (輔助功能) (`load_lm_bynames_from_json()`)：**
    *   此方法用於從 `json/` 目錄載入一或多個法規的 JSON 檔案到 `LawMetadataMgr` 的記憶體中。
    *   這可能用於：
        *   系統初始化，若資料庫為空且 `law_proc.ipynb` 尚未執行時，用於初步載入資料。
        *   載入不透過標準資料庫流程管理的補充性元資料。
    *   注意：載入後，若要將這些資料存入資料庫，仍需逐一透過 `upsert_law_metadata_to_db()`。
    ```python
    # lmmgr.load_lm_bynames_from_json(["法規A", "法規B"]) # 從 json/法規A_*.json 等檔案載入
    # loaded_lm_A = lmmgr.get_lm_byname("法規A")
    # if loaded_lm_A:
    #     # lmmgr.upsert_law_metadata_to_db(loaded_lm_A) # 如有必要，存入資料庫
    #     pass
    ```
*   **匯出所有已載入 (記憶體中) 的元資料至 JSON (`export_all_to_json()`)：**
    *   將 `LawMetadataMgr` 物件中所有 `LawMetadata` 實例匯出為各自的 JSON 檔案。
    *   此功能主要用於將記憶體中的資料（可能來自 JSON 檔案載入或混合來源）批次匯出。
    ```python
    # lmmgr.export_all_to_json(output_dir="json_backup_all")
    ```
*   **新增/移除記憶體中的 `LawMetadata` 物件 (`add_lm()`, `remove_lm()`)：**
    *   `add_lm(lm_obj)`: 將一個 `LawMetadata` 物件加入到 `LawMetadataMgr` 的內部字典 `lms`。
    *   `remove_lm(law_name)`: 從內部字典 `lms` 中移除一個 `LawMetadata` 物件。
    *   **重要：** 這些操作僅影響記憶體中的集合。若要讓變更反映到資料庫，必須明確呼叫 `upsert_law_metadata_to_db()` 或 `delete_law_metadata_from_db()`。

## 5. 查詢與分析功能的運用與擴展

系統提供了多種查詢與分析元資料的方式：

*   **直接資料庫查詢 (建議用於複雜查詢)：**
    *   由於所有法規基礎資料和詳細元資料都儲存在 PostgreSQL 資料庫中，開發者可以直接使用 SQL 進行強大且高效的查詢。
    *   這對於跨多個法規、多個元資料欄位的複雜分析、以及整合外部資料進行查詢特別有用。
    *   開發者應熟悉資料庫的綱要 (tables, columns, relationships) 以便撰寫有效的 SQL 查詢。
*   **Python 腳本與 `LawMetadataMgr` (主要在 `law_meta_loader.ipynb` 中)：**
    *   `law_meta_loader.ipynb` 筆記本的「進階搜尋」區塊提供了一些基於 Python 的查詢範例，這些函數操作的是從資料庫載入到記憶體中的 `LawMetadata` 物件。
    *   這些 Python 函數對於快速探索、針對特定已載入法規進行操作，或執行那些在 Python 中更容易實現的邏輯（例如，涉及複雜文字處理或與 LLM 互動的查詢）仍然非常有用。
    *   現有範例函數包括：
        *   `keyword_search(metadata, keyword, fields_to_search)`：在指定欄位搜尋關鍵字。
        *   `category_filter(metadata, category_type, metadata_type="hierarchy_relations")`：篩選特定類型的元資料。
        *   `combined_search_hierarchy(metadata, category_type, related_law_keyword)`：複合條件搜尋。
        *   `generate_mermaid_diagram(metadata)` / `generate_article_mermaid_diagram(metadata)`：生成 Mermaid 語法以視覺化關係。
*   **擴展 Python 查詢範例：**
    *   若要撰寫一個新的 Python 查詢函數，例如「查找所有在其『法律效果』中提及特定法律概念的法條」：
        1.  使用 `LawMetadataMgr` 的 `load_lm_from_db()` 載入一或多個目標法規的元資料到 `LawMetadata` 物件。
        2.  迭代 `LawMetadata` 物件中的 `law_articles`。
        3.  檢查每個法條的 `法律意涵['法律效果']` 欄位是否包含目標概念的文字。
    *   或者，考慮將此類查詢直接以 SQL 形式在資料庫上執行，可能會更有效率，特別是當法規數量眾多時。

開發者應根據查詢的複雜度、資料量大小以及是否需要在應用程式邏輯中進一步處理結果，來選擇最適合的查詢方式。

## 6. LLM 互動與提示調整 (進階)

若開發者在 `law_meta_loader.ipynb` 中使用 LLM 功能生成詳細元資料，並需要微調其行為或產出，可以從以下方面著手：

*   **`generate()` 函數 (或類似的 LLM 互動函數)：**
    *   `client`: `genai.Client` 物件。
    *   `files`: 上傳給 LLM 的檔案列表。這通常包含 `法律語法形式化.md`。法規本文可能從資料庫提取後直接作為字串傳遞，或也可能暫存為檔案上傳。
    *   `user_prompt`: 主要的提示文本。
    *   `file_path`: 儲存 LLM 回應的 `.txt` 檔案路徑 (中繼儲存)。
*   **`types.GenerateContentConfig` (Gemini API 設定)：**
    *   `temperature` (0.0 - 1.0)：控制隨機性，較低的值使輸出更具確定性。
    *   `top_p`, `top_k`：控制核心採樣的參數。
    *   `max_output_tokens`：限制 LLM 回應的長度。
    *   `system_instruction`: 例如 `請以台灣人的立場，用繁體中文回答`，此處設定了 LLM 的角色和語言。
*   **提示 (`prompt_list`, `prompt_list_a` 等在 `law_meta_loader.ipynb` 中的各種提示變數)：**
    *   這些列表或字串是直接傳送給 LLM 的指令。
    *   若發現 LLM 對某些法規 (從資料庫提取的文本) 的理解或產出格式不佳，可以嘗試修改這些提示的措辭、結構或提供的範例。
    *   **注意：** 修改提示通常需要多次實驗才能達到預期效果。 LLM 的輸出會先存於 `txt/` 目錄，確認無誤後才會透過 `upsert_law_metadata_to_db` 存入資料庫。

## 7. 元資料的重新生成與更新

在以下情況，開發者可能需要重新生成或更新既有的元資料：

*   **基礎法規資料變更 (透過 `law_proc.ipynb`)：**
    *   若原始的 XML 法規彙編檔案 (`FalV.xml` 等) 更新，並透過 `law_proc.ipynb` 重新執行匯入 (`synchronize_lawmgr_with_db`)。這會更新資料庫中法規的基本資訊和法條文本。
    *   此後，與該法規相關的詳細元資料 (五種 JSON 類型) 可能需要使用 `law_meta_loader.ipynb` 重新生成或更新，以確保與最新的基礎資料一致。
*   **規格文件 (`法律語法形式化.md`) 變更：** 若元資料的綱要或定義有調整，則所有受影響法規的詳細元資料都應使用 `law_meta_loader.ipynb` 重新生成。
*   **LLM 提示 (在 `law_meta_loader.ipynb` 中) 修改：** 為了改善特定部分的元資料產出品質，可能需要修改提示並重新生成。
*   **LLM 模型更新或更換：** 新的 LLM 模型版本可能產生不同的結果，可能需要重新生成元資料。

**操作步驟：**

1.  **備份 (強烈建議)：**
    *   **資料庫備份：** 在進行大規模重新生成前，強烈建議備份您的 PostgreSQL 資料庫，或至少備份相關的表格。
    *   **JSON 備份 (可選)：** 如果您有重要的 JSON 匯出檔案，也請一併備份。
2.  **更新基礎資料 (若適用)：**
    *   如果變更是源於 XML 檔案，首先執行 `law_proc.ipynb` 的相關步驟，將更新後的基礎資料同步到資料庫。
3.  **調整 `law_meta_loader.ipynb` 以重新生成：**
    *   設定目標法規的 PCode (例如 `law_pcode_to_load`)。
    *   確保 LLM 相關設定 (API 金鑰、提示) 和 `法律語法形式化.md` 檔案正確。
    *   啟用 `law_meta_loader.ipynb` 中與 LLM 互動和元資料生成的相關儲存格。
4.  **執行元資料生成與儲存：**
    *   執行 `law_meta_loader.ipynb` 中的儲存格，以使用 LLM（如果需要）生成新的元資料。
    *   生成的元資料將暫存於 `txt/` 目錄，然後解析。
    *   最重要的一步是使用 `lmmgr.upsert_law_metadata_to_db(updated_lm_object)` 將更新後的元資料儲存回 PostgreSQL 資料庫。
5.  **驗證：**
    *   主要在 PostgreSQL 資料庫中檢查元資料是否已按預期更新。
    *   檢查 `txt/` 中的 LLM 原始輸出來偵錯。
    *   如有需要，可將更新後的元資料匯出為 JSON 檔案進行額外驗證。

## 8. 偵錯與日誌

*   **`txt/` 目錄 (主要由 `law_meta_loader.ipynb` 使用)：**
    *   LLM 的原始回應（包含提示和模型的完整回答）都儲存在此目錄下的文字檔案中。
    *   這是偵錯 LLM 產出問題 (例如，元資料不正確、JSON 格式錯誤) 的第一站。檢查 LLM 是否正確理解提示，以及其 JSON 內容是否符合預期。
*   **Jupyter Notebook 輸出：**
    *   兩個筆記本 (`law_proc.ipynb` 和 `law_meta_loader.ipynb`) 的儲存格輸出會顯示檔案處理的路徑、資料庫操作的狀態、JSON 解析結果、錯誤訊息等，有助於即時追蹤流程和發現問題。
*   **PostgreSQL 資料庫日誌與客戶端工具：**
    *   檢查 PostgreSQL 伺服器的日誌，以了解是否有資料庫層級的錯誤 (例如，連線問題、權限錯誤、SQL 語法錯誤)。
    *   使用資料庫客戶端工具 (如 `psql`、pgAdmin、DBeaver 等) 直接連接資料庫，檢查資料是否正確寫入、表格結構是否符合預期、查詢是否返回正確結果。這對於驗證 `law_proc.ipynb` 的資料匯入和 `law_meta_loader.ipynb` 的元資料儲存至關重要。
*   **Python `print()` 陳述式與偵錯器：**
    *   在開發或偵錯筆記本中的 Python 程式碼時，適時加入 `print()` 陳述式來檢查變數狀態、資料結構或程式流程。
    *   對於更複雜的問題，可考慮使用 Python 偵錯器 (如 `pdb` 或整合在 JupyterLab/IDE 中的偵錯工具)。

本開發者手冊旨在提供您開始使用並深入了解此法律元資料框架所需的資訊。隨著您對系統的熟悉，您將能夠更有效地利用其功能並進行客製化開發。
