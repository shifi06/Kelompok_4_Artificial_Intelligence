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