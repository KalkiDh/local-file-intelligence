# utils/file_loader.py

import os
import glob
import pandas as pd
import pdfplumber

def load_files_from_directory(directory_path):
    combined_context = ""
    file_count = 0
    
    files = glob.glob(os.path.join(directory_path, "*"))
    print(f"📂 Scanning {directory_path}...")

    for file_path in files:
        filename = os.path.basename(file_path)
        content = ""
        
        try:
            # 1. Handle Text / Code / Logs
            if filename.endswith(('.txt', '.md', '.py', '.json', '.log')):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            # 2. Handle CSV (Improved Formatting)
            elif filename.endswith('.csv'):
                df = pd.read_csv(file_path)
                # Add columns summary
                columns = ", ".join(df.columns)
                # Convert to markdown with explicit headers
                csv_text = df.head(50).to_markdown(index=False)
                content = f"Columns: {columns}\nRow Count: {len(df)}\n\n{csv_text}"
                if len(df) > 50:
                    content += "\n... (Remaining rows truncated for brevity)"

            # 3. Handle PDF (Cleaner Extraction)
            elif filename.endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            # Clean up excessive newlines
                            cleaned_text = "\n".join([line.strip() for line in extracted.split('\n') if line.strip()])
                            content += cleaned_text + "\n"
            else:
                continue

            # Add clear delimiters for the LLM
            combined_context += f"\n{'='*20}\n📄 FILE: {filename}\n{'='*20}\n{content}\n"
            file_count += 1
            print(f"   ✅ Loaded: {filename}")

        except Exception as e:
            print(f"   ❌ Error loading {filename}: {e}")

    return combined_context, file_map_placeholder, file_count

# Placeholder since we removed the map logic for Pure RAG
file_map_placeholder = {}