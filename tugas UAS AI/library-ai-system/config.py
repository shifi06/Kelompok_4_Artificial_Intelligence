import os

class Config:
    SECRET_KEY = 'rahasia-perpustakaan-ai'
    
    # Konfigurasi Server Ollama
    # Diperbaiki: Menghapus spasi di awal ' http...'
    OLLAMA_URL = 'http://10.100.21.22:11434' 
    OLLAMA_MODEL = 'qwen3:8b' 
    
    # DITAMBAHKAN: Endpoint embedding yang tadi hilang
    OLLAMA_EMBED_URL = f'{OLLAMA_URL}/api/embeddings'
    
    # (Opsional) Model khusus embedding jika berbeda dengan model chat
    OLLAMA_EMBED_MODEL = 'nomic-embed-text'
    
    # Konfigurasi Vector DB (Chroma)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CHROMA_DB_DIR = os.path.join(BASE_DIR, 'chroma_data')
    COLLECTION_NAME = 'library_books'