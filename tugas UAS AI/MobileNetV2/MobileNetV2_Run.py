import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# ==========================================
# 1. KONFIGURASI NAMA FILE
# ==========================================
# Ganti dengan nama file model .keras Anda
NAMA_MODEL = 'model_mobilenetv2_full.keras' 

# Ganti dengan nama file gambar yang ingin ditebak
GAMBAR_TES = 'kucing.jpg' 

# Opsional: Masukkan nama-nama kelas Anda agar output tidak cuma berupa angka
# Urutannya harus sama dengan saat Anda melatih model (biasanya sesuai urutan abjad folder)
NAMA_KELAS = ['Ayam', 'Bebek', 'Burung', 'Kucing', 'Sapi'] # Ganti sesuai dataset Anda

# ==========================================
# 2. MEMUAT MODEL
# ==========================================
print(f"Sedang memuat model '{NAMA_MODEL}'...")
try:
    model = tf.keras.models.load_model(NAMA_MODEL)
    print("Model berhasil dimuat!\n")
except Exception as e:
    print(f"Gagal memuat model. Pastikan file ada di lokasi yang benar. Error: {e}")
    exit()

# ==========================================
# 3. MEMPROSES GAMBAR & PREDIKSI
# ==========================================
try:
    # Muat gambar dengan target ukuran MobileNetV2 (224x224)
    img = image.load_img(GAMBAR_TES, target_size=(224, 224))
    
    # Ubah gambar ke array angka dan tambahkan dimensi batch
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Normalisasi nilai pixel sesuai standar MobileNetV2 (-1 hingga 1)
    img_array_siap = preprocess_input(img_array)
    
    # Lakukan prediksi
    print(f"Sedang menebak gambar '{GAMBAR_TES}'...")
    prediksi = model.predict(img_array_siap)
    
    # Ambil indeks dengan nilai probabilitas tertinggi
    indeks_tertinggi = np.argmax(prediksi)
    tingkat_kepercayaan = np.max(prediksi) * 100
    
    # ==========================================
    # 4. TAMPILKAN HASIL
    # ==========================================
    print("-" * 30)
    print("HASIL PREDIKSI:")
    
    # Jika Anda mengisi daftar NAMA_KELAS di atas, tampilkan namanya
    if len(NAMA_KELAS) > indeks_tertinggi:
        nama_tebakan = NAMA_KELAS[indeks_tertinggi]
        print(f"Kategori    : {nama_tebakan} (Indeks ke-{indeks_tertinggi})")
    else:
        print(f"Kategori    : Indeks kelas ke-{indeks_tertinggi}")
        
    print(f"Kepercayaan : {tingkat_kepercayaan:.2f}%")
    print("-" * 30)

except FileNotFoundError:
    print(f"Error: Gambar '{GAMBAR_TES}' tidak ditemukan.")