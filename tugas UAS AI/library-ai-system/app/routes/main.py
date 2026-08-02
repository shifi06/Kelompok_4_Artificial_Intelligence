from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort, Response, session
import requests
import re
from config import Config
from app.models.book import BookVectorDB

main_bp = Blueprint('main', __name__)

# Isi data awal ke Vector DB saat aplikasi dijalankan
BookVectorDB.seed_initial_data()

# =========================================================
# HALAMAN UTAMA
# =========================================================

@main_bp.route('/')
def index():
    # Tampilkan rekomendasi buku nyata dari Vector DB di halaman depan
    books = BookVectorDB.get_all_books()[:3]
    return render_template('index.html', books=books)

# =========================================================
# CRUD BUKU
# =========================================================

@main_bp.route('/books')
def list_books():
    """READ: Menampilkan seluruh koleksi buku"""
    books = BookVectorDB.get_all_books()
    letters = set()
    has_special = False
    for b in books:
        ch = (b['title'] or '').strip()[:1].upper()
        if ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            letters.add(ch)
        elif ch != '':
            has_special = True
    return render_template(
        'books.html',
        books=books,
        available_letters=sorted(letters),
        has_special=has_special,
    )


@main_bp.route('/books/<int:book_id>')
def book_detail(book_id):
    """READ: Menampilkan detail satu buku (halaman unik per buku, bagus untuk SEO)"""
    book = BookVectorDB.get_book(str(book_id))
    if not book:
        abort(404)
    return render_template('book_detail.html', book=book)


@main_bp.route('/books/new')
def new_book():
    """CREATE: Form untuk menambahkan buku baru"""
    return render_template('book_form.html', book=None)


@main_bp.route('/books/create', methods=['POST'])
def create_book():
    """CREATE: Menyimpan buku baru ke Vector DB"""
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    category = request.form.get('category', '').strip() or 'Umum'
    description = request.form.get('description', '').strip()

    if not title or not description:
        flash('Judul dan deskripsi buku wajib diisi.', 'danger')
        return redirect(url_for('main.new_book'))

    # Tentukan ID baru (ID tertinggi + 1)
    books = BookVectorDB.get_all_books()
    numeric_ids = [int(b['id']) for b in books if str(b['id']).isdigit()]
    next_id = max(numeric_ids, default=0) + 1

    if BookVectorDB.add_book(next_id, title, author, category, description):
        flash(f'Buku "{title}" berhasil ditambahkan.', 'success')
    else:
        flash('Gagal menambahkan buku. Pastikan server Ollama aktif.', 'danger')
    return redirect(url_for('main.list_books'))


@main_bp.route('/books/<int:book_id>/edit')
def edit_book(book_id):
    """UPDATE: Form untuk mengubah data buku"""
    book = BookVectorDB.get_book(str(book_id))
    if not book:
        flash('Buku tidak ditemukan.', 'warning')
        return redirect(url_for('main.list_books'))
    return render_template('book_form.html', book=book)


@main_bp.route('/books/<int:book_id>/update', methods=['POST'])
def update_book(book_id):
    """UPDATE: Menyimpan perubahan data buku"""
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    category = request.form.get('category', '').strip() or 'Umum'
    description = request.form.get('description', '').strip()

    if not title or not description:
        flash('Judul dan deskripsi buku wajib diisi.', 'danger')
        return redirect(url_for('main.edit_book', book_id=book_id))

    if BookVectorDB.update_book(book_id, title, author, category, description):
        flash(f'Buku "{title}" berhasil diperbarui.', 'success')
        return redirect(url_for('main.book_detail', book_id=book_id))
    else:
        flash('Gagal memperbarui buku. Pastikan server Ollama aktif.', 'danger')
        return redirect(url_for('main.edit_book', book_id=book_id))


@main_bp.route('/books/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """DELETE: Menghapus buku dari Vector DB"""
    if BookVectorDB.delete_book(str(book_id)):
        flash('Buku berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus buku.', 'danger')
    return redirect(url_for('main.list_books'))


# =========================================================
# SEO: robots.txt & sitemap.xml
# =========================================================

@main_bp.route('/robots.txt')
def robots_txt():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {request.url_root}sitemap.xml\n"
    )
    return Response(content, mimetype='text/plain')


