# main.py

import argparse
import sys
import time
import threading
from core.agent import Agent
from utils.file_loader import load_files_from_directory

# Simple spinner animation
def spinner(stop_event):
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{chars[i % len(chars)]} AI Thinking... ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 20 + "\r") # Clear line

def main():
    parser = argparse.ArgumentParser(description="Local File Intelligence CLI (Robust RAG)")
    parser.add_argument("--files", type=str, help="Path to the folder containing your files", required=True)
    args = parser.parse_args()

    print("\n🚀 System Initialized (High-Precision Mode)")
    print("-" * 40)
    
    # 1. Load Files
    context_text, _, count = load_files_from_directory(args.files)
    
    if count == 0:
        print("❌ No valid files found. Exiting.")
        sys.exit(1)
        
    print(f"ℹ️  Context loaded from {count} files. Size: {len(context_text)} chars.")
    print("   Type 'exit' to quit.")
    print("-" * 40)

    # 2. Initialize Agent
    agent = Agent(model="llama3") 

    # 3. Interactive Loop
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input: continue
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            
            # Start spinner in background
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=spinner, args=(stop_spinner,))
            spinner_thread.start()
            
            # Get response
            response = agent.query(user_input, context_text)
            
            # Stop spinner
            stop_spinner.set()
            spinner_thread.join()
            
            print(f"{response}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()