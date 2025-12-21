import sys
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

import config
import os
import json
import datetime



def load_and_split_pdf() -> List:
    """Load PDF and split into chunks."""
    print(f"Loading PDF from: {config.PDF_PATH}")
    
    try:
        # Load PDF
        loader = PyMuPDFLoader(config.PDF_PATH)
        pages = loader.load()
        
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )
        
        splits = text_splitter.split_documents(pages)
        print(f"Split PDF into {len(splits)} chunks")
        return splits
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        sys.exit(1)

def create_vectorstore(documents: List) -> None:
    """Create and save FAISS vectorstore using Ollama embeddings."""
    print("Initializing Ollama embeddings...")
    embeddings = OllamaEmbeddings(
        base_url=config.OLLAMA_BASE_URL,
        model=config.EMBED_MODEL_NAME
    )
    
    print(f"Creating FAISS vectorstore for {len(documents)} chunks...")
    try:
        # Create embeddings with progress tracking
        total_chunks = len(documents)
        for i, _ in enumerate(documents, 1):
            if i % 10 == 0:  # Show progress every 10 chunks
                print(f"Processing chunk {i}/{total_chunks} ({(i/total_chunks)*100:.1f}%)")
        
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(config.FAISS_INDEX_PATH)
        print(f"Vectorstore saved to: {config.FAISS_INDEX_PATH}")

        # Save metadata about embedding model used to build this index
        try:
            meta = {
                "embed_model": config.EMBED_MODEL_NAME,
                "created_at": datetime.datetime.utcnow().isoformat() + "Z"
            }
            os.makedirs(config.FAISS_INDEX_PATH, exist_ok=True)
            meta_path = os.path.join(config.FAISS_INDEX_PATH, "meta.json")
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump(meta, mf)
            print(f"FAISS meta saved to: {meta_path}")
        except Exception as e:
            print(f"Warning: could not write FAISS meta file: {e}")
        
    except Exception as e:
        print(f"Error creating vectorstore: {str(e)}")
        sys.exit(1)

def main():
    """Main function to process PDF and create vectorstore."""
    print("\n=== Starting Data Preparation ===\n")
    
    # Check if PDF exists
    if not os.path.exists(config.PDF_PATH):
        print(f"Error: PDF file not found at {config.PDF_PATH}")
        sys.exit(1)
    
    # Process documents
    documents = load_and_split_pdf()
    create_vectorstore(documents)
    
    print("\n=== Data Preparation Complete ===\n")

if __name__ == "__main__":
    import os
    main()