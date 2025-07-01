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
    def __init__(self, db_config, gemini_api_key):
        self.db_config = db_config
        self.client = genai.Client(api_key=gemini_api_key) # Initialize client once
        
        # Upload static spec file once
        # Assuming 法律語法形式化.md is in the root directory of the project
        self.spec_file = self.client.files.upload(file="法律語法形式化.md", config={'mime_type':"text/markdown"})
        print(f"Uploaded static spec file: {self.spec_file.uri}")


    def _get_db_connection(self):
        return psycopg2.connect(**self.db_config)

    def generate_meta_list(self, markdown_file_list_path):
        with open(markdown_file_list_path, 'r', encoding='utf-8') as f:
            law_names = [line.strip() for line in f if line.strip()]
        
        for law_name in law_names:
            markdown_path = os.path.join('data', f'{law_name}.md')
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
                                      generate_law_articles=True): # Changed default to False
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
            
            # Check if the file already exists for non-article metadata
            if meta_type_key != 'law_articles' and os.path.exists(output_file):
                print(f"Skipping generation for {meta_type_key}: {output_file} already exists.")
                continue

            b_need = True
            run_cnt = 0
            while b_need and run_cnt < 3: # Retry up to 3 times
                try:
                    run_cnt += 1
                    # Pass law_content directly to _call_gemini_api
                    text_output = self._call_gemini_api(law_name, law_content, config['prompt'])

                    # Save raw text output to a temporary file
                    raw_output_file = os.path.join(tmp_output_dir, f"{law_name}_{meta_type_key}.txt")
                    with open(raw_output_file, 'w', encoding='utf-8') as f:
                        f.write(text_output)
                    print(f"Saved raw output to {raw_output_file}")

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
                    with open(tmp_output_file, 'w', encoding='utf-8') as f: # Write to temporary file
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
                    shutil.move(tmp_output_file, output_file) # Move to final destination
                    print(f"Generated {meta_type_key} to {output_file}")
                    b_need = False # Success, exit loop
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON for {meta_type_key}: {e}")
                    print(f"Problematic block content: {text_output[:500]}...")
                    time.sleep(5) # Wait before retrying
                except Exception as e:
                    print(f"Error generating content for {meta_type_key}: {e}")
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
