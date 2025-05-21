# 開發者使用手冊：法律元資料框架 (how_to_use.md)

## 1. 前言

本文件為開發者提供如何使用「法律元資料框架」的實務指南。建議在閱讀本文件前，先熟悉 `sw_arch.md` 中描述的系統架構。本手冊將著重於具體的操作步驟、程式碼的運用以及系統的客製化與擴展。

## 2. 開發環境設定

確保您的開發環境符合以下要求：

*   **Python 版本：** 建議使用 Python 3.8 或更高版本。
*   **必要的 Python 套件：**
    *   `google-generativeai`：用於與 Google Gemini API 互動。
    *   `json`：處理 JSON 資料。
    *   `re`：使用正規表示式進行文本處理。
    *   `os`：與作業系統互動，如檔案路徑處理。
    *   您可以透過 pip 安裝：`pip install google-generativeai`
*   **API 金鑰設定：**
    *   您必須擁有一個 Google Gemini API 金鑰。
    *   將金鑰設定為環境變數 `GEMINI_API_KEY`。例如，在 Linux/macOS 的 shell 中：
        ```bash
        export GEMINI_API_KEY="您的API金鑰"
        ```
        或在 Windows PowerShell 中：
        ```powershell
        $Env:GEMINI_API_KEY="您的API金鑰"
        ```
        建議將此設定加入您的 shell 設定檔（如 `.bashrc`, `.zshrc`）或在啟動 Jupyter Notebook 的環境中設定。

## 3. 核心流程：處理新法律文件

以下步驟詳細說明開發者如何使用 `law_meta_loader.ipynb` 筆記本處理新的法律文件。

**3.1. 準備輸入檔案：**

1.  **建立法律 Markdown 檔案：**
    *   將新的法律文本儲存為 Markdown 檔案（`.md`），例如 `新的法律名稱.md`。
    *   檔案應存放於專案的根目錄。
    *   確保檔案為 UTF-8 編碼。
2.  **確認規格文件：**
    *   `法律語法形式化.md` 檔案必須存在於根目錄，因為它將作為 LLM 生成元資料的依據。

**3.2. 設定 Jupyter Notebook (`law_meta_loader.ipynb`)：**

1.  **開啟筆記本：** 啟動 Jupyter Notebook 伺服器並開啟 `law_meta_loader.ipynb`。
2.  **設定 `law_name` 變數：**
    *   在標示為「LLM 建構 json」區段的第一個程式碼儲存格中，找到 `law_name` 變數。
    *   將其值設定為您要處理的法律檔案名稱（不含 `.md` 副檔名）。例如：
        ```python
        law_name="新的法律名稱"
        ```
3.  **控制執行流程開關：**
    *   筆記本中使用 `if 0:` 或 `if 1:` 的結構來控制特定區塊的程式碼是否執行。作為開發者，您需要根據需求調整這些開關：
        *   `if 1: # 設定 LLM, 並上傳檔案`：處理新法律時應設為 `1`。
        *   `if 1: # 產生非法條的 Meta data`：產生法規、概念、層級、關係等元資料時設為 `1`。
        *   `if 0: # 取得最大條號`：若要讓 LLM 輔助判斷最大條號則設為 `1`，或手動設定 `max_cnt`。
        *   `if 0: # 產生法條 Meta Data`：產生逐條元資料時設為 `1`。
        *   `if 0: #從檔案內組合法條 Meta data`：從 `txt/` 檔案組裝最終的法條 JSON 時設為 `1`。
        *   其他如「單法規使用」、「法規管理使用」、「進階搜尋」等區塊的開關，則根據您的當前任務調整。

**3.3. 執行筆記本儲存格 (逐步指南)：**

依序執行以下關鍵儲存格，以完成新法律的處理：

1.  **起始化-物件與functions：** 執行此儲存格以載入必要的函式庫、定義輔助函數及核心類別 (`LawMetadata`, `LawMetadataMgr`)。
2.  **LLM 建構 json - 初始化 Client 與上傳檔案：**
    *   執行第一個程式碼儲存格（在設定 `law_name` 之後）。
    *   此儲存格會使用您的 `GEMINI_API_KEY` 初始化 `genai.Client`。
    *   接著，它會使用 `client.files.upload()` 將您的法律 `.md` 檔案以及 `法律語法形式化.md` 上傳至 Gemini 服務。請確認檔案路徑正確。
