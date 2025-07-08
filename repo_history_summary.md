# Repo 修改歷史摘要

## 近期活動 (過去 20 天)

### 文件與架構更新
*   更新了 `sw_arch.md` 文件，反映了 V0.2.1 的變更。
*   更新了 `law_check_result.md`。
*   新增了任務列表到建議說明中。
*   忽略了部分目錄。
*   修訂了 `project.feature` 以符合 V0.2.1。
*   新增了中央行政機關組織基準法的 JSON 檔案。
*   CLI 需要支援短參數和長參數。
*   新增了 `@FEAT-004` CLI 工具功能。
*   新增了系統架構和處理流程的 Mermaid 圖。
*   新增了法規 A2A 實驗說明與測試資訊。
*   新增了 `repo_history_summary.md`。
*   更新了 `README.md`。
*   更新了 `law_proc.ipynb` 的架構描述。
*   將法規原始檔移到 `data` 目錄中。
*   Revert "Refactor: Move law-related Markdown and text files to data/ directory"。
*   Refactor: Move law-related Markdown and text files to data/ directory。
*   更新了 `sw_arch.md`，包含資料流程和目錄結構。
*   創建了 `法規工具目前樣態_V0.1.md`。

### 核心功能與 CLI 工具
*   新增了從資料庫選擇法規來生成元資料的腳本。
*   修正了 `law_cli.py` 的同步問題。
*   新增了 CLI 工具的範例命令功能，並通過了 `FEAT-004` 測試。
*   新增了 19 個法規的資料。
*   新增了少量法規的資料。
*   修正了 XML 導入對法規列表的支援。
*   修正了生成元資料函數的回滾，並從 `show_law` 進行測試。
*   `show_law` 功能新增 Markdown 格式並可導出到檔案。
*   修正了在生成 AI 之前檢查文本格式。
*   新增了 `@SCEN-026 --import-meta-list` 一個法規的測試。
*   修正了 5 個元資料首次通過 CLI 測試。
*   修正了 XML 導入測試並重命名了範例檔案。
*   修正了導入關鍵字的測試。
*   修正了導入摘要邏輯，首次測試通過。
*   實作了 `@FEAT-004` CLI 工具，在測試之前。
*   修訂以包含摘要、關鍵字，並修改了標頭。
*   確認了新生成的法律元資料的工作。
*   重構了 `law_meta_loader.ipynb` 以支援新的資料庫綱要 (v0.2)。
*   新增了 LLM 資料導入函數到 `law_proc.ipynb`。

### 資料庫與資料處理
*   修正了 `legal_concepts` 的 `law_id_code_key` 錯誤。
*   新增了資料庫視圖和存儲過程。
*   修正了 `db: lawdb, user:lawdb` 的權限授予。
*   修正了 LLM 摘要記錄與法規名稱不匹配的問題。
*   能夠 upsert 法規、法條、法律概念、層級關係、法律關係的元資料。
*   修正了導入法規、摘要、關鍵字到資料庫的測試。
*   修正了啟動資料庫，並修正了 JSON 語法錯誤。
*   更新了軟刪除邏輯以使用 `is_active` 欄位。
*   重構了 Notebooks 以支援法規的軟刪除和關係表中的法規名稱。
*   新增了軟刪除到 `laws` 表和關係表中的法規名稱。
*   修正了 `#1895`。
*   確認了新生成的法律元資料的工作。
*   重建了資料庫中特定法規的內容。
*   修改了 `legal_concepts`，新增了 `law_id` 欄位。
*   大部分元資料已經可以灌入，`legal_concepts` 還有問題。
*   導入了摘要和關鍵字。
*   整合了 PostgreSQL 到 `law_proc.ipynb` 進行法規資料處理。
*   在遷移 `law_proc` 以支援資料庫之前進行初始化。

### 測試與自動化
*   新增了 `continue run script`。
*   新增了更多診斷資訊。
*   新增了 `python install requirements.txt`。
*   新增了 `test_cli.sh`。
*   新增了完整的 workflow 腳本（尚未測試）。
*   新增了 `@SCEN-020-INT` 整合測試，並通過了 `@SCEN-019-INT`。
*   修正了 `@SCEN-019` 檢查資料庫結果成功。
*   實作了 `@SCEN-019` 整合測試，並通過了測試。
*   修正了 `phase4_cli_tools.feature` 的 8 個測試，僅限介面。
*   新增了 `pytest` 可以與 `pytest_bdd` 架構一起運行。
*   新增了 `steps.py` 可以首次運行。
*   修正了提供法規元資料計數。
*   新增了 `@FEAT-003` 的程式碼和範例結果。
*   修正了人工快速審查。
*   回滾了錯誤的刪除。

### Docker 環境
*   新增了 Docker Compose 設定。
*   修正了啟動資料庫，並修正了 JSON 語法錯誤。

### 資料與範例更新
*   提供了法規的 XML 範例檔案。
*   提供了摘要與關鍵字的範例檔案。

## 較早的歷史 (一個月至三個月前)

### 文件與架構
*   新增了開發者指南 (`how_to_use.md`) 與系統架構文件 (`sw_arch.md`)。

### 資料庫與查詢
*   整合了 PostgreSQL 用於儲存法規的 metadata。
*   建立了資料庫的 dump 檔案。
*   開始加入查詢功能。

### 初期開發
*   匯入了 prompts、修改了 JSON 格式並新增了一些法規。
*   更新了 README 檔案。
*   專案的初始提交。

---

**總結:** 這個專案在過去幾個月中開發活躍，近期的重點在於整合 PostgreSQL 資料庫、匯入由大型語言模型（LLM）產生的資料（摘要和關鍵字），以及新增管理和重建資料庫內容的功能。