# main.py

import argparse
import sys
import time
import threading
from core.agent import Agent
from core.hybrid_manager import HybridContextManager
from core.summarizer import DeepSummarizer
from utils.file_loader import load_files_raw

# Spinner for UI
def spinner(stop_event):
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{chars[i % len(chars)]} AI Thinking... ")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 20 + "\r")

def main():
    parser = argparse.ArgumentParser(description="Local Hybrid RAG System")
    parser.add_argument("--files", type=str, help="Path to documents", required=True)
    args = parser.parse_args()

    print("\n🚀 Initializing Hybrid RAG Engine...")
    print("-" * 50)

    # 1. Initialize Managers
    manager = HybridContextManager()
    agent = Agent(model="llama3")
    deep_summarizer = DeepSummarizer(agent)

    # 2. Load and Route Files
    raw_files = load_files_raw(args.files)
    if not raw_files:
        print("❌ No valid files found.")
        sys.exit(1)

    print("\n🧠 Routing & Indexing Files:")
    for filename, content in raw_files:
        status = manager.process_and_index(filename, content)
        print(f"   📄 {filename:<30} → {status}")

    print("-" * 50)
    print("ℹ️  Commands:")
    print("   :files        → List all loaded files")
    print("   :focus [name] → Lock chat to a specific file")
    print("   :deep [name]  → 🧠 Deep Map-Reduce Summary (Slow but detailed)")
    print("   :all          → Return to global mode")
    print("   exit          → Quit")
    print("-" * 50)
    
    current_focus = None 

    # 4. Chat Loop
    while True:
        try:
            if current_focus:
                prompt_text = f"\n🔒 [{current_focus}] You: "
            else:
                prompt_text = "\n🌍 [Global] You: "
                
            user_input = input(prompt_text).strip()
            
            if not user_input: continue

            # --- COMMAND HANDLING ---
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if user_input.lower() == ":files":
                print("\n📂 Loaded Files:")
                for f in manager.list_files():
                    print(f" - {f}")
                continue

            if user_input.lower() == ":all":
                current_focus = None
                print("🌍 Switched to Global Mode.")
                continue

            # --- FIXED FOCUS LOGIC ---
            if user_input.lower().startswith(":focus"):
                target = user_input.replace(":focus", "").strip()
                
                # Combine both lists and search safely
                all_files = list(manager.small_files.keys()) + manager.large_files
                
                # Find first file containing the search term (case-insensitive)
                match = next((f for f in all_files if target.lower() in f.lower()), None)
                
                if match:
                    current_focus = match
                    print(f"🔒 Focused on '{current_focus}'.")
                else:
                    print(f"❌ File matching '{target}' not found. Type :files to check names.")
                continue

            # --- DEEP SUMMARY ---
            if user_input.lower().startswith(":deep"):
                target = user_input.replace(":deep", "").strip()
                all_files = list(manager.small_files.keys()) + manager.large_files
                match = next((f for f in all_files if target.lower() in f.lower()), None)
                
                if match:
                    print(f"🧠 Starting Deep Summary for: {match}")
                    print("   (This involves reading the whole file and may take time...)")
                    result = deep_summarizer.summarize_file(args.files, match)
                    print(f"\n{result}")
                else:
                    print(f"❌ File matching '{target}' not found.")
                continue

            # --- NORMAL AI QUERY ---
            stop_spinner = threading.Event()
            t = threading.Thread(target=spinner, args=(stop_spinner,))
            t.start()
            
            dynamic_context = manager.build_smart_context(user_input, focus_file=current_focus)
            response = agent.query(user_input, dynamic_context)
            
            stop_spinner.set()
            t.join()
            
            print(f"{response}")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()