3.  **LLM 建構 json - 產生非法條的 Meta data：**
    *   此儲存格包含一個 `prompt_list`，定義了生成四種非條文元資料的提示。
    *   迴圈會依序處理每個提示：
        *   呼叫 `generate(client, files, law_name, prompt_pair[1], file_path)` 函數。此函數會：
            *   將 Markdown 檔案和提示傳送給 Gemini API。
            *   接收 LLM 的回應。
            *   將原始回應（問題和答案）儲存於 `txt/[law_name]_[metadata_type].txt`。
        *   接著，程式碼會讀取此 `.txt` 檔案，使用 `handle_regex()` 提取 LLM 回應中的 JSON 內容。
        *   移除註解後，將純淨的 JSON 字串轉換為 Python 物件，並儲存至 `json/[law_name]_[metadata_type].json`。
4.  **LLM 建構 json - 取得最大條號 (選擇性)：**
    *   若啟用，此儲存格會提示 LLM 這部法律的最大條號。
    *   回應會被解析，`max_cnt` 變數會被設定。若不使用 LLM，您可以手動在此區塊或後續產生法條元資料的區塊設定 `max_cnt`。
5.  **LLM 建構 json - 產生法條 Meta Data：**
    *   此儲存格處理逐條元資料的生成，考慮到 LLM 可能的長度限制，它會分批次處理。
    *   `start`, `step`, `max_cnt` 變數控制批次的大小和範圍。
    *   `prompt_list_a` 會動態生成每批次的提示。
    *   與前述類似，`generate()` 函數被呼叫，LLM 回應儲存於 `txt/[law_name]_article_[start_index].txt`。
    *   內含一個 `while` 迴圈和 `try-except` 結構，用於處理 LLM API 可能發生的暫時性錯誤，並進行重試（最多3次）。
6.  **LLM 建構 json - 從檔案內組合法條 Meta data：**
    *   此儲存格讀取所有 `txt/[law_name]_article_*.txt` 檔案。
    *   使用 `handle_regex()` 提取 JSON 內容，並將其從字串轉換為 Python 列表。
    *   所有條文的元資料會被合併（`law_articles.extend(json_object)`）。
    *   最終完整的法條元資料列表會儲存至 `json/[law_name]_law_articles.json`。

**3.4. 驗證輸出：**

*   **主要輸出：** 檢查 `json/` 目錄，應包含五個對應於您法律的 JSON 檔案。
*   **中繼輸出：** `txt/` 目錄包含 LLM 的原始回應，可用於偵錯或了解 LLM 的具體產出。

## 4. 操作與管理既有元資料

透過 `LawMetadata` 和 `LawMetadataMgr` 類別，開發者可以載入、存取、修改和管理已生成的元資料。

**4.1. `LawMetadata` 類別 (單一法律)：**

*   **載入元資料：**
    ```python
    law_name = "政府採購法" # 替換為您要載入的法律名稱
    dir_json = "json"
    filepaths = {
        "law_regulation": f"{dir_json}/{law_name}_law_regulation.json",
        "legal_concepts": f"{dir_json}/{law_name}_legal_concepts.json",
        "hierarchy_relations": f"{dir_json}/{law_name}_hierarchy_relations.json",
        "law_relations": f"{dir_json}/{law_name}_law_relations.json",
        "law_articles": f"{dir_json}/{law_name}_law_articles.json"
    }
    lm = LawMetadata.from_json_files(**filepaths)
    if lm:
        print(lm)
    ```
*   **存取元資料內容：**
    ```python
    if lm:
        print("法規名稱:", lm.law_regulation.get("法規名稱"))
        if lm.legal_concepts:
            print("第一個法律概念:", lm.legal_concepts[0].get("詞彙名稱"))
    ```
*   **更新 ID：**
    *   若手動修改或合併不同來源的元資料，ID 可能需要更新以維持唯一性。
    ```python
    if lm:
        lm.renew_id() # 會更新法規、法條、概念等的代號
        # 之後記得儲存
    ```
*   **儲存元資料：**
    ```python
    if lm:
        # lm.law_regulation["法規版本"] = "新版本" # 範例：修改內容
        lm.to_json_files(output_prefix=f"{dir_json}/{law_name}_modified") 
        # 注意：output_prefix 會影響檔名，若要覆蓋原檔案，請使用原 law_name
    ```

**4.2. `LawMetadataMgr` 類別 (多個法律)：**

*   **初始化與載入：**
    ```python
    lmmgr = LawMetadataMgr()
    # 取得 json 目錄下所有法律名稱
    law_names_in_json_dir = get_law_names_from_directory("./json") 
    lmmgr.load_lm_bynames(law_names_in_json_dir)
    
    # 或載入特定法律
    # lmmgr.load_lm_bynames(["政府採購法", "民法"])
    
    lms = lmmgr.lms # 取得一個字典，key 為法規名稱，value 為 LawMetadata 物件
    ```
