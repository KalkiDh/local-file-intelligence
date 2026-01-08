# utils/file_loader.py

import os
import glob
import pandas as pd
import pdfplumber

def read_file_content(file_path):
    """
    Helper to read a single file based on extension.
    Used by the Deep Summarizer to re-read large files.
    """
    filename = os.path.basename(file_path)
    content = ""
    
    try:
        if filename.endswith(('.txt', '.md', '.py', '.json', '.log')):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

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