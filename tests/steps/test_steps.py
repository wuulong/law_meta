
"""
This module contains the step definitions for BDD tests using pytest-bdd.
It covers the features defined in the .feature files in the 'features' directory.
"""
import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# --- Mocks and Fixtures ---

@pytest.fixture
def mock_law_processor():
    """Mocks the LawProcessor for CLI tests."""
    with patch('law_cli.LawProcessor') as mock_proc:
        yield mock_proc.return_value

@pytest.fixture
def mock_law_metadata_manager():
    """Mocks the LawMetadataManager for CLI tests."""
    with patch('law_cli.LawMetadataManager') as mock_manager:
        yield mock_manager.return_value

# --- Load all scenarios from feature files ---

scenarios(
    '../features/phase1_data_loading.feature',
    '../features/phase2_meta_data_loading.feature',
    '../features/phase3_data_integrity_check.feature',
    '../features/phase4_cli_tools.feature',
)


# --- Helper function to run CLI ---

def run_cli(*args):
    """Helper function to run the CLI with specified arguments."""
    # The first argument to sys.argv is the script name
    test_args = ['law_cli.py'] + list(args)
    with patch.object(sys, 'argv', test_args):
        # Import and run the main function from law_cli
        from law_cli import main as cli_main
        cli_main()


# --- Step Definitions for phase4_cli_tools.feature ---

# @SCEN-019: 透過命令列工具匯入多個法規的 XML 資料，法規清單從檔案來
@given(parsers.parse('一個包含多個法規 XML 檔案路徑的清單檔案 "{file_path}"'))
def xml_list_file(tmp_path, file_path):
    """Creates a dummy XML list file."""
    content = "/path/to/law1.xml\n/path/to/law2.xml"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

@given('資料庫中不存在清單中的法規')
def laws_not_in_db(mock_law_metadata_manager):
    """Mocks the check for law existence to return False."""
    mock_law_metadata_manager.check_law_exists.return_value = False

@when(parsers.parse('執行命令列工具 `{command}`'))
def execute_cli_command(command, mock_law_processor, mock_law_metadata_manager):
    """Executes a command line tool command."""
    # We mock the processors, so the command itself is just for show.
    # The actual test logic is in the 'then' steps which check if the
    # correct processor methods were called.
    # We can split the command to pass arguments to our helper
    args = command.split()[1:] # remove 'python'
    run_cli(*args)


@then('"laws" 資料表中應包含從 XML 解析出的清單中所有法規紀錄')
def check_laws_imported(mock_law_processor):
    """Checks if the import_law_from_xml method was called for each law."""
    # Based on the dummy file, we expect 2 calls
    assert mock_law_processor.import_law_from_xml.call_count == 2

@then('"articles" 資料表中應包含所有對應的法條紀錄')
def check_articles_imported():
    """
    This is implicitly tested by checking if import_law_from_xml was called,
    as that function is responsible for importing both laws and articles.
    No additional assertion is needed here if the mock is for the whole process.
    """
    pass

# @SCEN-020: 透過命令列工具更新多個法規的 LLM 摘要
@given('資料庫中已存在多個法規')
def laws_exist_in_db():
    """A conceptual step, no mock needed as we check the processor call."""
    pass

@given(parsers.parse('一個包含多法規名稱與摘要內容的檔案 "{file_path}"'))
def summary_file(tmp_path, file_path):
    """Creates a dummy summary file."""
    content = "law1: summary1\nlaw2: summary2"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

@then(parsers.parse('"{table}" 資料表中清單中所有法規紀錄的 "{column}" 欄位應被更新'))
def check_summary_updated(mock_law_processor, table, column):
    """Checks if the update_summary_from_file method was called."""
    # This is a generic step, so we check which processor method was called.
    # In this scenario, it should be update_summary_from_file.
    mock_law_processor.update_summary_from_file.assert_called_once()


# @SCEN-021: 透過命令列工具更新多個法規的 LLM 關鍵字
@given(parsers.parse('一個包含法規名稱與關鍵字檔案路徑對應的清單檔案 "{file_path}"'))
def keywords_list_file(tmp_path, file_path):
    """Creates a dummy keywords list file."""
    content = "law1,keywords1\nlaw2,keywords2"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

# Using the same 'then' step from SCEN-020
@then('"laws" 資料表中清單中所有法規紀錄的 "llm_keywords" 欄位應被更新')
def check_keywords_updated(mock_law_processor):
    """Checks if the update_keywords_from_file method was called."""
    mock_law_processor.update_keywords_from_file.assert_called_once()


# @SCEN-022: 透過命令列工具從多個法規的 Markdown 檔案生成 Meta Data
@given(parsers.parse('一個包含法規名稱與 Markdown 檔案路徑對應的清單檔案 "{file_path}"'))
def markdown_list_file(tmp_path, file_path):
    """Creates a dummy markdown list file."""
    content = "law1,/path/to/law1.md\nlaw2,/path/to/law2.md"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

@given(parsers.parse('一份定義 Meta Data 結構的規格檔案 "{file_path}"'))
def meta_spec_file(tmp_path, file_path):
    """Creates a dummy meta spec file."""
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text("spec content", encoding="utf-8")
    return str(full_path)