*   **存取特定法律的元資料：**
    ```python
    if "政府採購法" in lms:
        gpa_lm = lms["政府採購法"]
        print(gpa_lm.law_regulation.get("簡述"))
    ```

## 5. 查詢與分析功能的運用與擴展

筆記本的「進階搜尋」區塊提供了一些查詢範例。開發者可以此為基礎進行擴展。

*   **`keyword_search(metadata, keyword, fields_to_search)`：** 在指定欄位搜尋關鍵字。
*   **`category_filter(metadata, category_type, metadata_type="hierarchy_relations")`：** 篩選特定類型的元資料。
*   **`combined_search_hierarchy(metadata, category_type, related_law_keyword)`：** 複合條件搜尋。
*   **`generate_mermaid_diagram(metadata)` / `generate_article_mermaid_diagram(metadata)`：** 生成 Mermaid 語法以視覺化關係。

**擴展範例：**
若要撰寫一個新的查詢函數，例如「查找所有在其『法律效果』中提及特定法律概念的法條」，您可以：
1.  確保已使用 `LawMetadataMgr` 載入相關法律。
2.  迭代 `LawMetadata` 物件中的 `law_articles`。
3.  檢查每個法條的 `法律意涵['法律效果']` 欄位是否包含目標概念的文字。

## 6. LLM 互動與提示調整 (進階)

開發者若需微調 LLM 的行為或產出，可以從以下方面著手：

*   **`generate()` 函數：**
    *   `client`: `genai.Client` 物件。
    *   `files`: 上傳給 LLM 的檔案列表。
    *   `user_prompt`: 主要的提示文本。
    *   `file_path`: 儲存 LLM 回應的 `.txt` 檔案路徑。
*   **`types.GenerateContentConfig`：**
    *   `temperature` (0.0 - 1.0)：控制隨機性，較低的值使輸出更具確定性。
    *   `top_p`, `top_k`：控制核心採樣的參數。
    *   `max_output_tokens`：限制 LLM 回應的長度。
    *   `system_instruction`: `請以台灣人的立場，用繁體中文回答`，此處設定了 LLM 的角色和語言。
*   **提示 (`prompt_list`, `prompt_list_a`)：**
    *   這些列表中的字串是直接傳送給 LLM 的指令。
    *   若發現 LLM 對某些法律的理解或產出格式不佳，可以嘗試修改這些提示的措辭、結構或提供的範例（若提示中包含範例）。
    *   **注意：** 修改提示可能需要多次實驗才能達到預期效果。

## 7. 元資料的重新生成與更新

在以下情況，開發者可能需要重新生成或更新既有的元資料：

*   **來源法律文件 (`.md`) 更新：** 若法條內容有修正。
*   **規格文件 (`法律語法形式化.md`) 變更：** 若元資料的綱要或定義有調整。
*   **LLM 提示 (`prompt_list`, `prompt_list_a`) 修改：** 為了改善特定部分的產出品質。
*   **LLM 模型更新或更換：** 新的模型版本可能產生不同的結果。

**操作步驟：**

1.  **備份 (建議)：** 在重新生成前，備份您 `json/` 目錄下相關的 JSON 檔案。
2.  **調整筆記本：**
    *   設定正確的 `law_name`。
    *   啟用對應的執行開關 (如 `if 1: # 產生法條 Meta Data`)。
    *   若只更新特定部分（例如僅法條），則僅啟用相關區塊。
3.  **執行相關儲存格：** 參考 3.3. 節的指南。
4.  **驗證輸出。**

## 8. 偵錯與日誌

*   **`txt/` 目錄：** LLM 的原始回應都儲存在此，是偵錯 LLM 產出問題的第一站。檢查 LLM 是否正確理解提示，以及其 JSON 格式是否大致正確。
*   **Jupyter Notebook 輸出：** 筆記本的儲存格輸出會顯示檔案處理的路徑、JSON 解析的結果等，有助於追蹤流程。
*   **`print()` 陳述式：** 在開發或偵錯時，適時在筆記本程式碼中加入 `print()` 陳述式來檢查變數狀態或程式流程。

本開發者手冊旨在提供您開始使用並深入了解此法律元資料框架所需的資訊。隨著您對系統的熟悉，您將能夠更有效地利用其功能並進行客製化開發。
