import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# Mengarah ke folder hasil ekstrak Kaggle
folder_dataset = 'flowers' 

# Augmentasi Gambar (Mengajari AI variasi sudut, posisi, dan zoom bunga)
datagen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
    rotation_range=30,      
    width_shift_range=0.2,  
    height_shift_range=0.2, 
    zoom_range=0.2,         
    horizontal_flip=True,   
    validation_split=0.2    # 80% Training, 20% Validation
)

print("=== LANGKAH 2: MEMUAT DATA GAMBAR ===")
train_generator = datagen.flow_from_directory(
    folder_dataset,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = datagen.flow_from_directory(
    folder_dataset,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)


# =====================================================================
# BAGIAN 3: MEMBANGUN ARSITEKTUR MODEL AI
# =====================================================================
# Memuat fondasi ResNet50 dengan bobot pretrained 'imagenet'
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Kunci seluruh lapisan dasar di awal (Tahap 1)
for layer in base_model.layers:
    layer.trainable = False

# Membuat struktur lapisan baru ("Kepala Klasifikasi") khusus untuk 5 kelas bunga kita
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(256, activation='relu')(x) 
x = Dropout(0.5)(x)                  # Lapisan pelindung agar AI tidak cuma menghafal foto
prediksi_akhir = Dense(5, activation='softmax')(x) 

# Menggabungkan base_model dan kepala klasifikasi baru
model = Model(inputs=base_model.input, outputs=prediksi_akhir)


# =====================================================================
# BAGIAN 4: SETTING FITUR KEAMANAN PELATIHAN (CALLBACKS)
# =====================================================================
# Berhenti otomatis jika akurasi ujian (val_accuracy) mandek dalam 4 putaran
hentikan_otomatis = EarlyStopping(monitor='val_accuracy', patience=4, restore_best_weights=True)

# Menurunkan kecepatan belajar jika AI mulai kebingungan di tengah jalan
turunkan_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=0.000001)


# =====================================================================
# BAGIAN 5: PROSES TRAINING TAHAP 1 (LATIHAN DASAR)
# =====================================================================
print("\n================ TAHAP 1: MULAI BELAJAR NYANTAI ================")
# Kompilasi awal dengan Learning Rate standar (0.001)
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# Latih kepala model baru selama 10 putaran awal
model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=10, 
    callbacks=[hentikan_otomatis, turunkan_lr]
)


# =====================================================================
# BAGIAN 6: PROSES TRAINING TAHAP 2 (FINE-TUNING KUNCI AKURASI 95%+)
# =====================================================================
print("\n================ TAHAP 2: FINE-TUNING (MEMBUKA OTAK RESNET) ================")

# 1. Buka gembok 20 lapisan paling atas dari otak ResNet50 agar bisa menyesuaikan detail bunga
for layer in base_model.layers[-20:]:
    layer.trainable = True

# 2. Kompilasi ulang, WAJIB menggunakan Learning Rate yang super kecil (0.00001) 
# agar AI menyerap detail tipis tanpa merusak pengetahuan dasar ResNet50
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# 3. Latih kembali selama maksimal 15 putaran untuk pemantapan tingkat tinggi
sejarah_pelatihan_final = model.fit(
    train_generator,
    validation_data=validation_generator,
    epochs=15, 
    callbacks=[hentikan_otomatis, turunkan_lr]
)


# =====================================================================
# BAGIAN 7: MENYIMPAN MODEL AKHIR
# =====================================================================
nama_file_simpan = 'model_klasifikasi_bunga_kaggle.keras'
model.save(nama_file_simpan)

print("\n=====================================================================")
print(f"PROSES SUKSES TOTAL! Model super akurat Anda disimpan sebagai: {nama_file_simpan}")
print("Silakan klik kanan/titik tiga pada file tersebut di menu kiri untuk mendownloadnya.")
print("=====================================================================")