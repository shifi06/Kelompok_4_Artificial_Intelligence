import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# 1. MEMUAT KEMBALI MODEL YANG SUDAH JADI
nama_file_model = 'model_klasifikasi_bunga.keras'
model = tf.keras.models.load_model(nama_file_model)
print("Model berhasil dibuka dan dimuat!")

# 2. MENYIAPKAN GAMBAR BARU YANG INGIN DITEBAK
# Ganti 'bunga_tes.jpg' dengan nama file foto bunga Anda
path_gambar = 'foto_bunga.jpg' 
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import os

# 1. MEMUAT MODEL SUPER AKURAT YANG SUDAH DILATIH TADI
nama_file_model = 'model_klasifikasi_bunga_kaggle.keras'

if not os.path.exists(nama_file_model):
    print(f"[ERROR] File '{nama_file_model}' tidak ditemukan!")
    print("Pastikan Anda sudah menjalankan proses training sampai selesai di cell sebelumnya.")
else:
    model = tf.keras.models.load_model(nama_file_model)
    print("Model super akurat berhasil dimuat! Siap menebak.")

    # 2. MENYIAPKAN GAMBAR YANG INGIN DITEBAK
    # Ganti 'tes_bunga.jpg' dengan nama file foto bunga yang Anda upload ke Colab
    path_gambar = 'raflesia.jpg' 

    if not os.path.exists(path_gambar):
        print(f"\n[PERINGATAN] Foto '{path_gambar}' belum di-upload!")
        print("Silakan upload foto bunga ke menu Files di sebelah kiri, lalu beri nama 'tes_bunga.jpg'.")
    else:
        # Ubah ukuran gambar ke 224x224 (Standar ResNet50)
        img = image.load_img(path_gambar, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) 

        # Preprocessing wajib ResNet50
        img_array = tf.keras.applications.resnet50.preprocess_input(img_array)

        # 3. AI MULAI MENEBAK
        print("\nAI sedang menganalisis gambar...")
        prediksi = model.predict(img_array)

        # Nama kelas sesuai dengan urutan alfabet dataset Kaggle
        nama_kelas = ['Daisy (Aster)', 'Dandelion', 'Roses (Mawar)', 'Sunflowers (Matahari)', 'Tulips']

        # Mengambil hasil tebakan tertinggi
        indeks_tertinggi = np.argmax(prediksi)
        bunga_tertebak = nama_kelas[indeks_tertinggi]
        persentase_keyakinan = prediksi[0][indeks_tertinggi] * 100

        # 4. MENAMPILKAN HASIL PREDIKSI
        print("\n================ HASIL PREDIKSI AI ================")
        print(f"Nama File      : {path_gambar}")
        
        # Ambang batas keyakinan (Confidence Threshold)
        if persentase_keyakinan < 70.0:
            print(f"Tebakan AI     : {bunga_tertebak} (Status: KEMUNGKINAN BESAR SALAH / RAGU)")
            print("                 *Catatan: Gambar terlalu buram atau bukan tipe bunga yang dikenali.")
        else:
            print(f"Tebakan AI     : {bunga_tertebak}")
            
        print(f"Tingkat Akurasi: {persentase_keyakinan:.2f}% yakin")
        print("---------------------------------------------------")
        print("Detail Analisis Semua Jenis Bunga:")
        
        for i, nama in enumerate(nama_kelas):
            skor_kelas = prediksi[0][i] * 100
            print(f"- {nama:<22}: {skor_kelas:.2f}%")
        print("===================================================")
# ResNet50 butuh ukuran gambar 224x224 piksel
img = image.load_img(path_gambar, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0) # Mengubah gambar menjadi format batch

# Preprocessing wajib agar sesuai standar ResNet50
img_array = tf.keras.applications.resnet50.preprocess_input(img_array)

# 3. MEMULAI PREDIKSI (AI MENEBAK GAMBAR)
prediksi = model.predict(img_array)

# Daftar nama kelas sesuai urutan alfabet dataset bunga kemarin
nama_kelas = ['Daisy (Aster)', 'Dandelion', 'Roses (Mawar)', 'Sunflowers (Matahari)', 'Tulips']

# Mengambil hasil tebakan dengan skor tertinggi
indeks_tertinggi = np.argmax(prediksi)
bunga_tertebak = nama_kelas[indeks_tertinggi]
persentase_keyakinan = prediksi[0][indeks_tertinggi] * 100

# 4. MENAMPILKAN HASIL NYATA
print("\n================ HASIL PREDIKSI ================")
print(f"Nama File      : {path_gambar}")
print(f"Tebakan AI     : {bunga_tertebak}")
print(f"Tingkat Akurasi: {persentase_keyakinan:.2f}% yakin")
print("=================================================")