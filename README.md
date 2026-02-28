# 🎓 ENSAJ AI Chatbot Assistant

An intelligent RAG-based chatbot for ENSAJ (École Nationale des Sciences Appliquées d'El Jadida) that answers student questions using a structured knowledge base, FastAPI backend, and local LLM via Ollama.

---

## 🚀 Features

- 🔍 **RAG Pipeline** — Retrieval-Augmented Generation with ChromaDB
- 🤖 **Multi-Agent System** — QA Agent & RAG Agent
- ⚡ **FastAPI Backend** — REST API with clean routing
- 🧠 **Local LLM** — Powered by Ollama (Llama 3.1)
- 🐳 **Docker Support** — docker-compose ready
- 📚 **Rich Knowledge Base** — 15+ documents covering all ENSAJ topics

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Ollama (Llama 3.1:8b) |
| RAG | ChromaDB + Custom Embeddings |
| Backend | FastAPI |
| Fine-tuning | Custom training pipeline |
| Language | Python 3.x |
| Container | Docker |

---

## 📁 Project Structure

```
ensa-chatbot/
├── src/
│   ├── agents/
│   │   ├── base_agent.py       # Base agent class
│   │   ├── qa_agent.py         # Q&A agent
│   │   └── rag_agent.py        # RAG agent
│   ├── api/
│   │   ├── main.py             # FastAPI app
│   │   ├── routes.py           # API endpoints
│   │   ├── models.py           # Pydantic schemas
│   │   └── dependencies.py     # DI & config
│   ├── rag/
│   │   ├── document_loader.py  # Load documents
│   │   ├── text_splitter.py    # Chunk text
│   │   ├── embeddings.py       # Generate embeddings
│   │   ├── vector_store.py     # ChromaDB interface
│   │   └── retriever.py        # Semantic search
│   ├── prompts/
│   │   └── prompt_templates.py # LLM prompt templates
│   ├── fine_tuning/
│   │   ├── train.py            # Fine-tuning script
│   │   └── training_data.jsonl # Training dataset
│   └── run_api.py              # Entry point
├── data/
│   └── raw/                    # Knowledge base documents
├── docker-compose.yml
├── requirements.txt
└── clean_cache.py
```

---

## 📚 Knowledge Base

The chatbot covers all ENSAJ topics including:

- 🏫 School presentation & history
- 📖 Engineering programs (6 filières)
- 📝 Admission & concours 2025
- 📋 Academic regulations
- 💰 Tuition fees & scholarships
- 🎓 Final year projects (PFE)
- 🏠 Student life & services
- 📅 Academic calendar
- ❓ FAQ

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/ouma-bg/ensaj-chatbot-assistant-.git
cd ensaj-chatbot-assistant-

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🔧 Configuration

Create a `.env` file:

```env
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3.1:8b
CHROMA_DB_PATH=./chroma_db
```

---

## 🏃 Run

### With Docker

```bash
docker-compose up
```

### Without Docker

```bash
# Make sure Ollama is running
ollama run llama3.1:8b

# Start the API
python src/run_api.py
```

API docs: `http://localhost:8000/docs`

---

## 📬 Contact

**Oumaima**
- GitHub: [@ouma-bg](https://github.com/ouma-bg)
