import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

# Tentukan parameter dasar
IMG_SHAPE = (224, 224, 3) # Ukuran input standar MobileNetV2
NUM_CLASSES = 10          # Ganti dengan jumlah kelas dataset Anda

# ==========================================
# TAHAP 1: FEATURE EXTRACTION
# ==========================================

# 1. Muat model dasar MobileNetV2 (tanpa lapisan klasifikasi paling atas)
base_model = MobileNetV2(input_shape=IMG_SHAPE,
                         include_top=False,
                         weights='imagenet')

# 2. Bekukan (freeze) model dasar agar bobotnya tidak berubah saat awal pelatihan
base_model.trainable = False

# 3. Tambahkan lapisan kustom di atasnya (Classification Head)
x = base_model.output
x = GlobalAveragePooling2D()(x) # Mengubah fitur 2D menjadi vektor 1D
x = Dense(128, activation='relu')(x) # Lapisan tersembunyi
x = Dropout(0.2)(x) # Mencegah overfitting

# Lapisan output (gunakan 'sigmoid' jika klasifikasi biner, 'softmax' untuk multiclass)
predictions = Dense(NUM_CLASSES, activation='softmax')(x)

# 4. Gabungkan menjadi satu model utuh
model = Model(inputs=base_model.input, outputs=predictions)

# 5. Kompilasi model untuk tahap 1
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='categorical_crossentropy', # Gunakan 'binary_crossentropy' untuk 2 kelas
              metrics=['accuracy'])

print("Model siap untuk Tahap 1: Feature Extraction")
# Lakukan model.fit() di sini untuk melatih lapisan klasifikasi atas terlebih dahulu...


# ==========================================
# TAHAP 2: FINE-TUNING
# ==========================================
# Catatan: Lakukan ini SETELAH model dilatih pada Tahap 1 agar bobot klasifikasi stabil.

# 1. Buka kunci model dasar
base_model.trainable = True

# 2. Tentukan dari lapisan mana Anda ingin mulai melakukan fine-tuning
# MobileNetV2 memiliki 154 layer. Kita akan membekukan 100 layer pertama.
fine_tune_at = 100

# Bekukan semua layer sebelum `fine_tune_at`
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

# 3. Kompilasi ulang model dengan Learning Rate yang JAUH LEBIH KECIL
# Sangat penting menggunakan LR kecil agar tidak merusak bobot pre-trained
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001 / 10),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

print("Model siap untuk Tahap 2: Fine-Tuning")
# Lanjutkan model.fit() untuk fine-tuning...
# Simpan dalam format Keras modern (.keras)
model.save('model_mobilenetv2_saya.keras')
print("Model berhasil disimpan!")