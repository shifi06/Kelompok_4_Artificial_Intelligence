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

@main_bp.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    # Query murni dari user, jadi Vector DB nggak bakal bingung
    query = data.get('query', '')

    try:
        # 1. Cari buku relevan di Vector DB (Semantic Search)
        search_results = BookVectorDB.search_books(query, n_results=3)
        
        # 2. Susun konteks dari hasil pencarian (Konteks RAG)
        context = ""
        # Ambil secara aman pakai .get() supaya tidak error jika datanya kosong
        if search_results and search_results.get('metadatas') and len(search_results['metadatas'][0]) > 0:
            context = "[DATA BUKU DARI DATABASE PERPUSTAKAAN]:\n"
            for i, meta in enumerate(search_results['metadatas'][0]):
                desc = search_results['documents'][0][i]
                judul = meta.get('title', 'Tidak diketahui')
                penulis = meta.get('author', 'Tidak diketahui')
                kategori = meta.get('category', 'Tidak diketahui')
                halaman = meta.get('pages', 'Tidak diketahui')
                
                context += f"- Judul: {judul}\n  Penulis: {penulis}\n  Kategori: {kategori}\n  Halaman: {halaman}\n  Deskripsi: {desc}\n\n"
        else:
            context = "Saat ini tidak ada buku yang relevan di database untuk pertanyaan tersebut."

        # 3. Kirim Prompt ke Ollama (Instruksi digabung di sini secara tersembunyi)
        prompt = (
            f"Kamu adalah Asisten AI Perpustakaan yang ramah. Pengguna bertanya: '{query}'.\n\n"
            f"{context}\n"
            f"[INSTRUKSI PENTING UNTUK AI]:\n"
            f"1. Jika kamu merekomendasikan buku dari [DATA BUKU DARI DATABASE PERPUSTAKAAN], kamu WAJIB menuliskannya dalam format list rapi yang mencakup: Judul, Penulis, Kategori, Jumlah Halaman, dan Deskripsi singkat.\n"
            f"2. Jangan pernah mengarang/halusinasi buku yang tidak ada di dalam data yang diberikan.\n"
            f"3. Jawablah dengan bahasa Indonesia yang natural dan bersahabat."
        )

        # Diperbaiki: Menambahkan endpoint '/api/generate' agar tidak error 404
        api_url = f"{Config.OLLAMA_URL}/api/generate"
        
        response = requests.post(api_url, json={
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