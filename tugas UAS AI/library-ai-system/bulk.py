import pandas as pd
import time
from app.models.book import BookVectorDB

def run_bulk_insert_csv():
    file_path = 'dataset_anime_20000.csv'
    print(f"Membaca file {file_path}...")
    
    try:
        # 1. Baca file CSV
        df = pd.read_csv(file_path)
        
        # 2. Bersihkan data (Hapus baris jika Title atau Synopsis kosong)
        df = df.dropna(subset=['Title', 'Synopsis'])
        
        total_books = len(df)
        print(f"Ditemukan {total_books} data yang siap diproses. Memulai embedding ke Ollama...")
        
        # 3. Looping untuk memasukkan ke Vector DB
        for index, row in df.iterrows():
            # Buat ID unik
            book_id = int(time.time() * 1000) + index
            
            # --- AMBIL DATA SESUAI HEADER CSV ('Title', 'Author', 'Category', 'Pages', 'Synopsis') ---
            title = str(row.get('Title', 'Tanpa Judul')).strip()
            author = str(row.get('Author', 'Penulis Tidak Diketahui')).strip() if pd.notna(row.get('Author')) else "Penulis Tidak Diketahui"
            category = str(row.get('Category', 'Umum')).strip() if pd.notna(row.get('Category')) else "Umum"
            pages = str(row.get('Pages', 'N/A')).strip() if pd.notna(row.get('Pages')) else "N/A"
            synopsis = str(row.get('Synopsis', '')).strip() if pd.notna(row.get('Synopsis')) else ""
            
            # 🌟 GABUNGKAN INFO TERSEDIA MENJADI SATU KONTEKS LENGKAP UNTUK AI
            description_lengkap = (
                f"Judul: '{title}'. Ditulis oleh {author}. "
                f"Kategori/Genre: {category}. Jumlah Halaman: {pages}. "
                f"Sinopsis Utama: {synopsis}"
            )
            
            print(f"[{index + 1}/{total_books}] Memproses: {title[:40]}...")
            
            # Masukkan ke Vector DB
            BookVectorDB.add_book(
                book_id=book_id,
                title=title,
                category=category,
                description=description_lengkap
            )
            
        print("\n🎉 Bulk insert CSV selesai! Semua data berhasil masuk ke Vector DB.")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' tidak ditemukan. Pastikan sejajar dengan file python ini.")
    except Exception as e:
        print(f"Terjadi kesalahan sistem: {str(e)}")

if __name__ == "__main__":
    run_bulk_insert_csv()