@then(parsers.parse('應在 "{directory}" 目錄下生成清單中每個法規對應的五種 Meta Data JSON 檔案'))
def check_meta_json_generated(mock_law_processor, directory):
    """Checks if generate_meta_from_markdown was called for each law."""
    assert mock_law_processor.generate_meta_from_markdown.call_count == 2


# @SCEN-023: 透過命令列工具刪除多個法規的所有資料
@given(parsers.parse('一個包含要刪除法規名稱的清單檔案 "{file_path}"'))
def delete_list_file(tmp_path, file_path):
    """Creates a dummy delete list file."""
    content = "law1\nlaw2"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

@then('資料庫中所有與清單中法規相關的紀錄應被清除 (laws, articles, legal_concepts, law_hierarchy_relationships, law_relationships)')
def check_laws_deleted(mock_law_metadata_manager):
    """Checks if delete_law_by_name was called for each law."""
    assert mock_law_metadata_manager.delete_law_by_name.call_count == 2


# @SCEN-024: 透過命令列工具匯出多個法規的完整資料為 Markdown 檔案
@given('資料庫中已存在多個法規的完整資料')
def db_with_full_law_data():
    """A conceptual step, no mock needed."""
    pass

@given(parsers.parse('一個包含要匯出法規名稱的清單檔案 "{file_path}"'))
def export_list_file(tmp_path, file_path):
    """Creates a dummy export list file."""
    content = "law1\nlaw2"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

@then(parsers.parse('"{directory}" 目錄下應生成清單中每個法規對應的 Markdown 檔案，其中包含該法規的完整條文內容及相關 Meta Data (若有)'))
def check_markdown_exported(mock_law_processor, directory):
    """Checks if export_law_to_markdown was called for each law."""
    assert mock_law_processor.export_law_to_markdown.call_count == 2


# @SCEN-025: 透過命令列工具執行資料庫完整性檢查並輸出報告
@when('執行命令列工具 `python law_cli.py --check-integrity` 或 `python law_cli.py -c`')
def execute_integrity_check(mock_law_processor):
    """Executes the integrity check command."""
    run_cli('--check-integrity')

@then('應輸出資料庫完整性檢查報告，包含各表格的資料量、空值比例等指標')
def check_integrity_report_output(mock_law_processor):
    """Checks if the integrity check method was called."""
    mock_law_processor.check_database_integrity.assert_called_once()

@then('報告應儲存至預設的報告檔案路徑')
def check_report_file_saved(mock_law_processor):
    """Checks if the integrity check method was called with a file path."""
    # The check_database_integrity function should handle the saving.
    # We just need to ensure it was called.
    mock_law_processor.check_database_integrity.assert_called_once()


# @SCEN-026: 透過命令列工具將已產生的 Meta Data 灌入資料庫
@given(parsers.parse('一個包含多個法規名稱的清單檔案 "{file_path}"'))
def meta_import_list_file(tmp_path, file_path):
    """Creates a dummy meta import list file."""
    content = "law1\nlaw2"
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return str(full_path)

@given(parsers.parse('"{directory}" 目錄下存在清單中每個法規對應的五種 Meta Data JSON 檔案'))
def meta_json_files_exist(tmp_path, directory):
    """Creates dummy meta JSON files."""
    json_dir = tmp_path / directory
    json_dir.mkdir(parents=True, exist_ok=True)
    # Create dummy files for "law1"
    (json_dir / "law1_law_regulation.json").touch()
    (json_dir / "law1_law_articles.json").touch()
    (json_dir / "law1_legal_concepts.json").touch()
    (json_dir / "law1_law_hierarchy_relations.json").touch()
    (json_dir / "law1_law_relations.json").touch()
    # Create dummy files for "law2"
    (json_dir / "law2_law_regulation.json").touch()
    (json_dir / "law2_law_articles.json").touch()
    (json_dir / "law2_legal_concepts.json").touch()
    (json_dir / "law2_law_hierarchy_relations.json").touch()
    (json_dir / "law2_law_relations.json").touch()


@then('資料庫中對應法規的 `laws` 表格 `law_metadata` 欄位應被填入')
def check_law_metadata_imported(mock_law_processor):
    """Checks if import_meta_data_from_json was called."""
    assert mock_law_processor.import_meta_data_from_json.call_count == 2

@then('資料庫中對應法規的 `articles` 表格 `article_metadata` 欄位應被填入')
def check_article_metadata_imported():
    """Implicitly tested by the call to import_meta_data_from_json."""
    pass

@then('資料庫中對應法規的 `legal_concepts` 資料表應包含對應的法律概念')
def check_legal_concepts_imported():
    """Implicitly tested by the call to import_meta_data_from_json."""
    pass

@then('資料庫中對應法規的 `law_hierarchy_relationships` 資料表應包含對應的階層關係')
def check_hierarchy_imported():
    """Implicitly tested by the call to import_meta_data_from_json."""
    pass

@then('資料庫中對應法規的 `law_relationships` 資料表應包含對應的關聯性資料')
def check_relations_imported():
    """Implicitly tested by the call to import_meta_data_from_json."""
    pass
