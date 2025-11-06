# Medical Chatbot 🔬🤖

A clean, local medical Q&A chatbot that:

- Loads a medical PDF, splits it into chunks.
- Creates embeddings (via Ollama) and builds a FAISS vector store.
- Serves a lightweight Flask backend and a static frontend UI for chat.

---

## 🚀 Quick Highlights

- Fast embedding model: `nomic-embed-text` (configured in `backend/config.py`).
- Vector search: FAISS (saved to `data/faiss_index`).
- Serve & chat: Flask backend + simple static frontend at `http://127.0.0.1:5000`.

## 📁 Project layout

- `backend/` — Flask app, data prep, retriever.
- `data/` — PDF, FAISS index, extracted texts.
- `frontend/` — `index.html`, `script.js`, `style.css` (static UI).

---

## 🛠️ Prerequisites

- Windows (PowerShell examples provided). Works on other OSes with equivalent shell commands.
- Python 3.10+ recommended.
- Ollama installed and running locally (API at `http://localhost:11434`).
- Put your PDF at `data/medical_docs.pdf` (or update `backend/config.py`).

## ⚡ Quick Start (PowerShell)

Run these in the project root (e.g., `D:\Medical_chatbot`):

```powershell
# 1) Create & activate a venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## 🧠 Pull Ollama models

```powershell
# Embeddings (recommended fast model)
ollama pull nomic-embed-text

# (Optional) LLM for generation if you plan to run it locally
# ollama pull llama2
```

Ensure Ollama is running before creating embeddings.

## 🗂️ Prepare the FAISS vector store

This reads `data/medical_docs.pdf`, splits it into chunks, creates embeddings, and saves FAISS files to `data/faiss_index`.

```powershell
# Optional: remove previous index to rebuild
# Remove-Item -Recurse -Force .\data\faiss_index

# Build index (may take time depending on PDF size)
python backend/data_preparation.py
```

You will see progress output showing chunk counts and embedding progress.

## ▶️ Run the backend + frontend

```powershell
python backend/app.py
```

Open: http://127.0.0.1:5000

POST to `/chat` with JSON: `{ "query": "your question" }` to receive `{ "response": ..., "success": true }`.

---

## ⚙️ Configuration (edit `backend/config.py`)

- `PDF_PATH` — path to the PDF to index.
- `FAISS_INDEX_PATH` — where FAISS index is saved.
- `OLLAMA_BASE_URL` — Ollama API endpoint.
- `EMBED_MODEL_NAME` — embedding model (e.g., `nomic-embed-text`).
- `LLM_MODEL_NAME` — LLM for generation (e.g., `llama2`).
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — splitter settings (larger chunk → fewer embeddings).
- `FLASK_HOST` / `FLASK_PORT` — server bind address.

## 💡 Performance tips

- Increase `CHUNK_SIZE` and reduce `CHUNK_OVERLAP` to cut embedding count.
- Use `nomic-embed-text` (faster) as your `EMBED_MODEL_NAME`.
- Batch embeddings (if supported by the API) to reduce round trips to Ollama.

## 🐞 Troubleshooting

- "Retriever not initialized": make sure `data/faiss_index` exists and `python backend/data_preparation.py` ran successfully.
- Ollama not reachable: confirm Ollama is running and `OLLAMA_BASE_URL` is correct.
- Slow indexing: try the performance tips above.

## 🧩 Developer notes

- Backend entrypoint: `backend/app.py` (serves UI and `/chat` endpoint).
- Retriver & vectorstore: created in `backend/data_preparation.py` and stored in `data/faiss_index`.

## ✨ Next improvements

- Add a `setup.ps1` to automate venv, deps, model pulls, and index build.
- Batch embeddings to speed up indexing.
- Add tests and a benchmark script for indexing time per chunk.

---

If you want, I can add a one-click `setup.ps1` that runs these commands and a tiny status check script — tell me if you'd like that and I’ll add it.

Happy building! ✅

