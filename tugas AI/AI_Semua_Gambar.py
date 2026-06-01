import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image

# ==========================================
# 1. MUAT MODEL RESNET50 LENGKAP (include_top=True)
# ==========================================
# Kita nyalakan 'include_top' karena kita ingin memakai 1000 kategori asli ImageNet
print("Memuat model ResNet50 lengkap dengan 1000 kategori...")
model_asli = ResNet50(weights='imagenet', include_top=True)

# ==========================================
# 2. SIAPKAN GAMBAR RANDOM ANDAaN UNTUK DITEBAK OLEH AI
# ==========================================
# Ganti nama file sesuai gambar yang Anda upload
path_gambar = 'gambar_tes.jpg' 

# ResNet50 butuh ukuran 224x224
img = image.load_img(path_gambar, target_size=(224, 224))
x = image.img_to_array(img)
x = np.expand_dims(x, axis=0) # Ubah jadi batch (1, 224, 224, 3)

# Preprocessing standar ResNet
x = preprocess_input(x)

# ==========================================
# 3. PREDIKSI (AI MENEBAK GAMBAR)
# ==========================================
print("\nAI sedang berpikir...")
preds = model_asli.predict(x)

# decode_predictions mengubah kode angka menjadi nama benda yang bisa dibaca manusia
# Kita ambil 3 tebakan teratas (top-3)
hasil = decode_predictions(preds, top=3)[0]

# Tampilkan gambar dan hasil tebakannya
plt.figure(figsize=(6,6))
plt.imshow(img)
plt.axis('off')
title_text = f"Tebakan AI:\n1. {hasil[0][1]} ({hasil[0][2]*100:.1f}%)\n2. {hasil[1][1]} ({hasil[1][2]*100:.1f}%)"
plt.title(title_text)
plt.show()

print("\nDetail Hasil Prediksi:")
for i, (id, nama, skor) in enumerate(hasil):
    print(f"{i+1}. {nama}: {skor*100:.2f}% yakin")