import shutil
import json
from google import genai
from google.genai import types
from google.generativeai import types
import os
import re
import time
import psycopg2

class LawMetadataManager:
    def __init__(self, db_config, gemini_api_key, init_gemini=True, force_update=False):
        self.db_config = db_config
        self.client = None
        self.spec_file = None
        self.force_update = force_update # Store the force_update flag
        if init_gemini:
            self.client = genai.Client(api_key=gemini_api_key) # Initialize client once
            
            # Upload static spec file once
            # Assuming 法律語法形式化.md is in the root directory of the project
            self.spec_file = self.client.files.upload(file="法律語法形式化.md", config={'mime_type':"text/markdown"})
            print(f"Uploaded static spec file: {self.spec_file.uri}")


    def _get_db_connection(self):
        return psycopg2.connect(**self.db_config)

    def _format_article_number(self, article_number_str):
        """
        Converts various article number formats (e.g., "第一條", "第1條", "第 1 條")
        to a standard "第 X 條" format (with Arabic numerals and a space).
        """
        num_map = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                   '十': 10, '百': 100, '千': 1000}
        
        def chinese_to_arabic(num_str):
            if num_str.isdigit():
                return int(num_str)
            
            result = 0
            tmp = 0
            for char in num_str:
                if char in num_map:
                    val = num_map[char]
                    if val >= 10: # '十', '百', '千'
                        if tmp == 0: # Handles cases like '十', '百', '千' directly
                            tmp = 1
                        result += tmp * val
                        tmp = 0
                    else: # Single digit
                        tmp = tmp * 10 + val
                else: # Handle cases like '二十', '三十'
                    if char == '十':
                        if tmp == 0:
                            tmp = 1
                        result += tmp * 10
                        tmp = 0
            result += tmp # Add any remaining single digit
            return result

        # Remove spaces and then try to parse
        article_number_str = article_number_str.replace(' ', '')

        match = re.match(r'第(\S+)條', article_number_str)
        if match:
            num_part = match.group(1)
            try:
                # Try converting Chinese numerals first
                arabic_num = chinese_to_arabic(num_part)
            except ValueError: # Catch ValueError if int() conversion fails
                # Fallback to direct integer conversion if Chinese conversion fails
                arabic_num = int(num_part)
            return f"第 {arabic_num} 條"
        return article_number_str # Return original if no match

    def load_meta_data_list_to_db(self, law_list_file_path):
        with open(law_list_file_path, 'r', encoding='utf-8') as f:
            law_names = [line.strip() for line in f if line.strip()]
        
        for law_name in law_names:
            print(f"Loading metadata for law: {law_name}")
            self._load_single_law_metadata_to_db(law_name)

    def _load_single_law_metadata_to_db(self, law_name):
        conn = None
        try:
            conn = self._get_db_connection()
            cur = conn.cursor()

            json_dir = 'json'
            file_names = {
                "law_regulation": f"{law_name}_law_regulation.json",
                "law_articles": f"{law_name}_law_articles.json",
                "legal_concepts": f"{law_name}_legal_concepts.json",
                "hierarchy_relations": f"{law_name}_hierarchy_relations.json",
                "law_relations": f"{law_name}_law_relations.json",
            }

            # Get law_id first, as it's needed for articles and relationships
            law_id = None
            cur.execute("SELECT id, law_metadata FROM laws WHERE xml_law_name = %s", (law_name,))
            law_result = cur.fetchone()
            if law_result:
                law_id = law_result[0]
                existing_law_metadata = law_result[1]
            else:
                print(f"Error: Law '{law_name}' not found in DB. Cannot load metadata.")
                return

            # Check if law_metadata already exists and force_update is False
            if not self.force_update and existing_law_metadata is not None:
                print(f"Skipping loading metadata for {law_name}: law_metadata already exists. Use --force-meta-update to override.")
                return

            # 1. Load Law Meta Data (law_regulation.json)
            law_regulation_path = os.path.join(json_dir, file_names["law_regulation"])
            if os.path.exists(law_regulation_path):
                with open(law_regulation_path, 'r', encoding='utf-8') as f:
                    law_metadata = json.load(f)
                cur.execute("UPDATE laws SET law_metadata = %s WHERE id = %s", (json.dumps(law_metadata), law_id))
                print(f"Loaded law_metadata for {law_name}")
            else:
                print(f"Warning: {law_regulation_path} not found. Skipping law_metadata.")

            # 2. Load Article Meta Data (law_articles.json)
            law_articles_path = os.path.join(json_dir, file_names["law_articles"])
            if os.path.exists(law_articles_path):
                with open(law_articles_path, 'r', encoding='utf-8') as f:
                    articles_metadata = json.load(f)
                
                for article_meta in articles_metadata:
                    article_number = article_meta.get('條號')
                    if article_number:
                        # Convert to standard "第 X 條" format
                        formatted_article_number = self._format_article_number(article_number)
                        
                        cur.execute("UPDATE articles SET article_metadata = %s WHERE law_id = %s AND xml_article_number = %s", (json.dumps(article_meta), law_id, formatted_article_number))
                        if cur.rowcount == 0:
                            print(f"Warning: Article '{article_number}' (formatted: '{formatted_article_number}') for law '{law_name}' not found in DB for article_metadata update.")
                    else:
                        print(f"Warning: Article metadata missing '條號' for law '{law_name}'.")
                print(f"Loaded article_metadata for {law_name}")
            else:
                print(f"Warning: {law_articles_path} not found. Skipping article_metadata.")

            # 3. Load Legal Concept Meta Data (legal_concepts.json)
            legal_concepts_path = os.path.join(json_dir, file_names["legal_concepts"])
            if os.path.exists(legal_concepts_path):
                with open(legal_concepts_path, 'r', encoding='utf-8') as f:
                    legal_concepts_data = json.load(f)
                
                # Delete existing legal concepts for this law to avoid duplicate key errors
                cur.execute("DELETE FROM legal_concepts WHERE law_id = %s", (law_id,))
                
                for concept in legal_concepts_data:
                    code = concept.get('代號')
                    name = concept.get('詞彙名稱')
                    if code and name:
                        cur.execute("INSERT INTO legal_concepts (law_id, code, name, data) VALUES (%s, %s, %s, %s) ON CONFLICT (law_id, code) DO NOTHING;",
                                    (law_id, code, name, json.dumps(concept)))
                    else:
                        print(f"Warning: Legal concept missing '代號' or '詞彙名稱' for law '{law_name}'.")
                conn.commit() # Commit legal concepts separately
                print(f"Loaded legal_concepts for {law_name}")
            else:
                print(f"Warning: {legal_concepts_path} not found. Skipping legal_concepts.")

            # 4. Load Law Hierarchy Relationship Meta Data (hierarchy_relations.json)
            hierarchy_relations_path = os.path.join(json_dir, file_names["hierarchy_relations"])
            if os.path.exists(hierarchy_relations_path):
                with open(hierarchy_relations_path, 'r', encoding='utf-8') as f:
                    hierarchy_data = json.load(f)
                
                cur.execute("DELETE FROM law_hierarchy_relationships WHERE main_law_id = %s OR related_law_id = %s", (law_id, law_id))
                for rel in hierarchy_data:
                    rel_code = rel.get('關係代號')
                    main_law_name = rel.get('主法規')
                    related_law_name = rel.get('關聯法規')
                    hierarchy_type = rel.get('階層關係類型')

                    if rel_code and main_law_name and related_law_name and hierarchy_type:
                        main_law_id_rel = None
                        cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (main_law_name,))
                        main_law_id_result = cur.fetchone()
                        if main_law_id_result: main_law_id_rel = main_law_id_result[0]

                        related_law_id_rel = None
                        cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (related_law_name,))
                        related_law_id_result = cur.fetchone()
                        if related_law_id_result: related_law_id_rel = related_law_id_result[0]

                        if main_law_id_rel and related_law_id_rel:
                            cur.execute("INSERT INTO law_hierarchy_relationships (relationship_code, main_law_id, main_law_name, related_law_id, related_law_name, hierarchy_type, data) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                        (rel_code, main_law_id_rel, main_law_name, related_law_id_rel, related_law_name, hierarchy_type, json.dumps(rel)))
                        else:
                            print(f"Warning: Could not resolve main_law_id or related_law_id for hierarchy relationship '{rel_code}'.")
                    else:
                        print(f"Warning: Hierarchy relationship missing required fields for law '{law_name}'.")
                print(f"Loaded law_hierarchy_relationships for {law_name}")
            else:
                print(f"Warning: {hierarchy_relations_path} not found. Skipping law_hierarchy_relationships.")

            # 5. Load Law Relationship Meta Data (law_relations.json)
            law_relations_path = os.path.join(json_dir, file_names["law_relations"])
            if os.path.exists(law_relations_path):
                with open(law_relations_path, 'r', encoding='utf-8') as f:
                    law_relations_data = json.load(f)
                
                cur.execute("DELETE FROM law_relationships WHERE main_law_id = %s OR related_law_id = %s", (law_id, law_id))
                for rel in law_relations_data:
                    rel_code = rel.get('代號')
                    rel_type = rel.get('關聯類型')
                    main_law_name = rel.get('主法規')
                    main_article_number = rel.get('主法規條號')
                    related_law_name = rel.get('關聯法規')
                    related_article_number = rel.get('關聯法規條號')

                    if rel_code and rel_type:
                        main_law_id_rel = None
                        if main_law_name:
                            cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (main_law_name,))
                            main_law_id_result = cur.fetchone()
                            if main_law_id_result: main_law_id_rel = main_law_id_result[0]
                        
                        main_article_id_rel = None
                        if main_law_id_rel and main_article_number:
                            cur.execute("SELECT id FROM articles WHERE law_id = %s AND xml_article_number = %s", (main_law_id_rel, main_article_number))
                            main_article_id_result = cur.fetchone()
                            if main_article_id_result: main_article_id_rel = main_article_id_result[0]

                        related_law_id_rel = None
                        if related_law_name:
                            cur.execute("SELECT id FROM laws WHERE xml_law_name = %s", (related_law_name,))
                            related_law_id_result = cur.fetchone()
                            if related_law_id_result: related_law_id_rel = related_law_id_result[0]

                        related_article_id_rel = None
                        if related_law_id_rel and related_article_number:
                            cur.execute("SELECT id FROM articles WHERE law_id = %s AND xml_article_number = %s", (related_law_id_rel, related_article_number))
                            related_article_id_result = cur.fetchone()
                            if related_article_id_result: related_article_id_rel = related_article_id_result[0]

                        cur.execute("INSERT INTO law_relationships (code, relationship_type, main_law_id, main_law_name, main_article_id, related_law_id, related_law_name, related_article_id, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                    (rel_code, rel_type, main_law_id_rel, main_law_name, main_article_id_rel, related_law_id_rel, related_law_name, related_article_id_rel, json.dumps(rel)))
                    else:
                        print(f"Warning: Law relationship missing '代號' or '關聯類型' for law '{law_name}'.")
                print(f"Loaded law_relationships for {law_name}")
            else:
                print(f"Warning: {law_relations_path} not found. Skipping law_relationships.")

            conn.commit()
        except Exception as e:
            print(f"Error loading metadata for {law_name}: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                cur.close()
                conn.close()

    def generate_meta_list(self, markdown_file_list_path, output_dir): # Added output_dir parameter
        with open(markdown_file_list_path, 'r', encoding='utf-8') as f:
            law_names = [line.strip() for line in f if line.strip()]
        
        for law_name in law_names:
            markdown_path = os.path.join(output_dir, f'{law_name}.md') # Use output_dir here
            print(f"Generating metadata for law: {law_name} from {markdown_path}")
            # Call the refactored method with default flags
            self._generate_single_law_metadata(law_name, markdown_path)

    def _call_gemini_api(self, law_name, law_content, user_prompt):
        """
        Helper method to call Gemini API, handle file uploads, and retries.
        """
        model_name = "gemini-2.0-flash-thinking-exp-01-21" # Use gemini-1.5-flash as it is a commonly available model
        
        # Upload law content dynamically for each call
        # Create a temporary file to hold the law_content for upload
        temp_law_file_path = f"tmp_{law_name}_content.md"
        with open(temp_law_file_path, 'w', encoding='utf-8') as f:
            f.write(law_content)

        law_content_file = self.client.files.upload(file=temp_law_file_path, config={'mime_type':"text/markdown"})
        print(f"Uploaded law content file: {law_content_file.uri}")

        contents = [
            genai.types.Content(
                role="user",
                parts=[
                    genai.types.Part.from_uri(
                        file_uri=law_content_file.uri,
                        mime_type=law_content_file.mime_type,
                    ),
                    genai.types.Part.from_uri(
                        file_uri=self.spec_file.uri,
                        mime_type=self.spec_file.mime_type,
                    ),
                    genai.types.Part.from_text(text=user_prompt),
                ],
            )
        ]
        generate_content_config = genai.types.GenerateContentConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=64,
            max_output_tokens=65536,
            response_mime_type="text/plain",
            system_instruction=[
                genai.types.Part.from_text(text="""請以台灣人的立場，用繁體中文回答"""),
            ],
        )
        
        print(f"Q::{user_prompt}")

        response_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        ):
            response_text += chunk.text
        print(f"A::{response_text}")

        # Delete the dynamically uploaded law content file and local temporary file
        self.client.files.delete(name=law_content_file.name)
        os.remove(temp_law_file_path)
        print(f"Deleted temporary law content file: {law_content_file.name} and local file {temp_law_file_path}")

        return response_text

    def _generate_single_law_metadata(self, law_name, markdown_path,
                                      generate_law_regulation=True,
                                      generate_legal_concepts=True,
                                      generate_hierarchy_relations=True,
                                      generate_law_relations=True,
                                      generate_law_articles=False): # Changed default to False
        law_content = ""
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                law_content = f.read()
        except FileNotFoundError:
            alternative_markdown_path = os.path.join('output_dir', f'{law_name}.md')
            print(f"File not found in {markdown_path}, trying {alternative_markdown_path}")
            try:
                with open(alternative_markdown_path, 'r', encoding='utf-8') as f:
                    law_content = f.read()
            except FileNotFoundError:
                print(f"Error: Markdown file not found at {markdown_path} or {alternative_markdown_path}")
                return

        output_dir = 'json'
        tmp_output_dir = 'tmp/meta_data_temp' # New temporary directory for meta data
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(tmp_output_dir, exist_ok=True)

        # Define file names based on the specification
        file_names = {
            "law_regulation": f"{law_name}_law_regulation.json",
            "law_articles": f"{law_name}_law_articles.json",
            "legal_concepts": f"{law_name}_legal_concepts.json",
            "hierarchy_relations": f"{law_name}_hierarchy_relations.json",
            "law_relations": f"{law_name}_law_relations.json",
        }

        # Prompts for each metadata type
        prompt_configs = {
            'law_regulation': {
                'flag': generate_law_regulation,
                'prompt': f"根據提供的法規內容和法律語法形式化規範，產生法規 Meta Data (Law Meta Data)，盡可能詳列資訊，不要省略。請將 JSON 內容輸出，並用 '```json' 和 '```' 包裹。",
                'output_key': 'law_regulation'
            },
            'legal_concepts': {
                'flag': generate_legal_concepts,
                'prompt': f"根據提供的法規內容和法律語法形式化規範，產生法律概念 Meta Data (Legal Concept Meta Data)，注意並非 法規 Meta Data，請列出全部概念，不要省略。請將 JSON 內容輸出，並用 '```json' 和 '```' 包裹。",
                'output_key': 'legal_concepts'
            },
            'hierarchy_relations': {
                'flag': generate_hierarchy_relations,
                'prompt': f"根據提供的法規內容和法律語法形式化規範，產生法規階層關係 Meta Data，不包含法條間關聯性，請列出全部法規間階層關係，尤其包含上位關係，不要省略。請將 JSON 內容輸出，並用 '```json' 和 '```' 包裹。",
                'output_key': 'hierarchy_relations'
            },
            'law_relations': {
                'flag': generate_law_relations,
                'prompt': f"根據提供的法規內容和法律語法形式化規範，產生法規關聯性 Meta Data，不包含本法規內部法條之間的關聯性，請列出法規間全部關聯性，不要省略。請將 JSON 內容輸出，並用 '```json' 和 '```' 包裹。",
                'output_key': 'law_relations'
            },
            'law_articles': { # Set flag to False here
                'flag': False,
                'prompt': f"根據提供的法規內容和法律語法形式化規範，產生所有法條的 Meta Data (Article Meta Data)。為每條法條生成一個 JSON 物件，並將所有法條的 JSON 物件放入一個列表中。請列出所有法條，不要省略。請將 JSON 內容輸出，並用 '```json' 和 '```' 包裹。",
                'output_key': 'law_articles'
            },
        }

        for meta_type_key, config in prompt_configs.items():
            if not config['flag']:
                print(f"Skipping generation for {meta_type_key}.")
                continue

            tmp_output_file = os.path.join(tmp_output_dir, file_names[config['output_key']])
            output_file = os.path.join(output_dir, file_names[config['output_key']])
            raw_output_file = os.path.join(tmp_output_dir, f"{law_name}_{meta_type_key}.txt") # Define raw_output_file here

            # Check if the final JSON file already exists
            if not self.force_update and meta_type_key != 'law_articles' and os.path.exists(output_file):
                print(f"Skipping generation for {meta_type_key}: {output_file} already exists. Use --force-meta-update to override.")
                continue

            b_need = True # Assume we need to generate, unless processed from existing raw file

            # --- Attempt to process from existing raw text file first ---
            if os.path.exists(raw_output_file):
                print(f"Attempting to process {meta_type_key} from existing raw file: {raw_output_file}")
                try:
                    with open(raw_output_file, 'r', encoding='utf-8') as f:
                        existing_raw_text = f.read()
                    if self._process_raw_text_to_json(existing_raw_text, tmp_output_file, output_file, meta_type_key):
                        b_need = False # Successfully processed from existing raw file, no need for GenAI
                except Exception as e:
                    print(f"Error reading or processing existing raw file {raw_output_file}: {e}")
                    # b_need remains True, will proceed to GenAI call

            # --- If still needed, call GenAI and process its output ---
            run_cnt = 0
            while b_need and run_cnt < 3: # Retry up to 3 times
                text_output = "" # Initialize text_output here
                try:
                    run_cnt += 1
                    text_output = self._call_gemini_api(law_name, law_content, config['prompt'])

                    # Save raw text output to a temporary file (overwrite if exists)
                    with open(raw_output_file, 'w', encoding='utf-8') as f:
                        f.write(text_output)
                    print(f"Saved raw output to {raw_output_file}")

                    if self._process_raw_text_to_json(text_output, tmp_output_file, output_file, meta_type_key):
                        b_need = False # Success, exit loop
                    else:
                        # If _process_raw_text_to_json failed, b_need remains True, will retry
                        time.sleep(5) # Wait before retrying
                except Exception as e: # Catch any other errors during GenAI call or initial processing
                    print(f"Error during GenAI call or initial processing for {meta_type_key}: {e}")
                    time.sleep(5) # Wait before retrying

            if b_need: # If still not successful after retries
                print(f"Failed to generate {meta_type_key} after {run_cnt} attempts. Skipping.")

        # --- Generate Law Articles Meta Data (Batch Processing) ---
        if generate_law_articles:
            print(f"Generating law articles metadata for {law_name} (batch processing)...")
            all_articles_metadata = []
            step = 5 # Process 5 articles at a time

            # Get max article number from DB
            conn = None
            max_article_number = 0
            try:
                conn = self._get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT MAX(CAST(SUBSTRING(xml_article_number FROM '\\d+') AS INTEGER)) FROM articles WHERE law_id = (SELECT id FROM laws WHERE xml_law_name = %s)", (law_name,))
                result = cur.fetchone()
                if result and result[0]:
                    max_article_number = result[0]
                else:
                    print(f"Warning: Could not determine max article number for {law_name} from DB. Skipping article generation.")
                    return
            except Exception as e:
                print(f"Error getting max article number for {law_name}: {e}")
                if conn: conn.rollback()
                return
            finally:
                if conn:
                    cur.close()
                    conn.close()

            print(f"Max article number for {law_name}: {max_article_number}")
            max_article_number=9; # For testing, set to 9

            # Create a temporary directory for article metadata
            temp_articles_dir = os.path.join('tmp', 'articles', law_name)
            os.makedirs(temp_articles_dir, exist_ok=True)

            for i in range(1, max_article_number + 1, step):
                start_article = i
                end_article = min(i + step - 1, max_article_number)
                
                temp_article_file = os.path.join(temp_articles_dir, f"{law_name}_article_{start_article}-{end_article}.json")

                if os.path.exists(temp_article_file):
                    print(f"Loading articles {start_article}-{end_article} from {temp_article_file}")
                    with open(temp_article_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    all_articles_metadata.extend(json_data)
                    continue # Skip generation if file exists
                
                user_prompt = f"根據提供的法規內容和法律語法形式化規範，產生第{start_article}條到第{end_article}條的法條 Meta Data (Article Meta Data)。為每條法條生成一個 JSON 物件，並將所有法條的 JSON 物件放入一個列表中。請列出所有法條，不要省略。請將 JSON 內容輸出，並用 '```json' 和 '```' 包裹。"
                
                b_need = True
                run_cnt = 0
                while b_need and run_cnt < 3: # Retry up to 3 times
                    try:
                        run_cnt += 1
                        text_output = self._call_gemini_api(law_name, law_content, user_prompt)

                        # Extract JSON block using regex
                        json_match = re.search(r'```json\n(.*?)```', text_output, re.DOTALL)
                        if json_match:
                            json_string = json_match.group(1)
                        else:
                            # If no ```json block is found, assume the whole output is the JSON string
                            # and try to clean it up (e.g., if the model forgot the ```json markers)
                            json_string = text_output.strip()

                        # 移除單行註解
                        json_string = re.sub(r'//.*', '', json_string)
                        # 移除多行註解
                        json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.DOTALL)

                        json_data = json.loads(json_string)
                        all_articles_metadata.extend(json_data)
                        
                        # Save to temporary file
                        with open(temp_article_file, 'w', encoding='utf-8') as f:
                            json.dump(json_data, f, ensure_ascii=False, indent=2)
                        print(f"Generated and saved articles {start_article}-{end_article} to {temp_article_file}")
                        b_need = False # Success, exit loop
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON for articles {start_article}-{end_article}: {e}")
                        print(f"Problematic block content: {text_output[:500]}...")
                        time.sleep(5)
                    except Exception as e:
                        print(f"Error generating content for articles {start_article}-{end_article}: {e}")
                        time.sleep(5)
                
                if b_need:
                    print(f"Failed to generate articles {start_article}-{end_article} after {run_cnt} attempts. Skipping remaining articles.")
                    break # Stop processing further articles if a batch fails repeatedly

            # Save all collected articles metadata to the final file
            articles_output_file = os.path.join(output_dir, file_names['law_articles'])
            with open(articles_output_file, 'w', encoding='utf-8') as f:
                json.dump(all_articles_metadata, f, ensure_ascii=False, indent=2)
            print(f"Generated all law articles to {articles_output_file}")


    def _process_raw_text_to_json(self, raw_text, tmp_output_file, output_file, meta_type_key):
        """
        Helper to extract, clean, parse JSON from raw text, and save it.
        Returns True on success, False on failure.
        """
        try:
            json_match = re.search(r'```json\n(.*?)```', raw_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1).strip()
            else:
                # If no ```json block is found, try to parse the whole text as JSON
                json_string = raw_text.strip()
                print(f"Warning: No JSON block found in raw text for {meta_type_key}. Attempting to parse entire text as JSON.")

            json_string = re.sub(r'//.*\n', '', json_string)
            json_string = re.sub(r'/\*.*?\*/', '', json_string, flags=re.DOTALL)

            if not json_string:
                raise json.JSONDecodeError("Empty JSON string after extraction and cleaning.", raw_text, 0)

            json_data = json.loads(json_string)
            with open(tmp_output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            shutil.move(tmp_output_file, output_file)
            print(f"Successfully processed and saved {meta_type_key} from raw text to {output_file}")
            return True
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from raw text for {meta_type_key}: {e}")
            print(f"Problematic raw text content: {raw_text[:500]}...")
            return False
        except Exception as e:
            print(f"Error processing raw text for {meta_type_key}: {e}")
            return False


    def generate_llm_summary(self, law_name, md_content, summary_example_content=""):
        """
        Generates a summary for a given law using LLM based on its Markdown content.
        Optionally includes example summary content in the prompt.
        """
        if not self.client:
            print("Error: Gemini API client not initialized. Cannot generate summary.")
            return ""

        prompt_parts = [
            f"請根據以下法規的 Markdown 內容，生成一份簡要摘要（300字以內）。請將摘要內容輸出，並用 '```markdown' 和 '```' 包裹。"
        ]

        if summary_example_content:
            prompt_parts.append(f"\n\n以下是一個摘要範例，請參考其風格和內容結構：\n{summary_example_content}")

        prompt_parts.append(f"\n\n法規內容：\n{md_content}")

        user_prompt = "".join(prompt_parts)

        print(f"Generating LLM summary for {law_name}...")
        try:
            # Use the existing _call_gemini_api to interact with the LLM
            summary_text = self._call_gemini_api(law_name, md_content, user_prompt)
            
            # Extract content from markdown code block
            markdown_match = re.search(r'```markdown\n(.*?)```', summary_text, re.DOTALL)
            if markdown_match:
                return markdown_match.group(1).strip()
            else:
                print(f"Warning: No markdown code block found in summary for {law_name}. Returning raw text.")
                return summary_text.strip()
        except Exception as e:
            print(f"Error generating summary for {law_name}: {e}")
            return ""

    def generate_llm_keywords(self, law_name, md_content, keywords_example_content=""):
        """
        Generates keywords for a given law using LLM based on its Markdown content.
        Explicitly asks for keywords in a CSV code block and parses the response.
        """
        if not self.client:
            print("Error: Gemini API client not initialized. Cannot generate keywords.")
            return ""

        prompt_parts = [
            f"請根據以下法規的 Markdown 內容，生成該法規的關鍵字。請將每個關鍵字放在單獨一行，並用 '```csv' 和 '```' 包裹。CSV 檔案應只包含一列：'關鍵字'。"
        ]

        if keywords_example_content:
            prompt_parts.append(f"\n\n以下是一個關鍵字範例，請參考其風格和內容結構：\n{keywords_example_content}")

        prompt_parts.append(f"\n\n法規內容：\n{md_content}")

        user_prompt = "".join(prompt_parts)

        print(f"Generating LLM keywords for {law_name}...")
        try:
            keywords_text = self._call_gemini_api(law_name, md_content, user_prompt)
            
            # Extract content from CSV code block
            csv_match = re.search(r'''```csv
(.*?)```''', keywords_text, re.DOTALL)
            if csv_match:
                # Remove the first line (header) from the CSV content
                csv_content = csv_match.group(1).strip()
                lines = csv_content.split('\n')
                if lines and lines[0].strip() == '關鍵字':
                    return '\n'.join(lines[1:]).strip()
                return csv_content
            else:
                print(f"Warning: No CSV code block found in keywords for {law_name}. Returning raw text.")
                return keywords_text.strip()
        except Exception as e:
            print(f"Error generating keywords for {law_name}: {e}")
            return ""
