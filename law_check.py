# law_check.py

import psycopg2
import os
import re
import pandas as pd # Included as it's in law_proc.ipynb, though might not be strictly needed for all checks
from dotenv import load_dotenv
load_dotenv()

# --- PostgreSQL Connection Configuration (Copied from law_proc.ipynb) ---
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_NAME = "test_law_db_agent"

# Placeholder for the database connection object
db_connection = None
db_cursor = None

def get_db_params():
    params = {
        'host': os.getenv("DB_HOST", DB_HOST),
        'port': os.getenv("DB_PORT", DB_PORT),
        'user': os.getenv("DB_USER", DB_USER),
        'password': os.getenv("DB_PASSWORD", DB_PASSWORD),
        'dbname': os.getenv("DB_NAME", DB_NAME)
    }
    return params

def connect_db():
    global db_connection, db_cursor
    if db_connection and not db_connection.closed:
        print("Already connected to the database.")
        return True

    params = get_db_params()
    try:
        print(f"Connecting to PostgreSQL: {params['user']}@{params['host']}:{params['port']}/{params['dbname']}...")
        db_connection = psycopg2.connect(**params)
        db_cursor = db_connection.cursor()
        print("Successfully connected to PostgreSQL.")
        return True
    except psycopg2.Error as e:
        db_connection = None
        db_cursor = None
        print(f"Error connecting to PostgreSQL: {e}")
        return False

def disconnect_db():
    global db_connection, db_cursor
    if db_cursor:
        db_cursor.close()
        db_cursor = None
    if db_connection:
        db_connection.close()
        db_connection = None
        print("Disconnected from PostgreSQL.")
    else:
        print("Not connected to any database.")

def check_db_connection():
    global db_connection, db_cursor
    if not db_connection or db_connection.closed != 0:
        print("No active database connection.")
        return False
    try:
        db_cursor.execute("SELECT 1;")
        db_cursor.fetchone()
        print("Database connection is active.")
        return True
    except psycopg2.Error as e:
        print(f"Database connection check failed: {e}")
        # Attempt to reconnect or advise user
        return False

# --- Helper Functions for Data Conversion (Copied from law_proc.ipynb) ---
def str_to_date_for_sql(date_str): # Helper for YYYYMMDD string to be used with TO_DATE
    if date_str and isinstance(date_str, str) and len(date_str) == 8:
        try:
            int(date_str)
            return date_str
        except ValueError:
            return None
    return None

def str_to_bool(yn_str): # Helper for 'Y'/'N'
    if yn_str == 'Y':
        return True
    if yn_str == 'N':
        return False
    return None

def get_law_from_db(pcode_val):
    global db_cursor, db_connection
    if not db_cursor or not db_connection or (hasattr(db_connection, 'closed') and db_connection.closed != 0):
        return None
    try:
        db_cursor.execute("SELECT * FROM laws WHERE pcode = %s AND is_active = TRUE;", (pcode_val,))
        colnames = [desc[0] for desc in db_cursor.description]
        row = db_cursor.fetchone()
        if row:
            return dict(zip(colnames, row))
        return None
    except Exception as e:
        print(f"Error fetching law {pcode_val} from DB: {e}")
        return None

# --- Original law_check.py functions, modified to use direct DB connection ---

