# utils/vector_store.py

import chromadb
from chromadb.utils import embedding_functions
import os
import shutil
import stat
import time

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DB_PATH = "./database_store"

def force_delete_readonly(func, path, excinfo):
    """
    Error handler for shutil.rmtree to remove read-only files on Windows.
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

class VectorEngine:
    def __init__(self, reset_db=True):
        """
        Initializes the Vector DB.
        Safe for Windows: Handles file locking issues during reset.
        """
        if reset_db and os.path.exists(DB_PATH):
            print("   🧹 Cleaning up old database...", end=" ")
            try:
                # Try standard delete
                shutil.rmtree(DB_PATH, onerror=force_delete_readonly)
            except PermissionError:
                # If locked, wait 1 second and force try again
                print(" (Locked, retrying)...", end=" ")
                time.sleep(1.0)
                try:
                    shutil.rmtree(DB_PATH, onerror=force_delete_readonly)
                except Exception as e:
                    print(f"\n   ⚠️ Warning: Could not fully delete DB ({e}). Trying to proceed.")
            print("Done.")

        self.client = chromadb.PersistentClient(path=DB_PATH)
        
        # Uses HuggingFace model locally (downloads once, then runs offline)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        
        self.collection = self.client.get_or_create_collection(
            name="active_session_docs",
            embedding_function=self.embedding_fn
        )

    def add_document(self, filename, text_chunks):
        """
        Adds chunks to the vector index with metadata.
        """
        if not text_chunks:
            return

        ids = [f"{filename}_{i}" for i in range(len(text_chunks))]
        metadatas = [{"source": filename, "chunk_index": i} for i in range(len(text_chunks))]
        
        self.collection.add(
            documents=text_chunks,
            ids=ids,
            metadatas=metadatas
        )

    def search(self, query, n_results=5, file_filter=None):
        """
        Search with optional file filtering.
        """
        if self.collection.count() == 0:
            return []

        # Prepare filter query if a specific file is requested
        where_clause = {"source": file_filter} if file_filter else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause  # <--- This forces the DB to look at the specific file
        )
        
        # Check if we got results
        if not results['documents']:
            return []
            
        return results['documents'][0]