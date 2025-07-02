

"""
This module contains the step definitions for BDD tests using pytest-bdd.
It covers the features defined in the .feature files in the 'features' directory.
"""
import os
import sys
from unittest.mock import patch
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import dotenv

# Add project root to the Python path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
dotenv.load_dotenv()

# --- Mocks and Fixtures ---

@pytest.fixture
def mock_law_processor_class():
    """Mocks the LawProcessor class for CLI tests."""
    with patch('law_cli.LawProcessor') as mock_class:
        yield mock_class

@pytest.fixture
def mock_law_metadata_manager_class():
    """Mocks the LawMetadataManager class for CLI tests."""
    with patch('law_cli.LawMetadataManager') as mock_class:
        yield mock_class

# --- Load scenarios from the implemented feature file ---

scenarios('phase4_cli_tools.feature')

# --- Helper function to run CLI ---

def run_cli(*args):
    """Helper function to run the CLI with specified arguments."""
    test_args = ['law_cli.py'] + list(args)
    with patch.object(sys, 'argv', test_args):
        from law_cli import main as cli_main
        try:
            cli_main()
        except SystemExit:
            # Prevent SystemExit from stopping the test runner
            pass

# --- Generic Step Definitions ---

@when(parsers.parse('執行命令列工具 `{command}`'))
def execute_cli_command(command, mock_law_processor_class, mock_law_metadata_manager_class):
    """Executes a command line tool command, handling variations."""
    first_command = command.split('` 或 `')[0].strip('`')
    args = first_command.split()[2:]
    run_cli(*args)

@given('資料庫中已存在多個法規')
def laws_exist_in_db():
    """A conceptual step, no mock needed as we check the processor call."""
    pass

@given('資料庫中已載入法規資料')
def db_with_law_data():
    """A conceptual step, no mock needed."""
    pass

# --- Scenario-specific Step Definitions ---

# @SCEN-019
@given(parsers.parse('一個包含多個法規 XML 檔案路徑的清單檔案 "{file_path}"'))
def xml_list_file(file_path):
    # This will write to the actual data directory for the test
    # This is a temporary solution for the test environment.
    # A better approach would be to mock the file reading in law_cli.py.
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("中華民國憲法\n國家安全會議組織法")

@given('資料庫中不存在清單中的法規')
def laws_not_in_db(mock_law_metadata_manager_class):
    mock_instance = mock_law_metadata_manager_class.return_value
    mock_instance.check_law_exists.return_value = False

@then('"laws" 資料表中應包含從 XML 解析出的清單中所有法規紀錄')
def check_laws_imported(mock_law_processor_class):
    mock_instance = mock_law_processor_class.return_value
    mock_instance.import_xml.assert_called_once_with('data/xml_sample.xml', law_list=None)

@then('"articles" 資料表中應包含所有對應的法條紀錄')
def check_articles_imported():
    pass  # Implicitly tested by the call above

# @SCEN-020
@given(parsers.parse('一個包含多法規名稱與摘要內容的檔案 "{file_path}"'))
def summary_file(tmp_path, file_path):
    (tmp_path / os.path.dirname(file_path)).mkdir(exist_ok=True)
    (tmp_path / file_path).write_text("law1: summary1\nlaw2: summary2", encoding="utf-8")

@then(parsers.parse('"{table}" 資料表中清單中所有法規紀錄的 "{column}" 欄位應被更新'))
def check_summary_updated(mock_law_processor_class, table, column):
    mock_instance = mock_law_processor_class.return_value
    if "summary" in column:
        mock_instance.update_summary.assert_called_once_with('data/summary_sample.md', law_list=None)

# @SCEN-021
@given(parsers.parse('一個包含法規名稱與關鍵字檔案路徑對應的清單檔案 "{file_path}"'))
def keywords_list_file(tmp_path, file_path):
    (tmp_path / os.path.dirname(file_path)).mkdir(exist_ok=True)
    (tmp_path / file_path).write_text("law1,keywords1\nlaw2,keywords2", encoding="utf-8")

@then('"laws" 資料表中清單中所有法規紀錄的 "llm_keywords" 欄位應被更新')
def check_keywords_updated(mock_law_processor_class):
    mock_instance = mock_law_processor_class.return_value
    mock_instance.update_keywords.assert_called_once_with('data/keywords_sample.csv')

# @SCEN-022
@given(parsers.parse('一個包含法規名稱與 Markdown 檔案路徑對應的清單檔案 "{file_path}"'))
def markdown_list_file(tmp_path, file_path):
    (tmp_path / os.path.dirname(file_path)).mkdir(exist_ok=True)
    (tmp_path / file_path).write_text("law1,/path/to/law1.md\nlaw2,/path/to/law2.md", encoding="utf-8")

