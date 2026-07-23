import os
import requests
import chromadb
from config import Config

# Inisialisasi ChromaDB client lokal
chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_DIR)
collection = chroma_client.get_or_create_collection(name=Config.COLLECTION_NAME)

class BookVectorDB:
    @staticmethod
    def get_embedding(text):
        """Meminta vektor embedding dari server Ollama lokal"""
        try:
            # Timeout ditambahkan agar request tidak menggantung selamanya
            response = requests.post(
                Config.OLLAMA_EMBED_URL, 
                json={
                    "model": Config.OLLAMA_EMBED_MODEL,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json().get('embedding', [])
            if not embedding:
                print("⚠️ Warning: Output embedding dari Ollama kosong.")
            return embedding
        except Exception as e:
            print(f"❌ Error HTTP ke Ollama: {e}")
            return []

    @staticmethod
    def add_book(book_id, title, category, description):
        """Menambahkan atau memperbarui buku di Vector Database"""
        text_to_embed = description 
        embedding = BookVectorDB.get_embedding(text_to_embed)
        
        if embedding:
            collection.upsert(
                ids=[str(book_id)],
                embeddings=[embedding],
                documents=[description],
                metadatas=[{"title": title, "category": category}]
            )
            return True
        else:
            print(f"⚠️ GAGAL SIMPAN [{title[:25]}...]: Embedding kosong/gagal dibuat.")
            return False

    @staticmethod
    def search_books(query, n_results=5):
        """Mencari buku yang paling relevan dengan query pengguna"""
        query_embedding = BookVectorDB.get_embedding(query)
        
        if not query_embedding:
            return None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

    @staticmethod
    def get_context_for_ai(query, n_results=5):
        """
        Gunakan fungsi ini di handler AI kamu!
        Mengambil hasil Vector DB dan mengubahnya menjadi string teks utuh
        yang siap ditempel ke System Prompt LLM.
        """
        results = BookVectorDB.search_books(query, n_results=n_results)
        if not results or not results.get('documents') or not results['documents'][0]:
            return "Tidak ditemukan data buku yang relevan di database."
        
        # Menggabungkan dokumen-dokumen yang cocok menjadi 1 string
        matched_docs = results['documents'][0]
        context = "\n\n---\n\n".join(matched_docs)
        return context

    @staticmethod
    def seed_initial_data():
        """Fungsi pembantu untuk mengisi data awal jika database kosong"""
        if collection.count() == 0:
            print("Mengisi data awal ke Vector DB...")
            books = [
                (1, "Pemrograman Web Modern", "Teknologi / IT", "Buku panduan lengkap tentang HTML, CSS, JavaScript, dan framework web modern."),
                (2, "Sejarah Kecerdasan Buatan", "Sains / Komputer", "Buku yang membahas awal mula AI dari mesin Turing hingga Deep Learning masa kini."),
                (3, "Psikologi Manusia & AI", "Psikologi / Filsafat", "Membahas dampak interaksi manusia dengan asisten kecerdasan buatan dari sudut pandang psikologis."),
                (4, "Pengantar Astronomi", "Sains / Luar Angkasa", "Buku yang membahas bintang, planet, tata surya, dan fenomena alam semesta lainnya.")
            ]
            for b in books:
                teks_lengkap = f"Judul: '{b[1]}'. Kategori: {b[2]}. Deskripsi: {b[3]}"
                BookVectorDB.add_book(b[0], b[1], b[2], teks_lengkap)
            print("Selesai mengisi data Vector DB!")

    @staticmethod
    def get_all_books():
        """Mengambil semua buku dari Vector Database untuk ditampilkan di halaman koleksi"""
        try:
            results = collection.get(include=["metadatas", "documents"])
            books = []
            
            if results and results['ids']:
                for i in range(len(results['ids'])):
                    books.append({
                        'id': results['ids'][i],
                        'title': results['metadatas'][i].get('title', 'Tanpa Judul'),
                        'category': results['metadatas'][i].get('category', 'Umum'),
                        'description': results['documents'][i]
                    })
            return books
        except Exception as e:
            print(f"Error mengambil koleksi buku: {e}")
            return []