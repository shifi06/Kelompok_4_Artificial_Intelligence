import os

class Config:
    SECRET_KEY = 'rahasia-perpustakaan-ai'

    # Konfigurasi Server Ollama
    OLLAMA_URL = 'http://10.100.21.22:11434'
    OLLAMA_MODEL = 'qwen3:8b'
    OLLAMA_EMBED_URL = 'http://10.100.21.22:11434/api/embed'
    OLLAMA_EMBED_MODEL = 'qwen3:8b'  

    # Konfigurasi Vector DB (Chroma)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CHROMA_DB_DIR = os.path.join(BASE_DIR, 'chroma_data')
    COLLECTION_NAME = 'library_books'