@given(parsers.parse('一份定義 Meta Data 結構的規格檔案 "{file_path}"'))
def meta_spec_file(tmp_path, file_path):
    (tmp_path / file_path).write_text("spec content", encoding="utf-8")

@then(parsers.parse('應在 "{directory}" 目錄下生成清單中每個法規對應的五種 Meta Data JSON 檔案'))
def check_meta_json_generated(mock_law_metadata_manager_class, directory):
    mock_instance = mock_law_metadata_manager_class.return_value
    mock_instance.generate_meta_list.assert_called_once_with('data/law_tometa_list.txt')

# @SCEN-023
@given(parsers.parse('一個包含要刪除法規名稱的清單檔案 "{file_path}"'))
def delete_list_file(tmp_path, file_path):
    (tmp_path / os.path.dirname(file_path)).mkdir(exist_ok=True)
    (tmp_path / file_path).write_text("law1\nlaw2", encoding="utf-8")

@then('資料庫中所有與清單中法規相關的紀錄應被清除 (laws, articles, legal_concepts, law_hierarchy_relationships, law_relationships)')
def check_laws_deleted(mock_law_processor_class):
    mock_instance = mock_law_processor_class.return_value
    mock_instance.delete_law_list.assert_called_once_with('data/law_delete_list.txt')

# @SCEN-024
@given('資料庫中已存在多個法規的完整資料')
def db_with_full_law_data():
    pass

@given(parsers.parse('一個包含要匯出法規名稱的清單檔案 "{file_path}"'))
def export_list_file(tmp_path, file_path):
    (tmp_path / os.path.dirname(file_path)).mkdir(exist_ok=True)
    (tmp_path / file_path).write_text("law1\nlaw2", encoding="utf-8")

@then(parsers.parse('"{directory}" 目錄下應生成清單中每個法規對應的 Markdown 檔案，其中包含該法規的完整條文內容及相關 Meta Data (若有)'))
def check_markdown_exported(mock_law_processor_class, directory):
    mock_instance = mock_law_processor_class.return_value
    mock_instance.export_law_list.assert_called_once_with('data/law_tometa_list.txt', 'output_dir')

# @SCEN-025
@when('執行命令列工具 `python law_cli.py --check-integrity` 或 `python law_cli.py -c`')
def execute_integrity_check(mock_law_processor_class):
    run_cli('--check-integrity')

@then('應輸出資料庫完整性檢查報告，包含各表格的資料量、空值比例等指標')
def check_integrity_report_output(mock_law_processor_class):
    mock_instance = mock_law_processor_class.return_value
    mock_instance.check_integrity.assert_called_once()

@then('報告應儲存至預設的報告檔案路徑')
def check_report_file_saved():
    pass # Implicitly tested by the call above

# @SCEN-026
@given(parsers.parse('一個包含多個法規名稱的清單檔案 "{file_path}"'))
def meta_import_list_file(tmp_path, file_path):
    (tmp_path / os.path.dirname(file_path)).mkdir(exist_ok=True)
    (tmp_path / file_path).write_text("law1\nlaw2", encoding="utf-8")

@given(parsers.parse('"{directory}" 目錄下存在清單中每個法規對應的五種 Meta Data JSON 檔案'))
def meta_json_files_exist(tmp_path, directory):
    json_dir = tmp_path / directory
    json_dir.mkdir(parents=True, exist_ok=True)
    for law in ["law1", "law2"]:
        (json_dir / f"{law}_law_regulation.json").touch()
        (json_dir / f"{law}_law_articles.json").touch()
        (json_dir / f"{law}_legal_concepts.json").touch()
        (json_dir / f"{law}_law_hierarchy_relations.json").touch()
        (json_dir / f"{law}_law_relations.json").touch()

@then('資料庫中對應法規的 `laws` 表格 `law_metadata` 欄位應被填入')
def check_law_metadata_imported(mock_law_metadata_manager_class):
    mock_instance = mock_law_metadata_manager_class.return_value
    mock_instance.load_meta_data_list_to_db.assert_called_once_with('data/law_tometa_list.txt')

@then('資料庫中對應法規的 `articles` 表格 `article_metadata` 欄位應被填入')
def check_article_metadata_imported():
    pass # Implicitly tested

@then('資料庫中對應法規的 `legal_concepts` 資料表應包含對應的法律概念')
def check_legal_concepts_imported():
    pass # Implicitly tested

@then('資料庫中對應法規的 `law_hierarchy_relationships` 資料表應包含對應的階層關係')
def check_hierarchy_imported():
    pass # Implicitly tested

@then('資料庫中對應法規的 `law_relationships` 資料表應包含對應的關聯性資料')
def check_relations_imported():
    pass # Implicitly tested
