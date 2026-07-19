import chromadb
import requests
from config import Config

# Inisialisasi ChromaDB client lokal
chroma_client = chromadb.PersistentClient(path=Config.CHROMA_DB_DIR)
collection = chroma_client.get_or_create_collection(name=Config.COLLECTION_NAME)

class BookVectorDB:
    @staticmethod
    def get_embedding(text):
        """Meminta vektor embedding dari server Ollama lokal"""
        try:
            response = requests.post(Config.OLLAMA_EMBED_URL, json={
                "model": Config.OLLAMA_EMBED_MODEL,
                "prompt": text
            })
            response.raise_for_status()
            return response.json().get('embedding', [])
        except Exception as e:
            print(f"Gagal mendapatkan embedding: {e}")
            return []

    @staticmethod
    def add_book(book_id, title, category, description):
        """Menambahkan buku ke Vector Database"""
        text_to_embed = f"Judul: {title}. Kategori: {category}. Deskripsi: {description}"
        embedding = BookVectorDB.get_embedding(text_to_embed)
        
        if embedding:
            collection.add(
                ids=[str(book_id)],
                embeddings=[embedding],
                documents=[description],
                metadatas=[{"title": title, "category": category}]
            )

    @staticmethod
    def search_books(query, n_results=2):
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
                BookVectorDB.add_book(b[0], b[1], b[2], b[3])
            print("Selesai mengisi data Vector DB!")

    @staticmethod
    def get_all_books():
        """Mengambil semua buku dari Vector Database untuk ditampilkan di halaman koleksi"""
        try:
            # Mengambil metadata dan dokumen dari koleksi
            results = collection.get(include=["metadatas", "documents"])
            books = []
            
            if results and results['ids']:
                for i in range(len(results['ids'])):
                    books.append({
                        'id': results['ids'][i],
                        'title': results['metadatas'][i]['title'],
                        'category': results['metadatas'][i]['category'],
                        'description': results['documents'][i]
                    })
            return books
        except Exception as e:
            print(f"Error mengambil koleksi buku: {e}")
            return []