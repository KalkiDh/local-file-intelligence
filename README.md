# Local File Intelligence System 🧠

A terminal-based **RAG (Retrieval-Augmented Generation)** tool that lets you chat with your local files (PDF, CSV, TXT) using a local LLM (Ollama).

> **Privacy First:** No data leaves your machine. Everything runs offline.

## 🚀 Features

* **Multi-File Support:** Ingests PDFs, CSVs, Text files, Markdown, and Code (.py, .json) simultaneously.
* **Smart Formatting:** Automatically converts CSVs to Markdown tables and cleans PDF text.
* **Context-Aware:** Feeds full document context to the LLM for deep analysis.
* **CLI Interface:** Simple, interactive terminal chat with a thinking spinner.
* **Source Grounding:** citations and fact-checking prompts to reduce hallucinations.

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **LLM Engine:** Ollama (Llama 3)
* **Parsers:** `pdfplumber` (PDF), `pandas` (CSV/Excel)
* **Architecture:** Direct Context RAG (No Vector DB required for small-to-medium datasets).

## 📦 Installation

### 1. Prerequisites
* **Python** installed.
* **[Ollama](https://ollama.com/)** installed and running.

### 2. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/local-file-intelligence.git](https://github.com/YOUR_USERNAME/local-file-intelligence.git)
cd local-file-intelligence

3. Setup Virtual Environment
Bash

# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate


4. Install Dependencies
Bash

pip install ollama pdfplumber pandas tabulate
5. Pull the Model
Ensure Ollama is running, then pull the model you want to use (default is llama3):

Bash

ollama pull llama3
🖥️ Usage
Place your documents inside a folder (e.g., ./data/my_docs).

Run the main script pointing to that folder:

Bash

python main.py --files ./data/my_docs
Chat!

System: "Context loaded from 5 files..."

You: "Summarize the quarterly sales report."

You: "What are the key risks mentioned in the PDF?"

📂 Project Structure
local_file_intelligence/
├── core/
│   ├── agent.py            # Main interaction logic with Ollama
│   └── prompt_templates.py # System prompts for RAG & Formatting
├── utils/
│   └── file_loader.py      # Universal file parser (PDF/CSV/Text)
├── data/                   # (Ignored by Git) Place your files here
├── main.py                 # CLI Entry point
└── README.md
🔮 Future Roadmap
[ ] Vector Database: Add ChromaDB for handling large document sets (100+ files).

[ ] Agentic Mode: Re-enable Python code execution for complex math.

[ ] Memory: Add conversation history so the LLM remembers previous turns.


