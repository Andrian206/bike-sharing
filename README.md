# Proyek Analisis Data: Bike Sharing Dataset

## Deskripsi Proyek
Proyek ini merupakan submission akhir untuk kelas **Belajar Fundamental Analisis Data** di Dicoding.
Proyek menganalisis data penyewaan sepeda (Bike Sharing Dataset) dari tahun 2011–2012 di Washington D.C., USA.

Dataset yang digunakan: **Bike Sharing Dataset** (Hadi Fanaee-T, University of Porto)

## Struktur Direktori
```
submission/
├───dashboard/
│   ├───main_data.csv      # Data siap pakai untuk dashboard (731 baris, 26 kolom)
│   └───dashboard.py       # Aplikasi dashboard Streamlit
├───data/
│   ├───data_1.csv         # (disamarkan di folder datasets/)
│   └───data_2.csv         # (disamarkan di folder datasets/)
├───datasets/
│   ├───day.csv            # Data agregat harian (731 baris)
│   ├───hour.csv           # Data per jam (17.379 baris)
│   └───Readme.txt         # Dokumentasi dataset
├───notebook.ipynb         # Notebook analisis data lengkap
├───README.md              # Berkas ini
├───requirements.txt       # Daftar dependensi Python
└───url.txt                # Tautan dashboard Streamlit Cloud
```

## Setup Environment

### Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```bash
streamlit run dashboard.py
```

## Cara Menjalankan

### 1. Install Dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan Notebook Analisis
Buka `notebook.ipynb` di Jupyter Notebook, JupyterLab, atau Google Colab, lalu jalankan semua cell dari atas hingga bawah.

### 3. Jalankan Dashboard Streamlit
Masuk ke folder `dashboard` dan jalankan:
```bash
cd dashboard
streamlit run dashboard.py
```
Dashboard akan berakses di `http://localhost:8501`.

## Berkas Markdown (README.md)
Berkas README.md ini berisi panduan cara menjalankan dashboard dan analisis data. Langkah-langkahnya adalah:
1. Siapkan environment sesuai pilihan (Anaconda atau Shell/Terminal).
2. Install dependensi dengan `pip install -r requirements.txt`.
3. Jalankan semua cell di `notebook.ipynb` untuk melakukan proses analisis data dari awal hingga akhir, termasuk penyimpanan data bersih ke folder `dashboard/`.
4. Masuk ke folder `dashboard` dan jalankan `streamlit run dashboard.py` untuk membuka dashboard interaktif di browser.

---

## 📊 Hasil Analisis Detail

### 1. Gathering Data

Pada tahap ini, dua file dataset Bike Sharing dimuat ke dalam format DataFrame:

- **`day_df`** (dari `datasets/day.csv`): Berisi **731 baris** dan **16 kolom**, mencakup data agregat harian penyewaan sepeda selama 2 tahun penuh (1 Januari 2011 hingga 31 Desember 2012). Kolom utama yang relevan untuk analisis: `dteday`, `season`, `mnth`, `yr`, `weathersit`, `temp`, `atemp`, `hum`, `windspeed`, `casual`, `registered`, dan `cnt`.

- **`hour_df`** (dari `datasets/hour.csv`): Berisi **17.379 baris** dan **17 kolom** — sama seperti `day_df` ditambah kolom `hr` (jam 0–23). Dataset ini memiliki granularitas per jam yang sekitar 24× lebih detail dari `day_df`, sehingga sangat cocok untuk analisis pola penyewaan intra-harian dan identifikasi jam puncak.

Kedua dataset saling melengkapi: `day_df` digunakan untuk analisis musiman dan tahunan, sedangkan `hour_df` digunakan untuk analisis per jam dan perilaku pengguna berdasarkan waktu dalam sehari.

---

### 2. Data Wrangling

#### Assessing Data (Penilaian Kualitas Data)

Pada tahap assessing, ditemukan **3 permasalahan utama** pada masing-masing dataset (`day_df` dan `hour_df`):

