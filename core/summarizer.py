# core/summarizer.py

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_loader import read_file_content

class DeepSummarizer:
    def __init__(self, agent):
        self.agent = agent

    def summarize_file(self, directory, filename):
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return "❌ File not found on disk."

        print(f"\n📖 Reading full content of {filename}...")
        text = read_file_content(file_path)
        
        # 1. Chunking (Map Phase Setup)
        # We use LARGE chunks (approx 2000-3000 tokens) for summarization
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, 
            chunk_overlap=500
        )
        chunks = splitter.split_text(text)
        total_chunks = len(chunks)
        
        print(f"🧩 Split into {total_chunks} sections. Starting Map-Reduce...")

        # 2. Map Phase (Summarize each chunk)
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"   👉 Summarizing section {i+1}/{total_chunks}...", end="\r")
            
            prompt = (
                f"Summarize the following text section concisely. "
                f"Capture key dates, facts, and definitions. Ignore filler text.\n\n"
                f"TEXT:\n{chunk}"
            )
            # We bypass the standard query method to avoid re-formatting
            # Using the agent's internal model directly if possible, or query method
            response = self.agent.query(prompt, "") # Empty context, strict prompt
            
            # Clean response (remove "AI:" prefix)
            clean_summary = response.replace("🤖 AI:", "").strip()
            chunk_summaries.append(clean_summary)

        print(f"   ✅ Map phase complete. ({total_chunks} summaries generated).")

        # 3. Reduce Phase (Combine summaries)
        print("🔥 Reducing to final Master Summary...")
        combined_summaries = "\n\n".join([f"--- Section {i+1} ---\n{s}" for i, s in enumerate(chunk_summaries)])
        
        final_prompt = (
            f"You are provided with summaries of every section of a large document. "
            f"Synthesize these into a coherent, structured Executive Summary. "
            f"Use headers and bullet points.\n\n"
            f"SECTION SUMMARIES:\n{combined_summaries}"
        )
        
        final_response = self.agent.query(final_prompt, "")
        return final_response