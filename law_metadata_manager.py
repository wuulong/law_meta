import json
import os
import google.generativeai as genai
import re
import psycopg2

class LawMetadataManager:
    def __init__(self, db_config, gemini_api_key):
        self.db_config = db_config
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _get_db_connection(self):
        return psycopg2.connect(**self.db_config)

    def generate_meta_list(self, markdown_file_list_path):
        with open(markdown_file_list_path, 'r', encoding='utf-8') as f:
            markdown_entries = [line.strip().split(':', 1) for line in f if line.strip()]
        
        for law_name, markdown_path in markdown_entries:
            print(f"Generating metadata for law: {law_name} from {markdown_path}")
            self._generate_single_law_metadata(law_name, markdown_path)

    def _generate_single_law_metadata(self, law_name, markdown_path):
        # This is a simplified placeholder for LLM interaction.
        # In a real scenario, this would involve complex prompt engineering
        # and parsing of LLM responses.
        
        # Read the law content
        with open(markdown_path, 'r', encoding='utf-8') as f:
            law_content = f.read()

        # Read the metadata specification
        with open('/Volumes/D2024/github/law_meta/法律語法形式化.md', 'r', encoding='utf-8') as f:
            spec_content = f.read()

        prompt = f"""
        根據以下法律語法形式化規範，從提供的法規內容中提取並生成五種 JSON 格式的 Meta Data。
        請確保輸出嚴格遵守規範中定義的 JSON 結構和欄位。

        法律語法形式化規範：
        '''
        {spec_content}
        '''

        法規內容：
        '''
        {law_content}
        '''

        請為法規 "{law_name}" 生成以下五種 JSON Meta Data：
        1. 法規 Meta Data (Law Meta Data)
        2. 法條 Meta Data (Article Meta Data) - 為每條法條生成一個 JSON 物件，並將所有法條的 JSON 物件放入一個列表中。
        3. 法律概念 Meta Data (Legal Concept Meta Data) - 為每個法律概念生成一個 JSON 物件，並將所有法律概念的 JSON 物件放入一個列表中。
        4. 法規階層關係 Meta Data (Law Hierarchy Relationship Meta Data) - 為每個關係生成一個 JSON 物件，並將所有關係的 JSON 物件放入一個列表中。
        5. 法規關聯性 Meta Data (Law Relationship Meta Data) - 為每個關聯生成一個 JSON 物件，並將所有關聯的 JSON 物件放入一個列表中。

        請將每種 Meta Data 的 JSON 內容分別輸出，並用 '---END_OF_JSON---' 分隔。
        """

        try:
            response = self.model.generate_content(prompt)
            text_output = response.text

            # Split the response into individual JSON blocks
            json_blocks = re.split(r'---END_OF_JSON---', text_output)
            
            output_dir = 'json'
            os.makedirs(output_dir, exist_ok=True)

            # Define file names based on the specification
            file_names = {
                "法規 Meta Data": f"{law_name}_law_regulation.json",
                "法條 Meta Data": f"{law_name}_law_articles.json",
                "法律概念 Meta Data": f"{law_name}_legal_concepts.json",
                "法規階層關係 Meta Data": f"{law_name}_hierarchy_relations.json",
                "法規關聯性 Meta Data": f"{law_name}_law_relations.json",
            }

            # Attempt to parse and save each JSON block
            for i, block in enumerate(json_blocks):
                block = block.strip()
                if not block:
                    continue
                
                # Simple heuristic to identify which type of JSON it is
                # This part would need more robust logic in a real system
                if "法規名稱" in block and "法規版本" in block:
                    meta_type = "法規 Meta Data"
                elif "條號" in block and "條文內容" in block:
                    meta_type = "法條 Meta Data"
                elif "詞彙名稱" in block and "定義" in block:
                    meta_type = "法律概念 Meta Data"
                elif "階層關係類型" in block:
                    meta_type = "法規階層關係 Meta Data"
                elif "關聯類型" in block:
                    meta_type = "法規關聯性 Meta Data"
                else:
                    meta_type = f"unknown_{i}"

                output_file = os.path.join(output_dir, file_names.get(meta_type, f"temp_output_{meta_type}.json"))
                
                try:
                    # Clean the block to ensure it's valid JSON
                    # Remove any leading/trailing markdown code blocks if present
                    if block.startswith('```json'):
                        block = block[len('```json'):]
                    if block.endswith('```'):
                        block = block[:-len('```')]
                    
                    json_data = json.loads(block)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    print(f"Generated {meta_type} to {output_file}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for {meta_type} from block {i}: {e}")
                    print(f"Problematic block content: {block[:500]}...") # Print first 500 chars
                except Exception as e:
                    print(f"Error saving {meta_type} to file: {e}")

        except Exception as e:
            print(f"Error generating content for {law_name}: {e}")

    def load_meta_data_to_db(self, law_name):
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()

            # Get law_id
            cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (law_name,))
            law_id = cur.fetchone()
            if not law_id:
                print(f"Law '{law_name}' not found in database. Please import basic law data first.")
                return
            law_id = law_id[0]

            json_dir = 'json'
            
            # Load Law Meta Data
            law_regulation_path = os.path.join(json_dir, f"{law_name}_law_regulation.json")
            if os.path.exists(law_regulation_path):
                with open(law_regulation_path, 'r', encoding='utf-8') as f:
                    law_metadata = json.load(f)
                cur.execute("UPDATE laws SET law_metadata = %s WHERE id = %s", (json.dumps(law_metadata), law_id))
                print(f"Loaded Law Meta Data for {law_name}")

            # Load Article Meta Data
            law_articles_path = os.path.join(json_dir, f"{law_name}_law_articles.json")
            if os.path.exists(law_articles_path):
                with open(law_articles_path, 'r', encoding='utf-8') as f:
                    articles_metadata = json.load(f)
                for article_meta in articles_metadata:
                    article_number = article_meta.get('條號')
                    if article_number:
                        cur.execute("UPDATE articles SET article_metadata = %s WHERE law_id = %s AND xml_article_number = %s", 
                                    (json.dumps(article_meta), law_id, article_number))
                print(f"Loaded Article Meta Data for {law_name}")

            # Load Legal Concept Meta Data
            legal_concepts_path = os.path.join(json_dir, f"{law_name}_legal_concepts.json")
            if os.path.exists(legal_concepts_path):
                with open(legal_concepts_path, 'r', encoding='utf-8') as f:
                    legal_concepts_data = json.load(f)
                
                # Delete existing legal concepts for this law before inserting new ones
                cur.execute("DELETE FROM legal_concepts WHERE law_id = %s", (law_id,))
                for concept_meta in legal_concepts_data:
                    code = concept_meta.get('代號')
                    name = concept_meta.get('詞彙名稱')
                    if code and name:
                        cur.execute(
                            "INSERT INTO legal_concepts (law_id, code, name, data) VALUES (%s, %s, %s, %s)",
                            (law_id, code, name, json.dumps(concept_meta))
                        )
                print(f"Loaded Legal Concept Meta Data for {law_name}")

            # Load Law Hierarchy Relationship Meta Data
            hierarchy_relations_path = os.path.join(json_dir, f"{law_name}_hierarchy_relations.json")
            if os.path.exists(hierarchy_relations_path):
                with open(hierarchy_relations_path, 'r', encoding='utf-8') as f:
                    hierarchy_data = json.load(f)
                
                # Delete existing hierarchy relationships for this law before inserting new ones
                cur.execute("DELETE FROM law_hierarchy_relationships WHERE main_law_id = %s OR related_law_id = %s", (law_id, law_id))
                for hr_meta in hierarchy_data:
                    relationship_code = hr_meta.get('關係代號')
                    main_law_name = hr_meta.get('主法規')
                    related_law_name = hr_meta.get('關聯法規')
                    hierarchy_type = hr_meta.get('階層關係類型')

                    # Resolve main_law_id and related_law_id from names
                    cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (main_law_name,))
                    main_law_id_resolved = cur.fetchone()
                    cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (related_law_name,))
                    related_law_id_resolved = cur.fetchone()

                    if relationship_code and main_law_id_resolved and related_law_id_resolved:
                        cur.execute(
                            "INSERT INTO law_hierarchy_relationships (relationship_code, main_law_id, main_law_name, related_law_id, related_law_name, hierarchy_type, data) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (relationship_code, main_law_id_resolved[0], main_law_name, related_law_id_resolved[0], related_law_name, hierarchy_type, json.dumps(hr_meta))
                        )
                print(f"Loaded Law Hierarchy Relationship Meta Data for {law_name}")

            # Load Law Relationship Meta Data
            law_relations_path = os.path.join(json_dir, f"{law_name}_law_relations.json")
            if os.path.exists(law_relations_path):
                with open(law_relations_path, 'r', encoding='utf-8') as f:
                    relations_data = json.load(f)
                
                # Delete existing law relationships for this law before inserting new ones
                cur.execute("DELETE FROM law_relationships WHERE main_law_id = %s OR related_law_id = %s", (law_id, law_id))
                for lr_meta in relations_data:
                    code = lr_meta.get('代號')
                    relationship_type = lr_meta.get('關聯類型')
                    main_law_name = lr_meta.get('主法規')
                    main_law_article_number = lr_meta.get('主法規條號')
                    related_law_name = lr_meta.get('關聯法規')
                    related_law_article_number = lr_meta.get('關聯法規條號')

                    main_law_id_resolved = None
                    if main_law_name:
                        cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (main_law_name,))
                        main_law_id_resolved = cur.fetchone()
                        if main_law_id_resolved: main_law_id_resolved = main_law_id_resolved[0]

                    related_law_id_resolved = None
                    if related_law_name:
                        cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (related_law_name,))
                        related_law_id_resolved = cur.fetchone()
                        if related_law_id_resolved: related_law_id_resolved = related_law_id_resolved[0]

                    main_article_id_resolved = None
                    if main_law_id_resolved and main_law_article_number:
                        cur.execute("SELECT id FROM articles WHERE law_id = %s AND xml_article_number = %s", (main_law_id_resolved, main_law_article_number))
                        main_article_id_resolved = cur.fetchone()
                        if main_article_id_resolved: main_article_id_resolved = main_article_id_resolved[0]

                    related_article_id_resolved = None
                    if related_law_id_resolved and related_law_article_number:
                        cur.execute("SELECT id FROM articles WHERE law_id = %s AND xml_article_number = %s", (related_law_id_resolved, related_law_article_number))
                        related_article_id_resolved = cur.fetchone()
                        if related_article_id_resolved: related_article_id_resolved = related_article_id_resolved[0]

                    if code and relationship_type:
                        cur.execute(
                            "INSERT INTO law_relationships (code, relationship_type, main_law_id, main_law_name, main_article_id, related_law_id, related_law_name, related_article_id, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (code, relationship_type, main_law_id_resolved, main_law_name, main_article_id_resolved, related_law_id_resolved, related_law_name, related_article_id_resolved, json.dumps(lr_meta))
                        )
                print(f"Loaded Law Relationship Meta Data for {law_name}")

            conn.commit()
        except Exception as e:
            print(f"Error loading metadata for {law_name}: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()
