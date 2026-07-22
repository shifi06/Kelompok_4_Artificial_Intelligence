import csv
import random

# 1. Bahan Racikan Data Acak
kata_depan = ["Reinkarnasi Menjadi", "Kisah Sang", "Bangkitnya", "Petualangan", "Legenda", "Solo", "Kehidupan Baru", "Dunia"]
kata_tengah = ["Pahlawan", "Raja Iblis", "Ksatria Sihir", "Assassin", "Slime", "NPC", "Pemburu Naga", "Dewa"]
kata_belakang = ["di Dunia Lain", "dengan Status Max", "Kembali ke Masa Lalu", "di Akademi Sihir", "Online", "Terkuat"]
nama_penulis = ["Kawahara", "Oda", "Isayama", "Kishimoto", "Akutami", "Fujimoto", "Chugong", "Kubo", "Togashi"]
kategori_list = [
    "Isekai, Action, Fantasy", 
    "Sci-Fi, Mecha, Drama", 
    "School, Romance, Comedy", 
    "Dark Fantasy, Thriller",
    "Adventure, Magic, Shounen"
]

NAMA_FILE = 'dataset_anime_20000.csv'
TOTAL_DATA = 20000

print(f"⏳ Sedang membuat file {NAMA_FILE} berisi {TOTAL_DATA} baris...")

# 2. Proses Pembuatan File CSV
with open(NAMA_FILE, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Bikin Header (Baris paling atas di Excel)
    writer.writerow(['Title', 'Author', 'Category', 'Pages', 'Synopsis'])
    
    # Looping 20.000 kali untuk bikin datanya
    for i in range(TOTAL_DATA):
        judul = f"{random.choice(kata_depan)} {random.choice(kata_tengah)} {random.choice(kata_belakang)} Vol. {random.randint(1, 50)}"
        penulis = f"{random.choice(nama_penulis)} {random.choice(['T.', 'K.', 'R.', 'S.', 'Y.'])}"
        kategori = random.choice(kategori_list)
        halaman = f"{random.randint(150, 450)} Halaman"
        
        deskripsi = f"Volume ini melanjutkan kisah luar biasa dari {judul}. Sang protagonis harus menghadapi ancaman baru di dunianya menggunakan kekuatan rahasia yang dimilikinya. Karya epik ini ditulis oleh {penulis}."
        
        # Tulis ke dalam file CSV
        writer.writerow([judul, penulis, kategori, halaman, deskripsi])

print("✅ SUKSES! File CSV berhasil dibuat. Silakan cek folder kamu!")