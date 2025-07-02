
"""
This module contains the step definitions for BDD integration tests that connect to a live PostgreSQL database.
It uses a setup/teardown approach to ensure existing data is not affected.
"""
import os
import sys
import subprocess
import psycopg2
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
import dotenv

# Add project root to the Python path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
dotenv.load_dotenv()

# --- Load scenarios from the integration feature file ---
scenarios('../features/integration_tests.feature')

# --- Fixture for safe, direct database connection ---

@pytest.fixture(scope='function')
def safe_db_connection():
    """Connects to a live database, cleans up specific test data before and after the test."""
    conn_details = {
        "host": os.getenv('DB_HOST', 'localhost'),
        "port": os.getenv('DB_PORT', '5432'),
        "user": os.getenv('DB_USER', 'lawuser'),
        "password": os.getenv('DB_PASSWORD', 'lawpassword'),
        "dbname": os.getenv('DB_NAME', 'lawdb')
    }
    test_law_names = ["中華民國憲法", "國家安全會議組織法"]

    def cleanup_test_data():
        try:
            conn = psycopg2.connect(**conn_details)
            with conn.cursor() as cursor:
                for law_name in test_law_names:
                    # Delete only the specific test law. Cascade should handle related articles.
                    cursor.execute("DELETE FROM laws WHERE xml_law_name = %s;", (law_name,))
            conn.commit()
            conn.close()
        except psycopg2.Error as e:
            # If cleanup fails, print a warning but don't fail the test run
            print(f"\nWARNING: Failed to clean up test data. Error: {e}")

    # --- Setup: Clean up any leftover data from a previous failed run ---
    cleanup_test_data()

    yield conn_details

    # --- Teardown: Clean up data created during the test ---
    cleanup_test_data()


# --- Step Definitions ---

@given(parsers.parse('一個內容已知的法規 XML 檔案 "{file_path}" 和一個指向該檔案的清單檔案 "{list_file_path}"'), target_fixture='xml_file_for_integration')
def known_xml_file_for_integration(tmp_path, file_path, list_file_path):
    # We will use the actual data/xml_sample.xml
    return os.path.abspath("data/xml_sample.xml")

@given('一個乾淨且準備就緒的測試資料庫')
def clean_test_database(safe_db_connection):
    # The fixture ensures the specific test data is not present
    pass

@given('資料庫中已存在多個法規')
def laws_exist_in_db(safe_db_connection):
    conn = psycopg2.connect(**safe_db_connection)
    cur = conn.cursor()
    # Insert some dummy laws for testing update scenarios
    cur.execute("INSERT INTO laws (pcode, xml_law_name, xml_law_nature, xml_latest_change_date) VALUES (%s, %s, %s, %s) ON CONFLICT (pcode) DO NOTHING", ('Y0000001', '預算法', '法律', '2023-01-01'))
    cur.execute("INSERT INTO laws (pcode, xml_law_name, xml_law_nature, xml_latest_change_date) VALUES (%s, %s, %s, %s) ON CONFLICT (pcode) DO NOTHING", ('P0000001', '政府採購法', '法律', '2023-02-01'))
    cur.execute("INSERT INTO laws (pcode, xml_law_name, xml_law_nature, xml_latest_change_date) VALUES (%s, %s, %s, %s) ON CONFLICT (pcode) DO NOTHING", ('C0000001', '中醫藥發展法', '法律', '2023-03-01'))
    conn.commit()
    cur.close()
    conn.close()

@when(parsers.parse('執行命令列工具匯入該清單檔案'))
def run_cli_for_integration(xml_file_for_integration, safe_db_connection):
    env = os.environ.copy()
    env["DB_HOST"] = safe_db_connection["host"]
    env["DB_PORT"] = safe_db_connection["port"]
    env["DB_USER"] = safe_db_connection["user"]
    env["DB_PASSWORD"] = safe_db_connection["password"]
    env["DB_NAME"] = safe_db_connection["dbname"]

    command = [
        sys.executable,
        "law_cli.py",
        "--import-xml", # Use --import-xml for the single XML file
        xml_file_for_integration # This is now data/xml_sample.xml
    ]
    subprocess.run(command, check=True, env=env)