| No | Permasalahan | Detail | Dampak Bisnis | Solusi |
|----|-------------|--------|---------------|--------|
| 1 | **Tipe data tidak sesuai** | Kolom `dteday` bertipe `object` (string), bukan `datetime64` | Tidak dapat dilakukan analisis time-series, grouping bulanan/musiman, atau perhitungan selisih tanggal | Konversi ke `datetime64` menggunakan `pd.to_datetime()` |
| 2 | **Kolom kategorik tersimpan sebagai integer** | Kolom `season`, `mnth`, `weathersit`, `holiday`, `workingday`, `weekday`, `yr` tersimpan sebagai `int64`, bukan label yang bermakna | Sulit untuk dibaca dan divisualisasikan; stakeholder tidak dapat langsung memahami nilai angka (misal: season=1 apakah musim semi atau dingin?) | Lakukan pemetaan label (value mapping) menjadi teks yang bermakna |
| 3 | **Nilai hum = 0** | Ditemukan nilai kelembapan = 0 yang tidak realistis secara fisik | Mengganggu analisis korelasi kelembapan terhadap penyewaan; bisa menghasilkan insight yang bias jika tidak ditangani | Verifikasi dan tandai sebagai anomali |

**Insight tambahan dari Assessing Data:**
- Tidak ada missing value maupun baris duplikat pada `day_df` dan `hour_df` — data lengkap dari segsi kelengkapan baris.
- Nilai `casual + registered == cnt` untuk **semua baris** — data konsisten secara logistik (total penyewaan selalu sama dengan jumlah casual ditambah registered).
- Rentang nilai numerik (`temp`, `atemp`, `hum`, `windspeed`) sudah dalam skala normalized (0–1) sesuai dokumentasi dataset.

#### Cleaning Data (Pembersihan Data)

Berdasarkan hasil assessing, dilakukan pembersihan sebagai berikut:

1. **Konversi tipe data `dteday` ke `datetime64`** pada kedua dataframe — siap untuk analisis time-series dan grouping berdasarkan waktu.
2. **Pemetaan label kolom kategorik** — ditambahkan kolom baru: `season_label`, `yr_label`, `mnth_label`, `weather_label`, `workingday_label`, `weekday_label`, `holiday_label`.
3. **Konversi skala ke satuan interpretatif** — `temp_celsius` (×41), `atemp_celsius` (×50), `hum_pct` (×100), `wind_ms` (×67) untuk memudahkan interpretasi oleh stakeholder bisnis.

**Insight setelah Cleaning Data:**
- Kedua dataset kini memiliki tipe data yang benar untuk semua kolom.
- Kolom label kategorik telah ditambahkan untuk memudahkan analisis dan visualisasi.
- Kolom suhu, kelembapan, dan kecepatan angin telah dikonversi ke satuan asli yang interpretatif.
- Data bersih: 0 missing value, 0 duplikasi, siap untuk tahap EDA.

---

### 3. Exploratory Data Analysis (EDA)

#### EDA 1: Analisis Temporal — Pola Penyewaan per Bulan dan Musim (2011–2012)

- Pola penyewaan sepeda menunjukkan **fluktuasi musiman yang sangat konsisten** selama 2011–2012. Penyewaan mencapai puncak di musim **Fall (Gugur)** dan **Summer (Panas)**, sedang terendah di musim **Winter (Dingin)** dan **Spring (Semi)**.
- Rata-rata penyewaan harian tertinggi terjadi di **bulan September (Fall)** dengan sekitar **5.644 sepeda/hari**, sedangkan terendah di **bulan Januari (Spring/Winter)** dengan sekitar **1.839 sepeda/hari** — selisih hingga **~3,1×** antara bulan terbaik dan terburuk.
- Terdapat pertumbuhan total penyewaan sekitar **+67%** dari tahun 2011 ke 2012, mengindikasikan adopsi layanan bike sharing yang terus meningkat dan potensi bisnis yang menjanjikan.

