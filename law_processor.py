import xml.etree.ElementTree as ET
import psycopg2
from datetime import datetime
import json
import re

class LawProcessor:
    def __init__(self, db_config):
        self.db_config = db_config

    def _get_db_connection(self):
        return psycopg2.connect(**self.db_config)

    def import_xml(self, xml_file_path, law_list=None):
        print(f"Processing XML file: {xml_file_path}")
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        laws_to_process = []
        if root.tag == 'LAWS':
            laws_to_process = root.findall('法規')
        elif root.tag == '法規':
            laws_to_process = [root]
        else:
            print(f"Error: Unexpected root tag '{root.tag}' in {xml_file_path}")
            return

        for law_elem in laws_to_process:
            xml_law_name = law_elem.find('法規名稱').text
            if law_list and xml_law_name not in law_list:
                print(f"Skipping law '{xml_law_name}' as it is not in the provided law list.")
                continue
            self._process_law_element(law_elem)

    def _process_law_element(self, law_elem):
        pcode = law_elem.find('法規網址').text.split('pcode=')[1]
        xml_law_name = law_elem.find('法規名稱').text
        xml_law_nature = law_elem.find('法規性質').text
        xml_law_url = law_elem.find('法規網址').text
        xml_law_category = law_elem.find('法規類別').text
        xml_latest_change_date_str = law_elem.find('最新異動日期').text
        xml_latest_change_date = datetime.strptime(xml_latest_change_date_str, '%Y%m%d').date() if xml_latest_change_date_str else None
        xml_effective_date = law_elem.find('生效日期').text
        xml_effective_content = law_elem.find('生效內容').text
        xml_abolition_mark = law_elem.find('廢止註記').text
        xml_is_english_translated = True if law_elem.find('是否英譯註記').text == 'Y' else False
        xml_english_law_name = law_elem.find('英文法規名稱').text
        xml_attachment = law_elem.find('附件').text
        xml_history_content = law_elem.find('沿革內容').text
        xml_preamble = law_elem.find('前言').text

        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()

            # Check if law exists
            cur.execute("SELECT id, llm_summary, llm_keywords FROM laws WHERE pcode = %s", (pcode,))
            law_data = cur.fetchone()

            if law_data:
                law_id, llm_summary, llm_keywords = law_data
                # Update existing law, preserving LLM generated fields
                cur.execute(
                    """
                    UPDATE laws SET
                        xml_law_nature = %s, xml_law_name = %s, xml_law_url = %s,
                        xml_law_category = %s, xml_latest_change_date = %s,
                        xml_effective_date = %s, xml_effective_content = %s,
                        xml_abolition_mark = %s, xml_is_english_translated = %s,
                        xml_english_law_name = %s, xml_attachment = %s,
                        xml_history_content = %s, xml_preamble = %s
                    WHERE pcode = %s
                    """,
                    (
                        xml_law_nature, xml_law_name, xml_law_url,
                        xml_law_category, xml_latest_change_date,
                        xml_effective_date, xml_effective_content,
                        xml_abolition_mark, xml_is_english_translated,
                        xml_english_law_name, xml_attachment,
                        xml_history_content, xml_preamble, pcode
                    )
                )
                print(f"Updated law: {xml_law_name} (PCode: {pcode})")
            else:
                # Insert new law
                cur.execute(
                    """
                    INSERT INTO laws (
                        pcode, xml_law_nature, xml_law_name, xml_law_url,
                        xml_law_category, xml_latest_change_date,
                        xml_effective_date, xml_effective_content,
                        xml_abolition_mark, xml_is_english_translated,
                        xml_english_law_name, xml_attachment,
                        xml_history_content, xml_preamble
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        pcode, xml_law_nature, xml_law_name, xml_law_url,
                        xml_law_category, xml_latest_change_date,
                        xml_effective_date, xml_effective_content,
                        xml_abolition_mark, xml_is_english_translated,
                        xml_english_law_name, xml_attachment,
                        xml_history_content, xml_preamble
                    )
                )
                law_id = cur.fetchone()[0]
                print(f"Inserted new law: {xml_law_name} (PCode: {pcode})")
            
            # Process articles
            self._process_articles(cur, law_id, law_elem.find('法規內容'))
            
            conn.commit()

        except Exception as e:
            print(f"Error processing law {xml_law_name} (PCode: {pcode}): {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()

    def _process_articles(self, cur, law_id, law_content_elem):
        if law_content_elem is None:
            return

        # Delete existing articles for this law to ensure clean update
        cur.execute("DELETE FROM articles WHERE law_id = %s", (law_id,))

        for article_elem in law_content_elem.findall('條文'):
            xml_article_number = article_elem.find('條號').text
            xml_article_content = article_elem.find('條文內容').text
            xml_chapter_section = article_elem.find('編章節').text if article_elem.find('編章節') is not None else None

            cur.execute(
                """
                INSERT INTO articles (
                    law_id, xml_chapter_section, xml_article_number, xml_article_content
                ) VALUES (%s, %s, %s, %s)
                """,
                (law_id, xml_chapter_section, xml_article_number, xml_article_content)
            )
        print(f"Processed articles for law_id: {law_id}")

    def update_summary(self, summary_file_path):
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()

            with open(summary_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split content by "----- File: <filename> -----" and capture the filename
            # The regex now captures the law name (filename without .txt)
            parts = re.split(r'----- File: (.*?)\.txt -----\n', content)
            
            # The first element is usually empty if the file starts with a delimiter
            # Then it's (law_name, content, law_name, content, ...)
            for i in range(1, len(parts), 2):
                law_name = parts[i].strip()
                llm_summary = parts[i+1].strip()
                
                if not law_name or not llm_summary:
                    print(f"Warning: Could not parse law name or summary from part starting with: {parts[i][:50]}...")
                    continue

                print(f"Updating summary for law: {law_name}")
                cur.execute(
                    """
                    UPDATE laws SET llm_summary = %s WHERE xml_law_name = %s
                    """,
                    (llm_summary, law_name)
                )
                if cur.rowcount == 0:
                    print(f"Warning: Law '{law_name}' not found for summary update.")

            conn.commit()
        except Exception as e:
            print(f"Error updating summaries: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()

    def update_keywords(self, keyword_csv_path):
        import pandas as pd
        
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()

            df = pd.read_csv(keyword_csv_path)
            
            # Group by 'filename' and concatenate 'keywords' with '|'
            grouped_keywords = df.groupby('filename')['keywords'].apply(lambda x: '|'.join(x.astype(str))).reset_index()

            for index, row in grouped_keywords.iterrows():
                law_name = row['filename']
                llm_keywords = row['keywords']
                
                print(f"Updating keywords for law: {law_name}")
                cur.execute(
                    """
                    UPDATE laws SET llm_keywords = %s WHERE xml_law_name = %s
                    """,
                    (llm_keywords, law_name)
                )
                if cur.rowcount == 0:
                    print(f"Warning: Law '{law_name}' not found for keyword update.")
            conn.commit()
        except Exception as e:
            print(f"Error updating keywords: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_law_list(self, delete_law_list_path):
        with open(delete_law_list_path, 'r', encoding='utf-8') as f:
            law_names_to_delete = [line.strip() for line in f if line.strip()]
        
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()
            for law_name in law_names_to_delete:
                print(f"Deleting all data for law: {law_name}")
                cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (law_name,))
                law_id = cur.fetchone()
                
                if law_id:
                    law_id = law_id[0]
                    # ON DELETE CASCADE should handle articles, legal_concepts, law_hierarchy_relationships, law_relationships
                    cur.execute("DELETE FROM laws WHERE id = %s", (law_id,))
                    print(f"Successfully deleted law '{law_name}' and its related data.")
                else:
                    print(f"Warning: Law '{law_name}' not found for deletion.")
            conn.commit()
        except Exception as e:
            print(f"Error deleting laws: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()

    def export_law_list(self, export_law_list_path, output_dir):
        # This is a placeholder. Actual implementation would involve
        # reading from DB and formatting into Markdown.
        # For now, just simulate file creation.
        import os
        os.makedirs(output_dir, exist_ok=True)

        with open(export_law_list_path, 'r', encoding='utf-8') as f:
            law_names_to_export = [line.strip() for line in f if line.strip()]
        
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()
            for law_name in law_names_to_export:
                print(f"Exporting law: {law_name} to {output_dir}/{law_name}.md")
                
                cur.execute("SELECT xml_law_name, xml_preamble, llm_summary FROM laws WHERE xml_law_name = %s", (law_name,))
                law_data = cur.fetchone()
                
                if law_data:
                    exported_content = f"# {law_data[0]}\n\n"
                    if law_data[1]:
                        exported_content += f"## 前言\n{law_data[1]}\n\n"
                    
                    cur.execute("SELECT xml_chapter_section, xml_article_number, xml_article_content FROM articles WHERE law_id = (SELECT id FROM laws WHERE xml_law_name = %s) ORDER BY id", (law_name,))
                    articles = cur.fetchall()
                    
                    current_chapter_section = None
                    for chapter_section, article_number, article_content in articles:
                        if chapter_section and chapter_section != current_chapter_section:
                            exported_content += f"## {chapter_section}\n\n"
                            current_chapter_section = chapter_section
                        exported_content += f"### {article_number}\n{article_content}\n\n"
                    
                    output_file_path = os.path.join(output_dir, f"{law_name}.md")
                    with open(output_file_path, 'w', encoding='utf-8') as of:
                        of.write(exported_content)
                    print(f"Successfully exported '{law_name}' to '{output_file_path}'.")
                else:
                    print(f"Warning: Law '{law_name}' not found for export.")
            conn.commit()
        except Exception as e:
            print(f"Error exporting laws: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()

    def check_integrity(self):
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()

            print("--- 資料庫完整性檢查報告 ---")

            # 檢查 laws 表格
            cur.execute("SELECT COUNT(*) FROM laws")
            total_laws = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM laws WHERE pcode IS NULL OR xml_law_name IS NULL")
            null_laws_basic = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM laws WHERE law_metadata IS NULL OR law_metadata = '{}'::jsonb")
            null_laws_metadata = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM laws WHERE llm_summary IS NULL OR llm_summary = ''")
            null_laws_summary = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM laws WHERE llm_keywords IS NULL OR llm_keywords = ''")
            null_laws_keywords = cur.fetchone()[0]

            print(f"laws 表格總筆數: {total_laws}")
            print(f"  pcode 或 xml_law_name 為空筆數: {null_laws_basic}")
            print(f"  law_metadata 為空筆數: {null_laws_metadata}")
            print(f"  llm_summary 為空筆數: {null_laws_summary}")
            print(f"  llm_keywords 為空筆數: {null_laws_keywords}")
            print(f"  llm_summary 完整率: {((total_laws - null_laws_summary) / total_laws * 100):.2f}%" if total_laws > 0 else "0.00%")
            print(f"  llm_keywords 完整率: {((total_laws - null_laws_keywords) / total_laws * 100):.2f}%" if total_laws > 0 else "0.00%")
            print(f"  law_metadata 完整率: {((total_laws - null_laws_metadata) / total_laws * 100):.2f}%" if total_laws > 0 else "0.00%")

            # 檢查 articles 表格
            cur.execute("SELECT COUNT(*) FROM articles")
            total_articles = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM articles WHERE law_id IS NULL OR xml_article_number IS NULL")
            null_articles_basic = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM articles WHERE article_metadata IS NULL OR article_metadata = '{}'::jsonb")
            null_articles_metadata = cur.fetchone()[0]

            print(f"articles 表格總筆數: {total_articles}")
            print(f"  law_id 或 xml_article_number 為空筆數: {null_articles_basic}")
            print(f"  article_metadata 為空筆數: {null_articles_metadata}")
            print(f"  article_metadata 完整率: {((total_articles - null_articles_metadata) / total_articles * 100):.2f}%" if total_articles > 0 else "0.00%")

            # 檢查 legal_concepts 表格
            cur.execute("SELECT COUNT(*) FROM legal_concepts")
            total_legal_concepts = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM legal_concepts WHERE law_id IS NULL OR code IS NULL OR name IS NULL")
            null_legal_concepts_basic = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM legal_concepts WHERE data IS NULL OR data = '{}'::jsonb")
            null_legal_concepts_data = cur.fetchone()[0]

            print(f"legal_concepts 表格總筆數: {total_legal_concepts}")
            print(f"  law_id, code 或 name 為空筆數: {null_legal_concepts_basic}")
            print(f"  data 為空筆數: {null_legal_concepts_data}")
            print(f"  data 完整率: {((total_legal_concepts - null_legal_concepts_data) / total_legal_concepts * 100):.2f}%" if total_legal_concepts > 0 else "0.00%")

            # 檢查 law_hierarchy_relationships 表格
            cur.execute("SELECT COUNT(*) FROM law_hierarchy_relationships")
            total_lhr = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM law_hierarchy_relationships WHERE main_law_id IS NULL OR related_law_id IS NULL OR hierarchy_type IS NULL")
            null_lhr_basic = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM law_hierarchy_relationships WHERE data IS NULL OR data = '{}'::jsonb")
            null_lhr_data = cur.fetchone()[0]

            print(f"law_hierarchy_relationships 表格總筆數: {total_lhr}")
            print(f"  main_law_id, related_law_id 或 hierarchy_type 為空筆數: {null_lhr_basic}")
            print(f"  data 為空筆數: {null_lhr_data}")
            print(f"  data 完整率: {((total_lhr - null_lhr_data) / total_lhr * 100):.2f}%" if total_lhr > 0 else "0.00%")

            # 檢查 law_relationships 表格
            cur.execute("SELECT COUNT(*) FROM law_relationships")
            total_lr = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM law_relationships WHERE relationship_type IS NULL")
            null_lr_basic = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM law_relationships WHERE data IS NULL OR data = '{}'::jsonb")
            null_lr_data = cur.fetchone()[0]

            print(f"law_relationships 表格總筆數: {total_lr}")
            print(f"  relationship_type 為空筆數: {null_lr_basic}")
            print(f"  data 為空筆數: {null_lr_data}")
            print(f"  data 完整率: {((total_lr - null_lr_data) / total_lr * 100):.2f}%" if total_lr > 0 else "0.00%")

        except Exception as e:
            print(f"Error during integrity check: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()
