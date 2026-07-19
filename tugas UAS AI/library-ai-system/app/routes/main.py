from flask import Blueprint, render_template, request, jsonify
import requests
from config import Config
from app.models.book import BookVectorDB

main_bp = Blueprint('main', __name__)

# Isi data awal ke Vector DB saat aplikasi dijalankan
BookVectorDB.seed_initial_data()

@main_bp.route('/')
def index():
    # Data statis untuk mensimulasikan rekomendasi pada halaman depan
    books = [
        {"title": "Pemrograman Web Modern", "category": "Teknologi / IT"},
        {"title": "Sejarah Kecerdasan Buatan", "category": "Sains / Komputer"},
        {"title": "Psikologi Manusia & AI", "category": "Psikologi / Filsafat"}
    ]
    return render_template('index.html', books=books)

# --- TAMBAHAN RUTE BARU TANPA MENGHAPUS KODE LAMA ---

@main_bp.route('/koleksi')
def koleksi():
    # Ambil semua buku langsung dari ChromaDB
    koleksi_buku = BookVectorDB.get_all_books()
    # Kirim data buku ke file HTML
    return render_template('koleksi.html', books=koleksi_buku)

@main_bp.route('/tentang-ai')
def tentang_ai():
    return render_template('tentang_ai.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

# ----------------------------------------------------

@main_bp.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    query = data.get('query', '')

    try:
        # 1. Cari buku relevan di Vector DB (Semantic Search)
        search_results = BookVectorDB.search_books(query, n_results=2)
        
        # 2. Susun konteks dari hasil pencarian (Konteks RAG)
        context = ""
        if search_results and search_results['metadatas'] and len(search_results['metadatas'][0]) > 0:
            context = "Berikut adalah buku yang tersedia di perpustakaan kami yang relevan dengan pertanyaan:\n"
            for i, meta in enumerate(search_results['metadatas'][0]):
                desc = search_results['documents'][0][i]
                context += f"- Judul: {meta['title']} (Kategori: {meta['category']}). Deskripsi: {desc}\n"
        else:
            context = "Saat ini tidak ada buku yang sangat spesifik tentang itu di database, berikan saran umum saja."

        # 3. Kirim Prompt ke Ollama beserta Konteksnya
        prompt = (
            f"Anda adalah asisten AI di perpustakaan. Pengguna bertanya: '{query}'.\n\n"
            f"Informasi Database Perpustakaan (Gunakan ini untuk menjawab jika relevan):\n{context}\n\n"
            f"Jawablah dengan bahasa Indonesia yang ramah dan singkat. Jika buku ada di database, rekomendasikan buku tersebut."
        )

        response = requests.post(Config.OLLAMA_URL, json={
            "model": Config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        
        response.raise_for_status()
        response_data = response.json()
        
        return jsonify({"response": response_data.get('response', 'Maaf, saya tidak bisa menemukan jawaban saat ini.')})
        
    except requests.exceptions.RequestException as e:
        return jsonify({"response": f"Error menghubungi server Ollama. Pastikan server menyala. Detail: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"response": f"Terjadi kesalahan pada sistem: {str(e)}"}), 500