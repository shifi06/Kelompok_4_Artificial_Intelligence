import tensorflow as tf
import os
import pathlib
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing import image_dataset_from_directory

# ==========================================
# 1. OTOMATIS DOWNLOAD DATASET BUNGA
# ==========================================
print("--- LANGKAH 1: Mendownload Dataset Bunga Otomatis ---")
dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
data_dir = tf.keras.utils.get_file('flower_photos', origin=dataset_url, extract=True)
data_dir = pathlib.Path(data_dir)

# ==========================================
# 2. MEMBAGI DATASET (TRAIN & VALIDASI)
# ==========================================
print("\n--- LANGKAH 2: Membagi Dataset (80% Train, 20% Validasi) ---")
BATCH_SIZE = 32
IMG_SIZE = (224, 224)

# Load data untuk Training (80%)
train_dataset = image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# Load data untuk Validasi (20%)
validation_dataset = image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

class_names = train_dataset.class_names
JUMLAH_KELAS = len(class_names)
print(f"Ditemukan {JUMLAH_KELAS} kelas bunga: {class_names}")

# Preprocessing format gambar khusus ResNet50
def preprocess(images, labels):
    return tf.keras.applications.resnet50.preprocess_input(images), labels

train_dataset = train_dataset.map(preprocess)
validation_dataset = validation_dataset.map(preprocess)

# ==========================================
# 3. MEMBUAT MODEL RESNET50
# ==========================================
print("\n--- LANGKAH 3: Membuat Arsitektur ResNet50 ---")
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Bekukan model dasar

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation='relu')(x) # Layer tambahan
predictions = Dense(JUMLAH_KELAS, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# ==========================================
# 4. PROSES TRAINING (BELAJAR)
# ==========================================
print("\n--- LANGKAH 4: Memulai Proses Training ---")
# Kita coba 5 epoch dulu untuk latihan agar tidak terlalu lama
EPOCHS = 5 

history = model.fit(
    train_dataset,
    validation_data=validation_dataset,
    epochs=EPOCHS
)

# ==========================================
# 5. MENYIMPAN HASIL MODEL
# ==========================================
print("\n--- LANGKAH 5: Menyimpan Model ---")
nama_file = "model_klasifikasi_bunga.keras"
model.save(nama_file)
print(f"Selesai! Model AI Anda telah disimpan dengan nama '{nama_file}'")