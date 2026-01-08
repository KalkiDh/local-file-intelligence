# core/hybrid_manager.py

from utils.chunker import intelligent_chunking
from utils.vector_store import VectorEngine

SIZE_THRESHOLD = 4000 

class HybridContextManager:
    def __init__(self):
        self.vector_engine = VectorEngine(reset_db=True)
        # CHANGED: Store small files individually instead of one big string
        self.small_files = {}   # {filename: full_content}
        self.large_files = []   # List of filenames in Vector DB

    def process_and_index(self, filename, content):
        if len(content) < SIZE_THRESHOLD:
            # Store in RAM dictionary
            self.small_files[filename] = content
            return "RAM (Small)"
        else:
            # Index in Vector DB
            chunks = intelligent_chunking(content)
            self.vector_engine.add_document(filename, chunks)
            self.large_files.append(filename)
            return f"VECTOR ({len(chunks)} chunks)"

    def list_files(self):
        """Returns a list of all loaded files and their status."""
        files = []
        for f in self.small_files:
            files.append(f"{f} (RAM)")
        for f in self.large_files:
            files.append(f"{f} (Vector DB)")
        return files

    def build_smart_context(self, user_query, focus_file=None):
        """
        Constructs context. 
        If focus_file is set, ONLY uses that file.
        If focus_file is None, uses ALL small files + Vector Search on large files.
        """
        combined_context = ""
        
        # --- MODE A: FOCUSED ON ONE FILE ---
        if focus_file:
            # Case 1: It's a small file -> Return full content
            if focus_file in self.small_files:
                content = self.small_files[focus_file]
                return f"=== 🔒 FOCUSED MODE: {focus_file} ===\n{content}"
            
            # Case 2: It's a large file -> Strict Vector Search
            elif focus_file in self.large_files:
                # Retrieve MORE chunks (top-15) since we are focused on this alone
                retrieved_chunks = self.vector_engine.search(
                    user_query, 
                    n_results=15, 
                    file_filter=focus_file
                )
                if retrieved_chunks:
                    combined_context = f"=== 🔒 FOCUSED MODE: {focus_file} (Top Excerpts) ===\n"
                    for i, chunk in enumerate(retrieved_chunks):
                        combined_context += f"\n--- Excerpt {i+1} ---\n{chunk}\n"
                return combined_context
            
            else:
                return "❌ Error: Focused file not found in index."

        # --- MODE B: GLOBAL (HYBRID) ---
        else:
            # 1. Add ALL Small Files
            for fname, content in self.small_files.items():
                combined_context += f"\n{'='*20}\n📄 FILE: {fname}\n{'='*20}\n{content}\n"
            
            # 2. Vector Search (Hybrid Router logic)
            if self.large_files:
                # Detect intent for specific large file (implicit focus)
                target_file = None
                for fname in self.large_files:
                    if fname.lower() in user_query.lower():
                        target_file = fname
                        break
                
                # Search
                if target_file:
                    retrieved_chunks = self.vector_engine.search(user_query, n_results=10, file_filter=target_file)
                else:
                    retrieved_chunks = self.vector_engine.search(user_query, n_results=5)

                if retrieved_chunks:
                    combined_context += "\n\n=== 🔍 RELEVANT EXCERPTS FROM LARGE DOCUMENTS ===\n"
                    for i, chunk in enumerate(retrieved_chunks):
                        combined_context += f"\n--- Excerpt {i+1} ---\n{chunk}\n"

        return combined_context