@main_bp.route('/sitemap.xml')
def sitemap():
    pages = [
        {'loc': '', 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': '/books', 'priority': '0.9', 'changefreq': 'daily'},
    ]
    books = BookVectorDB.get_all_books()
    for b in books:
        pages.append({'loc': f"/books/{b['id']}", 'priority': '0.7', 'changefreq': 'weekly'})

    urls = []
    for p in pages:
        url = f"{request.url_root}{p['loc'].lstrip('/')}"
        urls.append(
            f"<url><loc>{url}</loc><changefreq>{p['changefreq']}</changefreq>"
            f"<priority>{p['priority']}</priority></url>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return Response(xml, mimetype='application/xml')


# =========================================================
# AI CHAT (Asisten Perpustakaan)
# =========================================================

@main_bp.route('/ask-ai', methods=['POST'])
def ask_ai():
    data = request.get_json()
    # Query murni dari user, jadi Vector DB nggak bakal bingung
    query = (data.get('query', '') or '').strip()

    if not query:
        return jsonify({"response": "Halo! Ada yang bisa saya bantu? Coba tulis pertanyaanmu dulu ya. 😊"}), 200

    # ============ RIWAYAT PERCAKAPAN (Session) ============
    history = session.get('chat_history', [])
    history.append({"role": "user", "content": query})
    # Batasi riwayat agar prompt tidak meledak (maks 5 pesan terakhir)
    history = history[-10:]

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

        # 3. Susun riwayat percakapan menjadi teks (tanpa pesan terbaru)
        history_lines = [
            f"{'Pengguna' if m['role'] == 'user' else 'Lia'}: {m['content']}"
            for m in history[:-1]
        ]
        history_text = "\n".join(history_lines) if history_lines else "(Ini adalah awal percakapan)"

        # 4. Kirim Prompt ke Ollama (Persona "Lia" yang hidup & natural)
        prompt = (
            "Kamu adalah 'Lia', pustakawan cerdas yang ceria, hangat, dan sangat ramah. "
            "Kamu berbicara seperti manusia asli yang sedang mengobrol santai dengan pengunjung perpustakaan, bukan seperti mesin atau chatbot yang kaku.\n\n"
            f"[RIWAYAT PERCAKAPAN SEBELUMNYA]:\n{history_text}\n\n"
            f"[PERTANYAAN TERBARU DARI PENGGUNA]:\n\"{query}\"\n\n"
            f"{context}\n"
            "[INSTRUKSI PENTING UNTUK LIA]:\n"
            "1. Balas dengan bahasa Indonesia yang santai, natural, dan hidup — seperti sedang chat dengan teman. Jangan mulai dengan kalimat template seperti 'Tentu!' atau 'Baik, akan saya bantu.' Variasikan gaya bicaramu.\n"
            "2. Gunakan emoji ringan secukupnya (seperti 📚 😊 ✨ 👋) untuk membuat obrolan terasa hangat, tapi jangan berlebihan.\n"
            "3. Jika pengguna menyapa (misal 'halo', 'hai', 'selamat pagi'), sapa balik dengan ramah lalu tawarkan bantuan, misalnya menanyakan buku apa yang sedang dicari.\n"
            "4. Jika pertanyaan terasa kurang jelas, ajukan pertanyaan balik yang ramah untuk memahami apa yang pengguna inginkan.\n"
            "5. Perhatikan riwayat percakapan di atas agar jawabanmu nyambung (misal pengguna meneruskan pertanyaan sebelumnya atau bertanya detail lanjutan).\n"
            "6. Jika kamu merekomendasikan buku dari [DATA BUKU DARI DATABASE PERPUSTAKAAN], tulis dalam format list rapi yang mencakup: Judul, Penulis, Kategori, dan Deskripsi singkat.\n"
            "7. Jangan pernah mengarang/menghalusinasi buku yang tidak ada di dalam data yang diberikan. Jika tidak ada buku yang cocok, akui dengan jujur lalu tawarkan membantu mencari dengan kata kunci lain.\n"
            "8. Setelah menjawab, ajak pengguna melanjutkan percakapan, misal 'Mau saya carikan yang lain?' atau 'Ada yang ingin ditanyakan lagi?'.\n"
            "9. Jawaban tidak perlu panjang-panjang. Cukup padat, hangat, dan langsung ke inti.\n"
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

        ai_response = response_data.get('response', 'Maaf, saya tidak bisa menemukan jawaban saat ini.')
        # Bersihkan tag pemikiran model (kalau ada) agar tidak bocor ke layar
        ai_response = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL).strip()
        if not ai_response:
            ai_response = "Hmm, sepertinya saya butuh sedikit waktu lagi untuk memikirkan itu. Bisa coba ditanyakan lagi?"

        # Simpan balasan AI ke riwayat percakapan
        history.append({"role": "assistant", "content": ai_response})
        session['chat_history'] = history[-10:]

        return jsonify({"response": ai_response})
        
    except requests.exceptions.RequestException as e:
        return jsonify({"response": f"Error menghubungi server Ollama. Pastikan server menyala. Detail: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"response": f"Terjadi kesalahan pada sistem: {str(e)}"}), 500
