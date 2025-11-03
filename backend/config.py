import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Data paths
PDF_PATH = os.path.join(DATA_DIR, "medical_docs.pdf")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index")
TEXTS_DIR = os.path.join(DATA_DIR, "texts")

# Ensure directories exist
for dir_path in [DATA_DIR, FAISS_INDEX_PATH, TEXTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"
EMBED_MODEL_NAME = "nomic-embed-text"  # Faster model for embeddings
LLM_MODEL_NAME = "llama2"    # Model to use for generation

# Text splitting settings
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

# API settings
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
DEFAULT_TEMPERATURE = 0.7