def check_laws_table_integrity():
    """
    @SCEN-010 Scenario: 檢查 laws 表格資料完整性
    """
    print("--- 檢查 laws 表格資料完整性 (SCEN-010) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 檢查 laws 表格應包含至少一筆紀錄
        db_cursor.execute("SELECT COUNT(*) FROM laws;")
        count = db_cursor.fetchone()[0]
        if count > 0:
            print(f"PASS: laws 表格包含 {count} 筆紀錄。")
        else:
            print("FAIL: laws 表格沒有任何紀錄。")
            return False

        # 檢查 pcode 和 xml_law_name 欄位不應為空
        db_cursor.execute("SELECT COUNT(*) FROM laws WHERE pcode IS NULL OR xml_law_name IS NULL OR pcode = '' OR xml_law_name = '';")
        empty_count = db_cursor.fetchone()[0]
        if empty_count == 0:
            print("PASS: laws 表格中所有紀錄的 pcode 和 xml_law_name 欄位皆不為空。")
        else:
            print(f"FAIL: laws 表格中有 {empty_count} 筆紀錄的 pcode 或 xml_law_name 欄位為空。")
            return False

        # 檢查 law_metadata 欄位應為有效的 JSONB 格式且不為空
        db_cursor.execute("SELECT COUNT(*) FROM laws WHERE law_metadata IS NULL OR law_metadata::text = 'null' OR law_metadata::text = '{}';")
        empty_metadata_count = db_cursor.fetchone()[0]
        if empty_metadata_count == 0:
            print("PASS: laws 表格中所有紀錄的 law_metadata 欄位皆為有效的 JSONB 格式且不為空。")
        else:
            print(f"FAIL: laws 表格中有 {empty_metadata_count} 筆紀錄的 law_metadata 欄位為空或無效。")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 檢查 laws 表格資料完整性時發生錯誤: {e}")
        return False

def check_articles_table_integrity():
    """
    @SCEN-011 Scenario: 檢查 articles 表格資料完整性
    """
    print("\n--- 檢查 articles 表格資料完整性 (SCEN-011) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 檢查 articles 表格應包含至少一筆紀錄
        db_cursor.execute("SELECT COUNT(*) FROM articles;")
        count = db_cursor.fetchone()[0]
        if count > 0:
            print(f"PASS: articles 表格包含 {count} 筆紀錄。")
        else:
            print("FAIL: articles 表格沒有任何紀錄。")
            return False

        # 檢查 law_id 和 xml_article_number 欄位不應為空
        db_cursor.execute("SELECT COUNT(*) FROM articles WHERE law_id IS NULL OR xml_article_number IS NULL OR xml_article_number = '';")
        empty_count = db_cursor.fetchone()[0]
        if empty_count == 0:
            print("PASS: articles 表格中所有紀錄的 law_id 和 xml_article_number 欄位皆不為空。")
        else:
            print(f"FAIL: articles 表格中有 {empty_count} 筆紀錄的 law_id 或 xml_article_number 欄位為空。")
            return False

        # 檢查 article_metadata 欄位應為有效的 JSONB 格式且不為空
        db_cursor.execute("SELECT COUNT(*) FROM articles WHERE article_metadata IS NULL OR article_metadata::text = 'null' OR article_metadata::text = '{}';")
        empty_metadata_count = db_cursor.fetchone()[0]
        if empty_metadata_count == 0:
            print("PASS: articles 表格中所有紀錄的 article_metadata 欄位皆為有效的 JSONB 格式且不為空。")
        else:
            print(f"FAIL: articles 表格中有 {empty_metadata_count} 筆紀錄的 article_metadata 欄位為空或無效。")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 檢查 articles 表格資料完整性時發生錯誤: {e}")
        return False

def check_legal_concepts_table_integrity():
    """
    @SCEN-012 Scenario: 檢查 legal_concepts 表格資料完整性
    """
    print("\n--- 檢查 legal_concepts 表格資料完整性 (SCEN-012) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 檢查 legal_concepts 表格應包含至少一筆紀錄
        db_cursor.execute("SELECT COUNT(*) FROM legal_concepts;")
        count = db_cursor.fetchone()[0]
        if count > 0:
            print(f"PASS: legal_concepts 表格包含 {count} 筆紀錄。")
        else:
            print("FAIL: legal_concepts 表格沒有任何紀錄。")
            return False

        # 檢查 law_id, code 和 name 欄位不應為空
        db_cursor.execute("SELECT COUNT(*) FROM legal_concepts WHERE law_id IS NULL OR code IS NULL OR name IS NULL OR code = '' OR name = '';")
        empty_count = db_cursor.fetchone()[0]
        if empty_count == 0:
            print("PASS: legal_concepts 表格中所有紀錄的 law_id, code 和 name 欄位皆不為空。")
        else:
            print(f"FAIL: legal_concepts 表格中有 {empty_count} 筆紀錄的 law_id, code 或 name 欄位為空。")
            return False

        # 檢查 data 欄位應為有效的 JSONB 格式且不為空
        db_cursor.execute("SELECT COUNT(*) FROM legal_concepts WHERE data IS NULL OR data::text = 'null' OR data::text = '{}';")
        empty_data_count = db_cursor.fetchone()[0]
        if empty_data_count == 0:
            print("PASS: legal_concepts 表格中所有紀錄的 data 欄位皆為有效的 JSONB 格式且不為空。")
        else:
            print(f"FAIL: legal_concepts 表格中有 {empty_data_count} 筆紀錄的 data 欄位為空或無效。")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 檢查 legal_concepts 表格資料完整性時發生錯誤: {e}")
        return False

def check_law_hierarchy_relationships_table_integrity():
    """
    @SCEN-013 Scenario: 檢查 law_hierarchy_relationships 表格資料完整性
    """
    print("\n--- 檢查 law_hierarchy_relationships 表格資料完整性 (SCEN-013) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 檢查 law_hierarchy_relationships 表格應包含至少一筆紀錄
        db_cursor.execute("SELECT COUNT(*) FROM law_hierarchy_relationships;")
        count = db_cursor.fetchone()[0]
        if count > 0:
            print(f"PASS: law_hierarchy_relationships 表格包含 {count} 筆紀錄。")
        else:
            print("FAIL: law_hierarchy_relationships 表格沒有任何紀錄。")
            return False

        # 檢查 main_law_id, related_law_id 和 hierarchy_type 欄位不應為空
        db_cursor.execute("SELECT COUNT(*) FROM law_hierarchy_relationships WHERE main_law_id IS NULL OR related_law_id IS NULL OR hierarchy_type IS NULL OR hierarchy_type = '';")
        empty_count = db_cursor.fetchone()[0]
        if empty_count == 0:
            print("PASS: law_hierarchy_relationships 表格中所有紀錄的 main_law_id, related_law_id 和 hierarchy_type 欄位皆不為空。")
        else:
            print(f"FAIL: law_hierarchy_relationships 表格中有 {empty_count} 筆紀錄的 main_law_id, related_law_id 或 hierarchy_type 欄位為空。")
            return False

        # 檢查 data 欄位應為有效的 JSONB 格式且不為空
        db_cursor.execute("SELECT COUNT(*) FROM law_hierarchy_relationships WHERE data IS NULL OR data::text = 'null' OR data::text = '{}';")
        empty_data_count = db_cursor.fetchone()[0]
        if empty_data_count == 0:
            print("PASS: law_hierarchy_relationships 表格中所有紀錄的 data 欄位皆為有效的 JSONB 格式且不為空。")
        else:
            print(f"FAIL: law_hierarchy_relationships 表格中有 {empty_data_count} 筆紀錄的 data 欄位為空或無效。")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 檢查 law_hierarchy_relationships 表格資料完整性時發生錯誤: {e}")
        return False

def check_law_relationships_table_integrity():
    """
    @SCEN-014 Scenario: 檢查 law_relationships 表格資料完整性
    """
    print("\n--- 檢查 law_relationships 表格資料完整性 (SCEN-014) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 檢查 law_relationships 表格應包含至少一筆紀錄
        db_cursor.execute("SELECT COUNT(*) FROM law_relationships;")
        count = db_cursor.fetchone()[0]
        if count > 0:
            print(f"PASS: law_relationships 表格包含 {count} 筆紀錄。")
        else:
            print("FAIL: law_relationships 表格沒有任何紀錄。")
            return False

        # 檢查 relationship_type 欄位不應為空
        db_cursor.execute("SELECT COUNT(*) FROM law_relationships WHERE relationship_type IS NULL OR relationship_type = '';")
        empty_count = db_cursor.fetchone()[0]
        if empty_count == 0:
            print("PASS: law_relationships 表格中所有紀錄的 relationship_type 欄位皆不為空。")
        else:
            print(f"FAIL: law_relationships 表格中有 {empty_count} 筆紀錄的 relationship_type 欄位為空。")
            return False

        # 檢查 data 欄位應為有效的 JSONB 格式且不為空
        db_cursor.execute("SELECT COUNT(*) FROM law_relationships WHERE data IS NULL OR data::text = 'null' OR data::text = '{}';")
        empty_data_count = db_cursor.fetchone()[0]
        if empty_data_count == 0:
            print("PASS: law_relationships 表格中所有紀錄的 data 欄位皆為有效的 JSONB 格式且不為空。")
        else:
            print(f"FAIL: law_relationships 表格中有 {empty_data_count} 筆紀錄的 data 欄位為空或無效。")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 檢查 law_relationships 表格資料完整性時發生錯誤: {e}")
        return False

def check_specific_law_consistency(law_name="政府採購法"):
    """
    @SCEN-015 Scenario: 檢查特定法規的資料一致性
    """
    print(f"\n--- 檢查特定法規 '{law_name}' 的資料一致性 (SCEN-015) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 取得法規 ID
        db_cursor.execute(f"SELECT id FROM laws WHERE xml_law_name = %s;", (law_name,))
        result = db_cursor.fetchone()
        if not result:
            print(f"FAIL: 未找到法規 '{law_name}' 的紀錄。")
            return False
        law_id = result[0]
        print(f"找到法規 '{law_name}' 的 ID: {law_id}")

        # 檢查 articles 關聯
        db_cursor.execute(f"SELECT COUNT(*) FROM articles WHERE law_id = %s;", (law_id,))
        article_count = db_cursor.fetchone()[0]
        if article_count > 0:
            print(f"PASS: articles 表格中找到 {article_count} 筆與 '{law_name}' 相關的法條。")
        else:
            print(f"FAIL: articles 表格中未找到與 '{law_name}' 相關的法條。")
            return False

        # 檢查 legal_concepts 關聯
        db_cursor.execute(f"SELECT COUNT(*) FROM legal_concepts WHERE law_id = %s;", (law_id,))
        concept_count = db_cursor.fetchone()[0]
        if concept_count > 0:
            print(f"PASS: legal_concepts 表格中找到 {concept_count} 筆與 '{law_name}' 相關的法律概念。")
        else:
            print(f"FAIL: legal_concepts 表格中未找到與 '{law_name}' 相關的法律概念。")
            return False

        # 檢查 law_hierarchy_relationships 關聯
        db_cursor.execute(f"SELECT COUNT(*) FROM law_hierarchy_relationships WHERE main_law_id = %s OR related_law_id = %s;", (law_id, law_id))
        hierarchy_count = db_cursor.fetchone()[0]
        if hierarchy_count > 0:
            print(f"PASS: law_hierarchy_relationships 表格中找到 {hierarchy_count} 筆與 '{law_name}' 相關的階層關係。")
        else:
            print(f"FAIL: law_hierarchy_relationships 表格中未找到與 '{law_name}' 相關的階層關係。")
            return False

        # 檢查 law_relationships 關聯
        db_cursor.execute(f"SELECT COUNT(*) FROM law_relationships WHERE main_law_id = %s OR related_law_id = %s;", (law_id, law_id))
        relationship_count = db_cursor.fetchone()[0]
        if relationship_count > 0:
            print(f"PASS: law_relationships 表格中找到 {relationship_count} 筆與 '{law_name}' 相關的關聯性資料。")
        else:
            print(f"FAIL: law_relationships 表格中未找到與 '{law_name}' 相關的關聯性資料。")
            return False

        # 檢查 llm_summary 和 llm_keywords 欄位不應為空
        db_cursor.execute(f"SELECT COUNT(*) FROM laws WHERE xml_law_name = %s AND (llm_summary IS NULL OR llm_summary = '' OR llm_keywords IS NULL OR llm_keywords = '');", (law_name,))
        empty_llm_count = db_cursor.fetchone()[0]
        if empty_llm_count == 0:
            print(f"PASS: 法規 '{law_name}' 的 llm_summary 和 llm_keywords 欄位皆不為空。")
        else:
            print(f"FAIL: 法規 '{law_name}' 的 llm_summary 或 llm_keywords 欄位為空。")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 檢查特定法規 '{law_name}' 的資料一致性時發生錯誤: {e}")
        return False

def check_summary_keywords_completeness():
    """
    @SCEN-016 Scenario: 檢查摘要與關鍵字的缺漏情況並建立指標
    """
    print("\n--- 檢查摘要與關鍵字的缺漏情況並建立指標 (SCEN-016) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 總法規數量
        db_cursor.execute("SELECT COUNT(*) FROM laws;")
        total_laws = db_cursor.fetchone()[0]
        print(f"總法規數量: {total_laws}")

        if total_laws == 0:
            print("WARN: 無法計算比例，因為 laws 表格中沒有任何紀錄。")
            return False

        # 計算 llm_summary 欄位為空的法規數量
        db_cursor.execute("SELECT COUNT(*) FROM laws WHERE llm_summary IS NULL OR llm_summary = '';")
        empty_summary_count = db_cursor.fetchone()[0]
        print(f"llm_summary 欄位為空的法規數量: {empty_summary_count}")

        # 計算 llm_keywords 欄位為空的法規數量
        db_cursor.execute("SELECT COUNT(*) FROM laws WHERE llm_keywords IS NULL OR llm_keywords = '';")
        empty_keywords_count = db_cursor.fetchone()[0]
        print(f"llm_keywords 欄位為空的法規數量: {empty_keywords_count}")

        # 計算 llm_summary 欄位有值的法規比例
        summary_filled_percentage = (total_laws - empty_summary_count) * 100.0 / total_laws
        print(f"llm_summary 欄位有值的法規比例: {summary_filled_percentage:.2f}%")

        # 計算 llm_keywords 欄位有值的法規比例
        keywords_filled_percentage = (total_laws - empty_keywords_count) * 100.0 / total_laws
        print(f"llm_keywords 欄位有值的法規比例: {keywords_filled_percentage:.2f}%")
        return True
    except Exception as e:
        print(f"ERROR: 檢查摘要與關鍵字缺漏情況時發生錯誤: {e}")
        return False

def check_metadata_completeness():
    """
    @SCEN-017 Scenario: 檢查 Meta Data 灌入資料庫的完整性並建立指標
    """
    print("\n--- 檢查 Meta Data 灌入資料庫的完整性並建立指標 (SCEN-017) ---")
    try:
        if not check_db_connection():
            print("FAIL: 資料庫未連線。")
            return False

        # 總數量
        db_cursor.execute("SELECT COUNT(*) FROM laws;")
        total_laws = db_cursor.fetchone()[0]
        db_cursor.execute("SELECT COUNT(*) FROM articles;")
        total_articles = db_cursor.fetchone()[0]
        db_cursor.execute("SELECT COUNT(*) FROM legal_concepts;")
        total_legal_concepts = db_cursor.fetchone()[0]
        db_cursor.execute("SELECT COUNT(*) FROM law_hierarchy_relationships;")
        total_hierarchy_relationships = db_cursor.fetchone()[0]
        db_cursor.execute("SELECT COUNT(*) FROM law_relationships;")
        total_law_relationships = db_cursor.fetchone()[0]

        print(f"總法規數量: {total_laws}")
        print(f"總法條數量: {total_articles}")
        print(f"總法律概念數量: {total_legal_concepts}")
        print(f"總法規階層關係數量: {total_hierarchy_relationships}")
        print(f"總法規關聯性資料數量: {total_law_relationships}")

        # 檢查 laws 表格中 law_metadata 欄位為空的法規數量
        db_cursor.execute("SELECT COUNT(*) FROM laws WHERE law_metadata IS NULL OR law_metadata::text = 'null' OR law_metadata::text = '{}';")
        empty_law_metadata_count = db_cursor.fetchone()[0]
        print(f"laws 表格中 law_metadata 欄位為空的法規數量: {empty_law_metadata_count}")

        # 檢查 articles 表格中 article_metadata 欄位為空的法條數量
        db_cursor.execute("SELECT COUNT(*) FROM articles WHERE article_metadata IS NULL OR article_metadata::text = 'null' OR article_metadata::text = '{}';")
        empty_article_metadata_count = db_cursor.fetchone()[0]
        print(f"articles 表格中 article_metadata 欄位為空的法條數量: {empty_article_metadata_count}")

        # 檢查 legal_concepts 表格中 data 欄位為空的法律概念數量
        db_cursor.execute("SELECT COUNT(*) FROM legal_concepts WHERE data IS NULL OR data::text = 'null' OR data::text = '{}';")
        empty_legal_concept_data_count = db_cursor.fetchone()[0]
        print(f"legal_concepts 表格中 data 欄位為空的法律概念數量: {empty_legal_concept_data_count}")

        # 檢查 law_hierarchy_relationships 表格中 data 欄位為空的階層關係數量
        db_cursor.execute("SELECT COUNT(*) FROM law_hierarchy_relationships WHERE data IS NULL OR data::text = 'null' OR data::text = '{}';")
        empty_hierarchy_data_count = db_cursor.fetchone()[0]
        print(f"law_hierarchy_relationships 表格中 data 欄位為空的階層關係數量: {empty_hierarchy_data_count}")

        # 檢查 law_relationships 表格中 data 欄位為空的關聯性資料數量
        db_cursor.execute("SELECT COUNT(*) FROM law_relationships WHERE data IS NULL OR data::text = 'null' OR data::text = '{}';")
        empty_relationship_data_count = db_cursor.fetchone()[0]
        print(f"law_relationships 表格中 data 欄位為空的關聯性資料數量: {empty_relationship_data_count}")

        # 計算比例
        law_metadata_filled_percentage = (total_laws - empty_law_metadata_count) * 100.0 / total_laws if total_laws > 0 else 0
        article_metadata_filled_percentage = (total_articles - empty_article_metadata_count) * 100.0 / total_articles if total_articles > 0 else 0
        legal_concept_data_filled_percentage = (total_legal_concepts - empty_legal_concept_data_count) * 100.0 / total_legal_concepts if total_legal_concepts > 0 else 0
        hierarchy_data_filled_percentage = (total_hierarchy_relationships - empty_hierarchy_data_count) * 100.0 / total_hierarchy_relationships if total_hierarchy_relationships > 0 else 0
        relationship_data_filled_percentage = (total_law_relationships - empty_relationship_data_count) * 100.0 / total_law_relationships if total_law_relationships > 0 else 0

        print(f"laws 表格中 law_metadata 欄位有值的法規比例: {law_metadata_filled_percentage:.2f}%")
        print(f"articles 表格中 article_metadata 欄位有值的法條比例: {article_metadata_filled_percentage:.2f}%")
        print(f"legal_concepts 表格中 data 欄位有值的法律概念比例: {legal_concept_data_filled_percentage:.2f}%")
        print(f"law_hierarchy_relationships 表格中 data 欄位有值的階層關係比例: {hierarchy_data_filled_percentage:.2f}%")
        print(f"law_relationships 表格中 data 欄位有值的關聯性資料比例: {relationship_data_filled_percentage:.2f}%")
        return True
    except Exception as e:
        print(f"ERROR: 檢查 Meta Data 完整性時發生錯誤: {e}")
        return False

def main():
    print("開始執行資料庫檢查...")
    all_passed = True

    if not connect_db():
        print("無法連接到資料庫，所有檢查將被跳過。")
        return

    try:
        if not check_laws_table_integrity():
            all_passed = False
        if not check_articles_table_integrity():
            all_passed = False
        if not check_legal_concepts_table_integrity():
            all_passed = False
        if not check_law_hierarchy_relationships_table_integrity():
            all_passed = False
        if not check_law_relationships_table_integrity():
            all_passed = False
        if not check_specific_law_consistency():
            all_passed = False
        if not check_summary_keywords_completeness():
            all_passed = False
        if not check_metadata_completeness():
            all_passed = False
    finally:
        disconnect_db()

    if all_passed:
        print("\n所有資料庫檢查均通過！")
    else:
        print("\n部分資料庫檢查未通過，請檢查上述錯誤訊息。")

if __name__ == "__main__":
    main()