@when(parsers.parse('執行命令列工具 `python law_cli.py --update-summary {summary_file_path}`'))
def run_cli_update_summary(summary_file_path, safe_db_connection):
    env = os.environ.copy()
    env["DB_HOST"] = safe_db_connection["host"]
    env["DB_PORT"] = safe_db_connection["port"]
    env["DB_USER"] = safe_db_connection["user"]
    env["DB_PASSWORD"] = safe_db_connection["password"]
    env["DB_NAME"] = safe_db_connection["dbname"]

    command = [
        sys.executable,
        "law_cli.py",
        "--update-summary",
        summary_file_path
    ]
    subprocess.run(command, check=True, env=env)

@then(parsers.parse('資料庫的 "{table_name}" 資料表中應包含 "{law_name}" 的紀錄'))
def check_law_record_in_db(safe_db_connection, table_name, law_name):
    conn = psycopg2.connect(**safe_db_connection)
    with conn.cursor() as cursor:
        cursor.execute(f"SELECT xml_law_name FROM {table_name} WHERE xml_law_name = %s", (law_name,))
        result = cursor.fetchone()
        assert result is not None, f"Law '{law_name}' not found in table '{table_name}'"
        assert result[0] == law_name
        print(f"\n--- 驗證法規匯入成功 ---")
        print(f"已找到法規: {result[0]}")
        # 額外查詢並顯示「中華民國憲法增修條文」的資訊
        cursor.execute("SELECT pcode, xml_law_name, xml_law_nature, xml_latest_change_date FROM laws WHERE xml_law_name = '中華民國憲法增修條文';")
        constitution_result = cursor.fetchone()
        if constitution_result:
            print(f"\n--- 中華民國憲法增修條文資訊 ---")
            print(f"PCode: {constitution_result[0]}")
            print(f"法規名稱: {constitution_result[1]}")
            print(f"法規性質: {constitution_result[2]}")
            print(f"最新異動日期: {constitution_result[3]}")
        else:
            print(f"\n--- 未找到中華民國憲法增修條文 ---")
    conn.close()

@then(parsers.parse('"{table_name}" 資料表中清單中所有法規紀錄的 "{column_name}" 欄位應被更新'))
def check_summary_updated(safe_db_connection, table_name, column_name):
    conn = psycopg2.connect(**safe_db_connection)
    with conn.cursor() as cursor:
        # Check for '預算法'
        cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE xml_law_name = %s", ('預算法',))
        result = cursor.fetchone()
        assert result is not None, "預算法 not found"
        assert result[0] is not None and result[0] != '', "預算法 summary not updated"
        print(f"預算法 {column_name} 已更新: {result[0][:50]}...")

        # Check for '政府採購法'
        cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE xml_law_name = %s", ('政府採購法',))
        result = cursor.fetchone()
        assert result is not None, "政府採購法 not found"
        assert result[0] is not None and result[0] != '', "政府採購法 summary not updated"
        print(f"政府採購法 {column_name} 已更新: {result[0][:50]}...")

        # Check for '中醫藥發展法'
        cursor.execute(f"SELECT {column_name} FROM {table_name} WHERE xml_law_name = %s", ('中醫藥發展法',))
        result = cursor.fetchone()
        assert result is not None, "中醫藥發展法 not found"
        assert result[0] is not None and result[0] != '', "中醫藥發展法 summary not updated"
        print(f"中醫藥發展法 {column_name} 已更新: {result[0][:50]}...")
    conn.close()

@then(parsers.parse('資料庫的 "{table_name}" 資料表中應包含 "{law_name}" 的 {count:d} 筆法條紀錄'))
def check_article_count_in_db(safe_db_connection, table_name, law_name, count):
    conn = psycopg2.connect(**safe_db_connection)
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(a.id)
            FROM articles a
            JOIN laws l ON a.law_id = l.id
            WHERE l.xml_law_name = %s
        """, (law_name,))
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == count, f"Expected {count} articles for law '{law_name}', but found {result[0]}"
    conn.close()
