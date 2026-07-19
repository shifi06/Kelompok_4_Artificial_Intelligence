import pandas as pd
import time
from app.models.book import BookVectorDB

def run_bulk_insert_csv():
    print("Membaca file google_books_1299.csv...")
    
    try:
        # 1. Baca file CSV
        df = pd.read_csv('google_books_1299.csv')
        
        # Deteksi nama kolom deskripsi (mengantisipasi 'description' atau 'descriptio' yang terpotong)
        desc_col = 'description' if 'description' in df.columns else 'descriptio' if 'descriptio' in df.columns else None
        
        # 2. Bersihkan data (Hapus baris jika judul atau deskripsinya kosong)
        if desc_col:
            df = df.dropna(subset=['title', desc_col])
        
        total_books = len(df)
        print(f"Ditemukan {total_books} buku yang siap diproses. Memulai embedding ke Ollama...")
        
        # 3. Looping untuk memasukkan ke Vector DB
        for index, row in df.iterrows():
            # Buat ID unik
            book_id = int(time.time() * 1000) + index
            
            # --- AMBIL SEMUA DATA SESUAI HEADER HEADER ---
            title = str(row.get('title', 'Tanpa Judul'))
            category = str(row.get('generes', 'Umum')) if pd.notna(row.get('generes')) else "Umum"
            author = str(row.get('author', 'Penulis Tidak Diketahui')) if pd.notna(row.get('author')) else "Tidak diketahui"
            
            # Data Ekstra
            rating = str(row.get('rating', 'N/A'))
            voters = str(row.get('voters', '0'))
            price = str(row.get('price', 'N/A'))
            currency = str(row.get('currency', ''))
            publisher = str(row.get('publisher', 'Tidak diketahui'))
            
            # Antisipasi header terpotong untuk halaman
            page_count = str(row.get('page_count', row.get('page_cou', 'N/A')))
            isbn = str(row.get('ISBN', 'N/A'))
            language = str(row.get('language', 'N/A'))
            published_date = str(row.get('published_date', 'N/A'))
            
            # Ambil sinopsis asli
            sinopsis = str(row.get(desc_col, '')) if desc_col else ''
            
            # 🌟 GABUNGKAN SEMUA INFO MENJADI SATU KONTEKS SUPER LENGKAP UNTUK AI
            description_lengkap = (
                f"Buku '{title}' ini ditulis oleh {author}. "
                f"Diterbitkan oleh {publisher} pada {published_date}. Bahasa pengantar: {language}. "
                f"Buku ini memiliki rating {rating}/5 berdasarkan {voters} ulasan. "
                f"Jumlah halaman: {page_count} halaman. Harga: {price} {currency}. ISBN: {isbn}. "
                f"Sinopsis Utama: {sinopsis}"
            )
            
            print(f"[{index + 1}/{total_books}] Memproses: {title[:40]}...")
            
            # Masukkan ke Vector DB (hanya butuh title, category, dan description)
            BookVectorDB.add_book(
                book_id=book_id,
                title=title,
                category=category,
                description=description_lengkap
            )
            
        print("\n🎉 Bulk insert CSV selesai! Semua buku beserta metadata detailnya berhasil masuk ke Vector DB.")
        
    except FileNotFoundError:
        print("Error: File 'google_books_1299.csv' tidak ditemukan. Pastikan sejajar dengan file python ini.")
    except Exception as e:
        print(f"Terjadi kesalahan sistem: {str(e)}")

if __name__ == "__main__":
    run_bulk_insert_csv()