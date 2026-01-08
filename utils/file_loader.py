# utils/file_loader.py

import os
import glob
import json
import pandas as pd
import pdfplumber

def _process_json(file_path):
    """
    Smart JSON Parser for NoSQL Data.
    Converts list-based JSON into line-delimited text (JSONL) for better RAG chunking.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Case A: List of Records (e.g., MongoDB dump, Logs)
        if isinstance(data, list):
            record_count = len(data)
            # Peek at first record keys if available
            keys = list(data[0].keys()) if record_count > 0 and isinstance(data[0], dict) else "Unknown"
            
            # Convert to JSON Lines (one record per line)
            # ensure_ascii=False keeps special characters readable
            jsonl_text = "\n".join([json.dumps(record, ensure_ascii=False) for record in data])
            
            return (
                f"Metadata:\n"
                f"- Type: NoSQL Collection (JSON)\n"
                f"- Total Records: {record_count}\n"
                f"- Schema Fields: {keys}\n\n"
                f"Records:\n"
                f"{jsonl_text}"
            )

        # Case B: Single Huge Object (e.g., Configuration, Nested Profile)
        elif isinstance(data, dict):
            # Pretty print with indentation so semantic chunkers usually split at logical brackets
            pretty_text = json.dumps(data, indent=2, ensure_ascii=False)
            keys = list(data.keys())
            return (
                f"Metadata:\n"
                f"- Type: NoSQL Document (Single Object)\n"
                f"- Root Keys: {keys}\n\n"
                f"Content:\n"
                f"{pretty_text}"
            )
            
        else:
            return str(data)

    except json.JSONDecodeError:
        return "Error: Invalid JSON format."
    except Exception as e:
        return f"Error parsing JSON: {e}"

def read_file_content(file_path):
    """
    Helper to read a single file based on extension.
    """
    filename = os.path.basename(file_path)
    content = ""
    
    try:
        if filename.endswith(('.txt', '.md', '.py', '.log')):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # UPDATED: Specialized JSON Handler
        elif filename.endswith(('.json', '.jsonl')):
            content = _process_json(file_path)

        elif filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            row_count = len(df)
            columns = ", ".join(df.columns.tolist())
            table_text = df.to_markdown(index=False)
            content = f"Metadata:\n- Type: CSV Data\n- Total Rows: {row_count}\n- Columns: {columns}\n\nData Table:\n{table_text}"

        elif filename.endswith('.pdf'):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        content += extracted + "\n"
        
        return content
    except Exception as e:
        return f"Error reading file: {e}"

def load_files_raw(directory_path):
    """
    Scans directory and uses read_file_content for each file.
    """
    files = glob.glob(os.path.join(directory_path, "*"))
    print(f"📂 Scanning {directory_path}...")
    
    loaded_files = []

    for file_path in files:
        filename = os.path.basename(file_path)
        content = read_file_content(file_path)
        if content and not content.startswith("Error"):
            loaded_files.append((filename, content))
        else:
            print(f"   ❌ Skipped {filename}")

    return loaded_files