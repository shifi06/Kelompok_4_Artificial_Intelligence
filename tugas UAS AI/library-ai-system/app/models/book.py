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
    def _build_full_text(title, author, category, description):
        """Menyusun teks lengkap yang disimpan di Vector DB (dipakai untuk embedding)"""
        parts = [f"Judul: '{title}'"]
        if author:
            parts.append(f"Penulis: {author}")
        parts.append(f"Kategori: {category}")
        parts.append(f"Deskripsi: {description}")
        return ". ".join(parts)

    @staticmethod
    def _clean_description(full_text):
        """Mengambil kembali deskripsi asli dari teks lengkap yang tersimpan di Vector DB"""
        if full_text and full_text.startswith("Judul:"):
            parts = full_text.split("Deskripsi: ", 1)
            return parts[1] if len(parts) > 1 else full_text
        return full_text

    @staticmethod
    def add_book(book_id, title, author, category, description):
        """Menambahkan buku baru di Vector Database"""
        full_text = BookVectorDB._build_full_text(title, author, category, description)
        embedding = BookVectorDB.get_embedding(full_text)
        
        if embedding:
            collection.add(
                ids=[str(book_id)],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[{"title": title, "author": author, "category": category}]
            )
            return True
        else:
            print(f"⚠️ GAGAL SIMPAN [{title[:25]}...]: Embedding kosong/gagal dibuat.")
            return False

    @staticmethod
    def update_book(book_id, title, author, category, description):
        """Memperbarui data buku yang sudah ada di Vector Database"""
        existing = BookVectorDB.get_book(str(book_id))
        if existing is None:
            print(f"⚠️ Buku dengan ID {book_id} tidak ditemukan, tidak bisa diperbarui.")
            return False

        full_text = BookVectorDB._build_full_text(title, author, category, description)
        embedding = BookVectorDB.get_embedding(full_text)

        if embedding:
            collection.update(
                ids=[str(book_id)],
                embeddings=[embedding],
                documents=[full_text],
                metadatas=[{"title": title, "author": author, "category": category}]
            )
            return True
        else:
            print(f"⚠️ GAGAL PERBARUI [{title[:25]}...]: Embedding kosong/gagal dibuat.")
            return False

    @staticmethod
    def delete_book(book_id):
        """Menghapus buku dari Vector Database berdasarkan ID"""
        try:
            collection.delete(ids=[str(book_id)])
            return True
        except Exception as e:
            print(f"❌ Error menghapus buku ID {book_id}: {e}")
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
                (1, "Pemrograman Web Modern", "Rudi Hartono", "Teknologi / IT", "Buku panduan lengkap tentang HTML, CSS, JavaScript, dan framework web modern."),
                (2, "Sejarah Kecerdasan Buatan", "Budi Santoso", "Sains / Komputer", "Buku yang membahas awal mula AI dari mesin Turing hingga Deep Learning masa kini."),
                (3, "Psikologi Manusia & AI", "Dewi Lestari", "Psikologi / Filsafat", "Membahas dampak interaksi manusia dengan asisten kecerdasan buatan dari sudut pandang psikologis."),
                (4, "Pengantar Astronomi", "Andi Wijaya", "Sains / Luar Angkasa", "Buku yang membahas bintang, planet, tata surya, dan fenomena alam semesta lainnya.")
            ]
            for b in books:
                BookVectorDB.add_book(b[0], b[1], b[2], b[3], b[4])
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
                        'author': results['metadatas'][i].get('author', 'Tidak Diketahui'),
                        'category': results['metadatas'][i].get('category', 'Umum'),
                        'description': BookVectorDB._clean_description(results['documents'][i])
                    })
            return books
        except Exception as e:
            print(f"Error mengambil koleksi buku: {e}")
            return []

    @staticmethod
    def get_book(book_id):
        """Mengambil satu buku dari Vector Database berdasarkan ID"""
        try:
            results = collection.get(ids=[str(book_id)], include=["metadatas", "documents"])
            if results and results['ids']:
                return {
                    'id': results['ids'][0],
                    'title': results['metadatas'][0].get('title', 'Tanpa Judul'),
                    'author': results['metadatas'][0].get('author', 'Tidak Diketahui'),
                    'category': results['metadatas'][0].get('category', 'Umum'),
                    'description': BookVectorDB._clean_description(results['documents'][0])
                }
            return None
        except Exception as e:
            print(f"Error mengambil buku ID {book_id}: {e}")
            return None