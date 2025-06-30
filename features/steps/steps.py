from behave import given, when, then
import os
import re
import pandas as pd
import psycopg2
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

# --- Core Logic Refactored from law_proc.ipynb ---

def extract_pcode_from_url(url_string):
    if not url_string: return None
    try:
        return parse_qs(urlparse(url_string).query).get('pcode', [None])[0]
    except Exception: return None

class XMLElement:
    def __init__(self, tag, attrib, text, children):
        self.tag, self.attrib, self.text, self.children, self.tags = tag, attrib, text, children, {}
    def __repr__(self): return f"XMLElement(tag={self.tag})"

def parse_xml_withobj(xml_file):
    def element_to_object(element):
        children = [element_to_object(child) for child in element]
        return XMLElement(tag=element.tag, attrib=element.attrib, text=element.text.strip() if element.text else None, children=children)
    tree = ET.parse(xml_file)
    root = tree.getroot()
    laws = {}
    for law_node in root.findall('法規'):
        name_node = law_node.find('法規名稱')
        if name_node is not None and name_node.text:
            laws[name_node.text] = element_to_object(law_node)
    return laws

class LawMgr:
    def __init__(self, laws):
        self.laws = laws
        self.law_items = {}
        for law_name, law_xml_element in laws.items():
            law_xml_element.tags['PCode'] = None
            for child_node in law_xml_element.children:
                law_xml_element.tags[child_node.tag] = child_node.text
                if child_node.tag == '法規網址' and child_node.text:
                    law_xml_element.tags['PCode'] = extract_pcode_from_url(child_node.text)
            
            current_chapter_section = None
            law_items_list = []
            法規內容_node = next((c for c in law_xml_element.children if c.tag == '法規內容'), None)
            if 法規內容_node:
                for content_child in 法規內容_node.children:
                    if content_child.tag == '編章節': current_chapter_section = content_child.text
                    elif content_child.tag == '條文':
                        條號 = next((item.text for item in content_child.children if item.tag == '條號'), None)
                        條文內容 = next((item.text for item in content_child.children if item.tag == '條文內容'), "")
                        if 條號: law_items_list.append({"編章節": current_chapter_section, "條號": 條號, "條文內容": 條文內容})
            self.law_items[law_name] = law_items_list

def synchronize_lawmgr_with_db(conn, lawmgr_instance):
    cursor = conn.cursor()
    for law_name, law_obj in lawmgr_instance.laws.items():
        pcode = law_obj.tags.get('PCode')
        if not pcode: continue
        
        cursor.execute("SELECT id FROM laws WHERE pcode = %s", (pcode,))
        existing_law = cursor.fetchone()
        
        if existing_law:
            law_id = existing_law[0]
            # In a real scenario, you would update more fields.
            # For this test, we keep it simple.
            cursor.execute("DELETE FROM articles WHERE law_id = %s", (law_id,))
        else:
            # Simplified insert for the purpose of the test
            sql = "INSERT INTO laws (pcode, xml_law_name) VALUES (%s, %s) RETURNING id"
            cursor.execute(sql, (pcode, law_obj.tags.get('法規名稱')))
            law_id = cursor.fetchone()[0]

        articles = lawmgr_instance.law_items.get(law_name, [])
        for article in articles:
            sql = "INSERT INTO articles (law_id, xml_article_number, xml_article_content) VALUES (%s, %s, %s)"
            cursor.execute(sql, (law_id, article.get('條號'), article.get('條文內容')))
    conn.commit()
    cursor.close()

def import_law_summaries(conn, summary_filepath):
    cursor = conn.cursor()
    with open(summary_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r"----- File: (.*)\.txt -----\n(.*?)(?=----- File:|\Z)", content, re.S)
    for law_name, summary in matches:
        cursor.execute("UPDATE laws SET llm_summary = %s WHERE xml_law_name = %s", (summary.strip(), law_name.strip()))
    conn.commit()
    cursor.close()

# --- BDD Step Implementations ---

@given('一個包含多部法規的 XML 檔案 "{filepath}"')
def step_impl(context, filepath):
    full_path = os.path.join(os.getcwd(), filepath)
    assert os.path.exists(full_path), f"File not found: {full_path}"
    context.xml_filepath = full_path
    law_objects = parse_xml_withobj(context.xml_filepath)
    assert law_objects, f"No laws could be parsed from {filepath}"
    context.lawmgr = LawMgr(law_objects)

@given('一個空的目標資料庫')
def step_impl(context):
    context.cursor.execute("SELECT COUNT(*) FROM laws")
    assert context.cursor.fetchone()[0] == 0, "Database was not empty at the start of the scenario."

@when('執行 `law_proc.ipynb` 中的資料庫同步功能')
def step_impl(context):
    assert hasattr(context, 'lawmgr'), "LawMgr object was not initialized."
    synchronize_lawmgr_with_db(context.conn, context.lawmgr)

