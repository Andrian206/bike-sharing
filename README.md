# Proyek Analisis Data: Bike Sharing Dataset

## Deskripsi Proyek

Proyek ini merupakan submission akhir untuk kelas Belajar Fundamental Analisis Data di Dicoding. Proyek ini menganalisis data penyewaan sepeda (Bike Sharing Dataset) dari tahun 2011-2012 di Washington D.C., USA.

Dataset yang digunakan: Bike Sharing Dataset (Hadi Fanaee-T, University of Porto)

## Struktur Direktori

```
submission/
├── dashboard/
│   ├── dashboard.py           # Aplikasi dashboard Streamlit
│   ├── day_data.csv           # Data bersih harian (731 baris, 27 kolom)
│   └── hour_data.csv          # Data bersih per jam (17.379 baris, 28 kolom)
├── datasets/
│   ├── day.csv                # Data agregat harian asli (731 baris)
│   ├── hour.csv               # Data per jam asli (17.379 baris)
│   └── Readme.txt             # Dokumentasi dataset asli
├── notebook.ipynb             # Notebook analisis data lengkap
├── README.md                  # Dokumentasi proyek lengkap
├── requirements.txt           # Daftar dependensi Python
├── url.txt                    # Tautan dashboard Streamlit Community Cloud
├── plot_clustering.png        # Visualisasi hasil clustering
├── plot_heatmap_season_tier.png   # Visualisasi heatmap season & tier
├── plot_temporal_analysis.png     # Visualisasi analisis temporal
├── plot_user_behavior.png         # Visualisasi perilaku pengguna
└── plot_weather_impact.png        # Visualisasi pengaruh cuaca
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

### Run Streamlit App

```bash
cd dashboard
streamlit run dashboard.py
```

## Deploy ke Streamlit Community Cloud

Ikuti langkah berikut untuk mendeploy dashboard ke Streamlit Community Cloud:

### 1. Push kode ke GitHub

Pastikan seluruh file proyek (termasuk folder dashboard/, requirements.txt, dan url.txt) telah di-push ke repository GitHub.

### 2. Buka Streamlit Community Cloud

Kunjungi https://share.streamlit.io dan login menggunakan akun GitHub Anda.

### 3. Buat Aplikasi Baru

Klik tombol "New app", lalu atur konfigurasi:
- Repository: repository proyek Anda
- Branch: main (atau branch utama Anda)
- Main file path: dashboard/dashboard.py

### 4. Deploy

Klik tombol "Deploy". Streamlit akan otomatis memasang dependensi dari requirements.txt.

### 5. Akses Dashboard

Setelah deployment selesai, dashboard dapat diakses publik melalui URL yang diberikan Streamlit Cloud, misalnya:
https://bike-sharing-rioandikaa01.streamlit.app/
## Hasil Analisis Detail

### 1. Gathering Data

Pada tahap ini, dua file dataset Bike Sharing dimuat ke dalam DataFrame Pandas:

- **day_df** (dari datasets/day.csv): Berisi 731 baris dan 16 kolom, mencakup data agregat harian penyewaan sepeda selama 2 tahun penuh (1 Januari 2011 hingga 31 Desember 2012).
- **hour_df** (dari datasets/hour.csv): Berisi 17.379 baris dan 17 kolom (memiliki tambahan kolom hr jam 0-23). Granularitas per jam ini digunakan untuk identifikasi perilaku jam sibuk intra-harian.

### 2. Data Wrangling

#### Assessing Data (Penilaian Kualitas Data)

Ditemukan permasalahan kualitas data yang langsung ditangani:

- **Tipe data dteday bertipe object (string)**: Dikonversi menjadi datetime64 agar memungkinkan ekstraksi fitur temporal dan manipulasi time-series.
- **Kolom kategorik tersimpan sebagai kode integer**: Kolom seperti season, mnth, weathersit, workingday, dan yr belum memiliki label deskriptif.
- **Variabel numerik dalam format ternormalisasi**: Kolom cuaca (temp, atemp, hum, windspeed) masih berada dalam rentang 0-1, membutuhkan denormalisasi ke satuan riil agar memiliki nilai interpretasi bisnis.

**Catatan Integritas Data**: Tidak ditemukan missing values maupun baris duplikat. Konsistensi logis terpenuhi di mana casual + registered == cnt pada seluruh baris.

#### Cleaning Data (Pembersihan Data)

- Konversi dteday ke tipe datetime64[ns].
- Pemetaan kolom kategorik menjadi label teks representatif: season_label, yr_label, mnth_label, weather_label, dan workingday_label.
- Denormalisasi variabel kontinu ke satuan metrik:
  - temp_celsius = temp x 41
  - atemp_celsius = atemp x 50
  - hum_pct = hum x 100
  - wind_ms = windspeed x 67 (km/jam atau m/s terkonversi)

### 3. Exploratory Data Analysis (EDA)

#### EDA 1: Analisis Temporal - Pola Bulanan dan Musiman

- **Pola Musiman**: Rata-rata sewa harian tertinggi diraih oleh musim Fall (Gugur) sebesar 5.644 unit/hari, diikuti Summer (4.992 unit/hari) dan Winter (4.728 unit/hari). Musim Spring (Semi) terendah dengan rata-rata 2.604 unit/hari (terpaut penurunan lebih dari 53% dibanding Fall).
- **Pola Bulanan**: Titik terendah konsisten di bulan Januari (1.232 unit/hari pada 2011; 3.121 unit/hari pada 2012). Puncak sewa terjadi pada pertengahan hingga akhir tahun (Juni 2011: 4.784 unit/hari dan September 2012: 7.286 unit/hari).
- **Pertumbuhan Bisnis**: Total penyewaan melonjak 64,9% dari 1.243.103 sewa (2011) menjadi 2.049.576 sewa (2012).

#### EDA 2: Analisis Perilaku Pengguna - Jam Sibuk Hari Kerja vs Non-Kerja

- **Hari Kerja (Bimodal)**: Memiliki 2 puncak jam sibuk komuter tajam pada pukul 08:00 (477,0 unit/jam) dan pukul 17:00-18:00 (puncak tertinggi 525,3 unit/jam). Pengguna didominasi mutlak oleh segmen terdaftar (Registered: 86,7%).
- **Hari Non-Kerja (Unimodal)**: Memiliki kurva tunggal landai khas rekreasi yang memuncak pada pukul 13:00 (372,7 unit/jam) dan stabil aktif antara pukul 11:00-16:00. Porsi pengguna kasual (Casual) meningkat lebih dari 2x lipat hingga mencapai 31,6%.

#### EDA 3: Analisis Pengaruh Cuaca terhadap Penyewaan

- **Kondisi Cuaca**: Kondisi cerah (Clear/Partly Cloudy) membukukan rata-rata sewa 4.877 unit/hari, kabut/berawan (Mist/Cloudy) menghasilkan 4.036 unit/hari, dan cuaca hujan/salju (Light Snow/Rain) anjlok drastis ke 1.803 unit/hari (penurunan masif sekitar 63,0%).
- **Korelasi Suhu & Angin**: Suhu (temp dan atemp) berkorelasi positif kuat (r = +0,63) dengan sweet spot di rentang 20-30 derajat C (puncak 5.726 unit/hari pada 25-30 derajat C). Kecepatan angin berkorelasi negatif moderat-rendah (r = -0,235), sedangkan kelembapan berkorelasi negatif lemah (r = -0,101).

### 4. Visualization & Explanatory Analysis

#### Visualisasi 1: Pola Temporal (Pertanyaan Bisnis 1)

Line chart & Bar chart: Menunjukkan garis 2012 yang selalu berada di atas 2011 di seluruh bulan, membuktikan tren pertumbuhan tahunan yang solid (+64,9%), dengan musim Fall sebagai kontributor sewa tertinggi (5.644 unit/hari).

#### Visualisasi 2: Pola Per Jam (Pertanyaan Bisnis 2)

Hourly Plot & Stacked Area: Mempertegas profil komuter harian. Grafik area membuktikan secara visual bahwa lonjakan jam 08:00 dan 17:00-18:00 hampir seluruhnya digerakkan oleh pengguna Registered, sedangkan pengguna Casual lebih dominan di siang akhir pekan.

#### Visualisasi 3: Pengaruh Cuaca (Pertanyaan Bisnis 3)

Bar Plot & Non-Linear Scatter Plot: Menunjukkan penurunan drastis 63% pada cuaca buruk (Snow/Rain) serta kurva polinomial suhu yang melandai/berbalik sedikit turun saat suhu melampaui 30 derajat C.

### 5. Analisis Lanjutan: Clustering Manual (Binning)

Penerapan manual binning pada 731 hari ke dalam 4 tingkatan permintaan (Demand Tier):

| Segmen Permintaan | Rentang Sewa (cnt) | Jumlah Hari | Porsi Hari (%) | Rata-rata Sewa | Rata-rata Suhu | Peluang Cuaca Baik |
|-------------------|-------------------|-------------|----------------|----------------|----------------|-------------------|
| Low Demand | < 2.000 | 98 hari | 13,4% | 1.395 unit/hari | 11,1°C | 45,0% |
| Medium Demand | 2.000-3.500 | 121 hari | 16,6% | 2.785 unit/hari | 14,9°C | 54,0% |
| High Demand | 3.500-5.500 | 289 hari | 39,5% | 4.505 unit/hari | 22,3°C | 64,0% |
| Very High Demand | > 5.500 | 223 hari | 30,5% | 6.803 unit/hari | 24,8°C | 76,0% |

**Insight Distribusi Silang Musim (Cross-Tabulation Heatmap)**:

- Musim Fall memiliki performa terbaik di mana 96,3% hari berada di tier permintaan tinggi (48,4% Very High dan 47,9% High).
- Musim Spring adalah musim terlemah di mana 75,6% hari berada di tier rendah (43,6% Low dan 32,0% Medium).
- Secara keseluruhan, sebanyak 70,0% hari operasional (High + Very High) berada pada level permintaan tinggi.

### 6. Conclusion & Recommendation

#### Kesimpulan

1. **Pola Temporal**: Penyewaan sepeda berfluktuasi secara teratur mengikuti musim (puncak di Fall: 5.644 sepeda/hari; terendah di Spring: 2.604 sepeda/hari) dan didukung pertumbuhan tahunan konsisten sebesar +64,9% dari 2011 ke 2012.

2. **Perilaku Pengguna**: Pola sewa hari kerja bersifat bimodal komuter (puncak 08:00 dan 17:00-18:00) yang digerakkan oleh 86,7% pengguna Registered. Hari libur bersifat unimodal santai (puncak 13:00) dengan kontribusi pengguna Casual naik menjadi 31,6%.

3. **Pengaruh Cuaca**: Kondisi cuaca hujan/salju memangkas penyewaan hingga 63,0%. Suhu berkorelasi positif kuat (r = +0,63) dengan tingkat kenyamanan optimal di rentang 20-30 derajat C, sementara angin kencang menurunkan minat bersepeda (r = -0,235).

4. **Segmentasi Hari**: Sebanyak 70,0% hari operasional berada di level High hingga Very High Demand, yang didominasi oleh musim panas/gugur, suhu hangat (lebih dari 22 derajat C), dan hari kerja komuter.

#### Rekomendasi Action Item

1. **Manajemen Armada Berbasis Musim**: Maksimalkan ketersediaan 100% armada pada musim Summer-Fall (Mei-Oktober), dan gunakan periode low-demand pada musim dingin (Desember-Februari) untuk perawatan besar unit (overhaul).

2. **Redistribusi Dinamis Berbasis Jam**:
   - Hari Kerja: Pastikan ketersediaan stok di area permukiman sebelum 07:00 pagi dan kosongkan dermaga di area perkantoran sebelum 16:00 sore.
   - Hari Libur: Pusatkan armada di dekat taman kota dan lokasi rekreasi mulai pukul 10:00-15:00.

3. **Pemasaran Berbasis Cuaca (Weather-Triggered)**: Kirimkan penawaran rute rekreasi otomatis saat suhu 20-30 derajat C dan cuaca cerah. Tawarkan perlindungan pembatalan gratis saat hujan mendadak untuk menjaga retensi pengguna kasual.

4. **Konversi Kasual ke Pelanggan Terdaftar**: Tawarkan promosi weekend pass dan diskon langganan bulanan di akhir pekan pada stasiun rekreasi saat keterlibatan pengguna Casual sedang berada di puncak (31,6%).

5. **Implementasi SOP Berbasis Prediksi Permintaan**: Gunakan hasil integrasi API cuaca untuk membagi kesiapan tim operasional: status Siaga Penuh pada hari berprediksi Very High Demand (lebih dari 5.500 sewa), dan status Efisiensi Biaya/Servis Unit pada hari berprediksi Low Demand (kurang dari 2.000 sewa).

## Author

**Rio Andika Andriansyah**
- Email: andikario0101@gmail.com
- ID Dicoding: rioandikaa01