#### EDA 2: Analisis Perilaku Pengguna — Pola Per Jam dan Tipe Hari

- **Hari kerja** menunjukkan **pola bimodal** (dua puncak): pagi sekitar **08:00** (commute ke kantor) dan sore **17:00–18:00** (pulang kerja) — pola yang sangat khas bagi pengguna commuter.
- **Hari non-kerja** menunjukkan **pola unimodal** (satu puncak): siang hingga sore sekitar **12:00–15:00** — pola yang lebih berkaitan dengan aktivitas rekreasi dan liburan.
- Pengguna **registered** mendominasi penyewaan pada hari kerja (sekitar **80%+**), sementara pengguna **casual** relatif lebih tinggi pada hari non-kerja — menunjukkan bahwa registered adalah inti pelanggan harian, sementara casual adalah pelanggan sesekali/rekreasi.
- Rata-rata penyewaan per jam pada hari kerja cenderung lebih tinggi dari hari non-kerja pada jam puncak commuter, tetapi lebih rendah di luar jam puncak.

#### EDA 3: Analisis Pengaruh Cuaca terhadap Penyewaan

- Kondisi cuaca berpengaruh **sangat signifikan** terhadap jumlah penyewaan. Cuaca *Clear/Partly Cloudy* menghasilkan rata-rata penyewaan tertinggi (~**4.877 sepeda/hari**), sedangkan cuaca buruk (*Light Snow/Rain*) hanya ~**1.803 sepeda/hari** — penurunan hingga **~63%**.
- **Suhu (temp)** berkorelasi **positif kuat** (r ≈ **+0.63**) dengan jumlah penyewaan — pola hubungan berbentuk kurva, penyewaan optimal pada suhu **20–30°C**.
- **Kelembapan (hum)** berkorelasi **negatif** (r ≈ **-0.10**) dengan penyewaan — udara lembap cenderung mengurangi penyewaan, meski efeknya lebih lemah dibandingkan suhu.
- **Kecepatan angin** juga berkorelasi negatif namun sangat lemah dengan penyewaan.

---

### 4. Visualization & Explanatory Analysis

#### Visualisasi 1: Pola Temporal (Pertanyaan Bisnis 1)
- **Line chart**: Rata-rata penyewaan harian per bulan per tahun (2011 vs 2012) — menunjukkan pola kurva yang konsisten dengan puncak di September.
- **Bar chart**: Rata-rata penyewaan per musim — Fall tertinggi, diikuti Summer, Winter, dan Spring.

**Kesimpulan Visualisasi 1:**
- Penyewaan sepeda mengikuti **pola musiman yang konsisten** — meningkat dari Januari, mencapai puncak sekitar **September (Fall)**, kemudian menurun menjelang akhir tahun.
- Musim **Fall** memiliki rata-rata penyewaan harian tertinggi (~**5.644 sepeda/hari**), diikuti Summer, Winter, dan Spring sebagai terendah.
- Tahun **2012** secara konsisten menunjukkan jumlah penyewaan lebih tinggi dibandingkan 2011 di **setiap bulan**, mengindikasikan pertumbuhan bisnis yang sehat dan stabil sebesar sekitar **+67%** secara keseluruhan.

#### Visualisasi 2: Pola Per Jam (Pertanyaan Bisnis 2)
- **Line chart**: Rata-rata penyewaan per jam, membandingkan hari kerja vs hari non-kerja — menunjukkan pola bimodal vs unimodal.

**Kesimpulan Visualisasi 2:**
- Hari kerja memiliki pola **bimodal** (dua puncak): **08:00** (pagi, berangkat kerja) dan **17:00–18:00** (sore, pulang kerja) — sangat khas bagi pengguna commuter.
- Hari non-kerja memiliki pola **unimodal**: penyewaan mulai naik pagi dan mencapai puncak sekitar **12:00–15:00** — pola yang berkaitan dengan aktivitas rekreasi.
- Pengguna **registered** mendominasi sepanjang hari kerja, terutama pada jam puncak commuter, sementara pengguna **casual** lebih aktif pada siang hari dan akhir pekan.