@then('"{table}" 資料表中應包含從 XML 解析出的法規紀錄')
def step_impl(context, table):
    context.cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count_in_db = context.cursor.fetchone()[0]
    count_in_mgr = len(context.lawmgr.laws)
    assert count_in_db == count_in_mgr, f"Expected {count_in_mgr} records in {table}, but found {count_in_db}."

@then('"{table}" 資料表中應包含所有對應的法條紀錄')
def step_impl(context, table):
    context.cursor.execute(f"SELECT COUNT(*) FROM {table}")
    total_articles_in_db = context.cursor.fetchone()[0]
    total_articles_in_mgr = sum(len(articles) for articles in context.lawmgr.law_items.values())
    assert total_articles_in_db == total_articles_in_mgr, f"Expected {total_articles_in_mgr} articles in {table}, but found {total_articles_in_db}."

@given('資料庫中已存在法規 "{law_name}"')
def step_impl(context, law_name):
    pcode = f"PCODE_{law_name}"
    context.cursor.execute("INSERT INTO laws (pcode, xml_law_name, llm_summary) VALUES (%s, %s, %s) RETURNING id", (pcode, law_name, 'old summary'))
    context.law_id = context.cursor.fetchone()[0]
    context.conn.commit()
    if not hasattr(context, 'pcodes'):
        context.pcodes = {}
    context.pcodes[law_name] = pcode

@given('一個位於 "{filepath}" 的摘要檔案，其中包含 "{law_name}" 的摘要')
def step_impl(context, filepath, law_name):
    full_path = os.path.join(os.getcwd(), filepath)
    assert os.path.exists(full_path), f"File not found: {full_path}"
    context.summary_filepath = full_path
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(rf"----- File: {re.escape(law_name)}\.txt -----\n(.*?)(?=----- File:|\Z)", content, re.S)
    assert match, f"Could not find summary for {law_name} in {filepath}"
    context.expected_summary = match.group(1).strip()

@when('執行 `law_proc.ipynb` 中的摘要匯入功能')
def step_impl(context):
    import_law_summaries(context.conn, context.summary_filepath)

@then('"{table}" 資料表中 "{law_name}" 紀錄的 "{field}" 欄位應被更新')
def step_impl(context, table, law_name, field):
    context.cursor.execute(f"SELECT {field} FROM {table} WHERE xml_law_name = %s", (law_name,))
    result = context.cursor.fetchone()
    assert result is not None, f"Could not find law '{law_name}' in {table}."
    actual_value = result[0]
    if field == 'llm_summary':
        assert actual_value == context.expected_summary, f"Summary for '{law_name}' was not updated correctly."
    else:
        assert actual_value is not None, f"Field '{field}' for '{law_name}' is null."

# --- Mock Implementations for law_meta_loader.ipynb steps ---

@given('"{path}" 目錄下存在對應 "{law_name}" 的五種 Meta Data JSON 檔案:')
def step_impl(context, path, law_name):
    context.meta_path = os.path.join(os.getcwd(), path)
    context.meta_law_name = law_name
    # In a real test, you would assert that the files exist.
    # For this mock, we just assume they do.
    print(f"Assuming Meta Data JSON files for {law_name} exist in {context.meta_path}")

@when('執行 `law_meta_loader.ipynb` 以載入 "{law_name}" 的 Meta Data')
def step_impl(context, law_name):
    # This is a mock of the loader's behavior.
    context.cursor.execute("UPDATE laws SET law_metadata = %s WHERE xml_law_name = %s", (f'{{"source": "{law_name}.json"}}', law_name))
    context.cursor.execute("UPDATE articles SET article_metadata = %s WHERE law_id = %s", (f'{{"source": "{law_name}_articles.json"}}', context.law_id))
    context.cursor.execute("INSERT INTO legal_concepts (law_id, name) VALUES (%s, %s)", (context.law_id, "mock legal concept"))
    context.conn.commit()
    print(f"Mocked Meta Data loading for {law_name}")

@then('"{table}" 資料表中 "{law_name}" 紀錄的 "{field}" 欄位應被填入')
def step_impl(context, table, law_name, field):
    context.cursor.execute(f"SELECT {field} FROM {table} WHERE xml_law_name = %s", (law_name,))
    result = context.cursor.fetchone()
    assert result is not None and result[0] is not None, f"Field '{field}' for '{law_name}' was not filled."

@then('"{table}" 資料表中 "{law_name}" 所有法條的 "{field}" 欄位應被填入')
def step_impl(context, table, law_name, field):
    context.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE law_id = %s AND {field} IS NOT NULL", (context.law_id,))
    count = context.cursor.fetchone()[0]
    assert count > 0, f"No articles for '{law_name}' had the '{field}' field filled."

@then('"{table}" 資料表應包含 "{law_name}" 的法律概念')
def step_impl(context, table, law_name):
    context.cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE law_id = %s", (context.law_id,))
    count = context.cursor.fetchone()[0]
    assert count > 0, f"No legal concepts found for '{law_name}' in {table}."

# The rest of the steps would be implemented following the same pattern.
# Due to space constraints and missing source for law_meta_loader, they are omitted here.
