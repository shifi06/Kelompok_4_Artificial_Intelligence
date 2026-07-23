import pandas as pd
import time
from app.models.book import BookVectorDB

def find_column(df, aliases):
    """
    Mencari nama kolom asli di CSV berdasarkan daftar opsi alias.
    Mengabaikan spasi berlebih dan huruf besar/kecil.
    """
    col_map = {col.strip().lower(): col for col in df.columns}
    for alias in aliases:
        alias_clean = alias.strip().lower()
        if alias_clean in col_map:
            return col_map[alias_clean]
    return None

def run_bulk_insert_csv(file_path):
    print(f"\n==========================================")
    print(f"Membaca file {file_path}...")
    
    try:
        # 1. Baca file CSV
        df = pd.read_csv(file_path)
        
        # 2. Deteksi pemetaan kolom secara dinamis
        title_col = find_column(df, ['title', 'judul'])
        author_col = find_column(df, ['author', 'penulis', 'creator'])
        category_col = find_column(df, ['category', 'generes', 'genre', 'kategori'])
        pages_col = find_column(df, ['pages', 'page_count', 'halaman'])
        desc_col = find_column(df, ['description', 'synopsis', 'sinopsis', 'summary'])
        
        # Pengecekan kolom utama (Wajib ada Judul & Deskripsi/Sinopsis)
        if not title_col or not desc_col:
            print(f"❌ Error: Kolom Judul atau Deskripsi/Sinopsis tidak ditemukan di {file_path}.")
            print(f"Kolom yang ada pada file ini: {list(df.columns)}")
            return

        # 3. Bersihkan data (Hapus baris jika Title atau Sinopsis kosong)
        df = df.dropna(subset=[title_col, desc_col])
        
        total_books = len(df)
        print(f"✅ Pemetaan Kolom Berhasil:")
        print(f"   • Judul     : '{title_col}'")
        print(f"   • Penulis   : '{author_col}'")
        print(f"   • Kategori  : '{category_col}'")
        print(f"   • Halaman   : '{pages_col}'")
        print(f"   • Deskripsi : '{desc_col}'")
        print(f"Ditemukan {total_books} data siap diproses. Memulai embedding ke Ollama...")
        
        # 4. Looping untuk memasukkan ke Vector DB
        for index, row in df.iterrows():
            book_id = int(time.time() * 1000) + index
            
            # Ambil data sesuai kolom yang berhasil dipetakan
            title = str(row[title_col]).strip()
            synopsis = str(row[desc_col]).strip()
            
            author = str(row[author_col]).strip() if author_col and pd.notna(row[author_col]) else "Penulis Tidak Diketahui"
            category = str(row[category_col]).strip() if category_col and pd.notna(row[category_col]) else "Umum"
            pages = str(row[pages_col]).strip() if pages_col and pd.notna(row[pages_col]) else "N/A"
            
            # Gabungkan informasi menjadi konteks lengkap untuk AI
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
            
        print(f"🎉 Bulk insert untuk file '{file_path}' selesai!")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' tidak ditemukan.")
    except Exception as e:
        print(f"❌ Terjadi kesalahan sistem: {str(e)}")

if __name__ == "__main__":
    # Daftar CSV yang ingin diproses sekaligus
    csv_files = [
        'google_books_1299.csv',
        'dataset_tech_900.csv'
    ]
    
    for csv_file in csv_files:
        run_bulk_insert_csv(csv_file)