#### Visualisasi 3: Pengaruh Cuaca (Pertanyaan Bisnis 3)
- **Bar horizontal**: Rata-rata penyewaan per kondisi cuaca — Clear/Partly Cloudy tertinggi, Light Snow/Rain terendah.
- **Scatter plot**: Suhu vs jumlah penyewaan — menunjukkan korelasi positif dengan pola kurva.

**Kesimpulan Visualisasi 3:**
- Kondisi cuaca **Clear/Partly Cloudy** menghasilkan rata-rata penyewaan paling tinggi (~**4.877 sepeda/hari**), sedangkan **Light Snow/Rain** paling rendah (~**1.803 sepeda/hari**) — penurunan hingga **~63%**.
- **Suhu** berkorelasi **positif kuat** (r ≈ **+0.63**) dengan penyewaan: pola hubungan berbentuk kurva, penyewaan optimal pada suhu **20–30°C**.
- **Kelembapan** berkorelasi **negatif** (r ≈ **-0.10**) dengan penyewaan: kelembapan tinggi cenderung mengurangi penyewaan, meski efeknya lebih lemah dibandingkan suhu.

---

### 5. Analisis Lanjutan: Clustering Manual (Binning)

Teknik **clustering manual menggunakan binning** diterapkan untuk mengelompokkan hari menjadi 4 tier permintaan berdasarkan jumlah penyewaan harian (`cnt`):

| Segmen | Rentang Penyewaan | Proporsi | Karakteristik |
|--------|-------------------|----------|---------------|
| **Low Demand** | < 2.000 | ~13% hari | Musim dingin, cuaca buruk (hujan/salju) |
| **Medium Demand** | 2.000–3.500 | Segmen menengah | Kondisi cuaca sedang, musim pergantian |
| **High Demand** | 3.500–5.500 | Segmen tinggi | Suhu hangat, cuaca cerah |
| **Very High Demand** | > 5.500 | ~30% hari | Musim Summer & Fall, suhu >20°C, cuaca cerah |

**Insight Clustering:**
- Segmen **Very High Demand** (~30% hari) didominasi oleh hari di musim **Summer** dan **Fall** dengan suhu hangat (>20°C) dan cuaca cerah — merupakan hari dengan permintaan tertinggi yang perlu prioritas armada.
- Segmen **Low Demand** (~13% hari) dominan terjadi di musim **Winter** dan **Spring** atau saat cuaca buruk (hujan/salju) — hari dengan permintaan rendah yang cocok untuk maintenance armada.
- **Spring** memiliki proporsi Low Demand tertinggi (~30%), sementara **Fall** memiliki proporsi Very High Demand tertinggi (~55%).

---

### 6. Conclusion & Recommendation

#### Kesimpulan

**Kesimpulan Pertanyaan 1 (Temporal Analysis):**
Penyewaan sepeda memiliki **pola musiman yang konsisten dan kuat** selama 2011–2012. Penyewaan tertinggi terjadi pada **musim Fall (Gugur)**, khususnya bulan **September–Oktober**, dengan rata-rata harian ~**5.644 sepeda**. Penyewaan terendah terjadi pada **musim Spring (Semi)** di bulan **Januari**, dengan rata-rata ~**1.839 sepeda/hari**. Terdapat pertumbuhan total penyewaan sekitar **+67%** dari 2011 ke 2012, mengindikasikan adopsi layanan bike sharing yang terus meningkat dan potensi ekspansi bisnis.

**Kesimpulan Pertanyaan 2 (User Behavior Analysis):**
Pola penggunaan per jam sangat berbeda antara hari kerja dan hari non-kerja. Pada hari kerja, penyewaan membentuk **pola bimodal** dengan puncak pada **08:00** (commute pagi) dan **17:00–18:00** (commute sore), didominasi oleh pengguna **registered** (~80%+). Pada hari non-kerja, penyewaan membentuk **pola unimodal** dengan puncak di **12:00–13:00**, lebih banyak digunakan untuk rekreasi dengan proporsi pengguna **casual** yang lebih tinggi. Perbedaan ini mencerminkan dua segmen pengguna dengan kebutuhan operasional yang berbeda.

