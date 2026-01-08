# core/agent.py

import ollama
from core.prompt_templates import RAG_SYSTEM_PROMPT

class Agent:
    def __init__(self, model="llama3"):
        self.model = model

    def query(self, user_question, context_text):
        """
        Pure RAG: Sends context + question to LLM and returns the text response.
        """
        
        # 1. Build the prompt
        full_prompt = RAG_SYSTEM_PROMPT.format(context_data=context_text)
        
        print("🤔 AI Thinking...")
        
        # 2. Call Ollama
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': full_prompt},
                {'role': 'user', 'content': user_question},
            ])
            
            # 3. Return the text directly
            return f"🤖 AI:\n{response['message']['content']}"
            
        except Exception as e:
            return f"❌ Error communicating with Ollama: {e}"