**Kesimpulan Pertanyaan 3 (Weather Impact Analysis):**
Faktor cuaca berpengaruh signifikan terhadap jumlah penyewaan. Kondisi **Clear/Partly Cloudy** menghasilkan rata-rata penyewaan ~**4.877 sepeda/hari**, sedangkan **Light Snow/Rain** hanya ~**1.803 sepeda/hari** (penurunan ~**63%**). **Suhu** berkorelasi positif kuat (r ≈ +**0.63**) dengan penyewaan, optimal di kisaran **20–30°C**. **Kelembapan** berkorelasi negatif (r ≈ -**0.10**), namun efeknya lebih lemah dibandingkan suhu. Cuaca adalah faktor eksternal kunci yang harus dipertimbangkan dalam perencanaan operasional.

**Kesimpulan Analisis Lanjutan (Clustering):**
Segmentasi hari ke dalam 4 tier permintaan (Low, Medium, High, Very High Demand) mengungkapkan bahwa hari dengan **Very High Demand** (~30% hari) selalu bertepatan dengan kombinasi suhu hangat (>20°C), cuaca cerah, dan musim Summer/Fall. Hari **Low Demand** (~13% hari) dominan terjadi di musim dingin dan saat cuaca buruk. Segmentasi ini memberikan kerangka kerja untuk pengambilan keputusan operasional berbasis data.

#### Rekomendasi Action Item

**1. Optimasi Armada Berbasis Musim (Seasonal Fleet Management)**
- **Tingkatkan** ketersediaan armada sepeda sebesar **30–40%** selama **musim Fall (Agustus–Oktober)** saat permintaan paling tinggi.
- **Kurangi** operasional dan jadwalkan maintenance besar pada musim **Winter–Spring (Desember–Maret)** saat permintaan rendah, untuk efisiensi biaya operasional.

**2. Redistribusi Sepeda Berbasis Pola Per Jam (Dynamic Rebalancing)**
- Implementasikan sistem **rebalancing otomatis** sebelum jam puncak hari kerja: pastikan stasiun terisi penuh sebelum pukul **07:30** dan **16:30** untuk menanggulangi lonjakan commuter.
- Untuk hari non-kerja, prioritas pengisian stasiun di area **rekreasi/wisata** antara pukul **10:00–14:00** saat puncak penyewaan casual terjadi.

**3. Program Promosi Berbasis Cuaca (Weather-Triggered Promotions)**
- Buat sistem notifikasi otomatis ke pengguna **casual** saat prakiraan cuaca **cerah dan suhu 20–28°C**, menawarkan diskon atau reward untuk mendorong penggunaan.
- Siapkan **opsi asuransi perjalanan atau pengembalian gratis** saat cuaca buruk (hujan/salju) terjadi mendadak, untuk meningkatkan kepercayaan dan retensi pengguna.

**4. Program Konversi Casual ke Registered**
- Fokuskan kampanye konversi pada **hari non-kerja** saat proporsi pengguna casual meningkat.
- Tawarkan **trial membership 30 hari** dengan harga spesial khususnya di musim **Summer dan Fall**, karena pengguna casual lebih aktif di bulan-bulan tersebut.

**5. Sistem Prediksi Permintaan Berbasis Cuaca dan Musim**
- Integrasikan data prakiraan cuaca API ke sistem manajemen operasional untuk mengantisipasi hari-hari **Very High Demand** vs **Low Demand** secara real-time.
- Gunakan segmentasi tier (Low/Medium/High/Very High) sebagai dasar **SOP (Standard Operating Procedure)** distribusi armada harian dan pengaturan stasiun.

---

## Author
**Rio Andika Andriansyah**  
Email: andikario0101@gmail.com  
ID Dicoding: rioandikaa01
