import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100

MONTH_NAMES_ID = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun',
    7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'
}


@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "day_data.csv")
    df = pd.read_csv(csv_path)
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['yr_label'] = df['yr_label'].astype(str)
    return df


@st.cache_data
def load_hour_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "hour_data.csv")
    hour_df = pd.read_csv(csv_path)
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    hour_df['yr_label'] = hour_df['yr_label'].astype(str)
    return hour_df


def format_md(month_day_tuple):
    m, d = month_day_tuple
    return f"{d} {MONTH_NAMES_ID[m]}"


def calculate_growth_metric(df_filtered, start_date, end_date):
    """
    Menghitung pertumbuhan total penyewaan antara dua periode kalender yang setara
    di dalam rentang tanggal yang dipilih.

    Returns:
        tuple: (label_text, value_str, delta_str, caption_str)
    """
    if df_filtered.empty:
        return (
            "Pertumbuhan (YoY)",
            "N/A",
            None,
            "Tidak ada data untuk rentang yang dipilih"
        )

    years_available = sorted(df_filtered['dteday'].dt.year.unique())
    if len(years_available) < 2:
        return (
            "Pertumbuhan (YoY)",
            "N/A",
            None,
            "Perbandingan belum tersedia"
        )

    year_first = int(years_available[0])
    year_last = int(years_available[-1])

    # Tentukan rentang tanggal yang ter-cover di masing-masing tahun berdasarkan filter date_range
    y1_start = max(start_date, pd.Timestamp(year=year_first, month=1, day=1))
    y1_end = min(end_date, pd.Timestamp(year=year_first, month=12, day=31))

    y2_start = max(start_date, pd.Timestamp(year=year_last, month=1, day=1))
    y2_end = min(end_date, pd.Timestamp(year=year_last, month=12, day=31))

    # Hitung irisan periode kalender (bulan, hari) yang setara di kedua tahun
    overlap_start = max((y1_start.month, y1_start.day), (y2_start.month, y2_start.day))
    overlap_end = min((y1_end.month, y1_end.day), (y2_end.month, y2_end.day))

    if overlap_start > overlap_end:
        return (
            f"Pertumbuhan ({year_last} vs {year_first})",
            "N/A",
            None,
            "Perbandingan belum tersedia (tidak ada periode setara)"
        )

    # Filter baris dalam periode kalender setara tanpa terkendala tahun kabisat (29 Feb)
    md_tuples = list(zip(df_filtered['dteday'].dt.month, df_filtered['dteday'].dt.day))
    in_overlap = pd.Series(
        [(overlap_start <= md <= overlap_end) for md in md_tuples],
        index=df_filtered.index
    )

    df_first_period = df_filtered[(df_filtered['dteday'].dt.year == year_first) & in_overlap]
    df_last_period = df_filtered[(df_filtered['dteday'].dt.year == year_last) & in_overlap]

    if df_first_period.empty or df_last_period.empty:
        return (
            f"Pertumbuhan ({year_last} vs {year_first})",
            "N/A",
            None,
            "Perbandingan belum tersedia"
        )

    total_first = df_first_period['cnt'].sum()
    total_last = df_last_period['cnt'].sum()

    if total_first == 0:
        return (
            f"Pertumbuhan ({year_last} vs {year_first})",
            "N/A",
            None,
            "Perbandingan belum tersedia"
        )

    growth_pct = ((total_last - total_first) / total_first) * 100
    diff_units = int(total_last - total_first)

    start_str = format_md(overlap_start)
    end_str = format_md(overlap_end)

    label_text = f"Pertumbuhan ({year_last} vs {year_first})"
    value_str = f"{growth_pct:+.1f}%"
    delta_str = f"{diff_units:+,} penyewaan"
    caption_str = f"Periode: {start_str}–{end_str} {year_last} vs {start_str}–{end_str} {year_first}"

    return label_text, value_str, delta_str, caption_str


# Load Data
df = load_data()
hour_df = load_hour_data()

# Sidebar Filter (tanpa filter tahun yang redundan)
st.sidebar.title("🚲 Bike Sharing")
st.sidebar.markdown("### Filter Data")

season_options = ['Spring', 'Summer', 'Fall', 'Winter']
available_seasons = [s for s in season_options if s in df['season_label'].unique()]
season_selected = st.sidebar.multiselect(
    "Pilih Musim:",
    options=available_seasons,
    default=available_seasons
)

date_min = df['dteday'].min().date()
date_max = df['dteday'].max().date()
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal:",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max
)

weather_options = sorted(df['weather_label'].unique())
weather_selected = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca:",
    options=weather_options,
    default=weather_options
)

# Penanganan input rentang tanggal (1 tanggal vs 2 tanggal)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    start_date = pd.to_datetime(date_range[0])
    end_date = start_date
    st.sidebar.info("Pilih tanggal akhir untuk melengkapi rentang analisis.")
else:
    start_date = pd.to_datetime(date_min)
    end_date = pd.to_datetime(date_max)

# Terapkan filter pada df dan hour_df
mask = (
    df['season_label'].isin(season_selected) &
    df['weather_label'].isin(weather_selected) &
    (df['dteday'] >= start_date) &
    (df['dteday'] <= end_date)
)
df_filtered = df[mask]

hour_mask = (
    hour_df['season_label'].isin(season_selected) &
    hour_df['weather_label'].isin(weather_selected) &
    (hour_df['dteday'] >= start_date) &
    (hour_df['dteday'] <= end_date)
)
hour_filtered = hour_df[hour_mask]

# Header Dashboard
st.title("🚲 Bike Sharing Data Analysis Dashboard")
st.markdown("""
Dashboard ini menyajikan hasil analisis data penyewaan sepeda berdasarkan 
**Bike Sharing Dataset** (2011–2012, Washington D.C.). 
Gunakan filter di sidebar untuk menyesuaikan periode tanggal, musim, dan kondisi cuaca.
""")
st.divider()

# Ringkasan Metrik (KPI)
st.subheader("Ringkasan Metrik")
col1, col2, col3, col4 = st.columns(4)

if df_filtered.empty:
    with col1:
        st.metric("Total Penyewaan", "0")
    with col2:
        st.metric("Rata-rata Harian", "0")
    with col3:
        st.metric("Penyewaan Tertinggi per Hari", "0")
    with col4:
        label_text, value_str, delta_str, caption_str = calculate_growth_metric(
            df_filtered, start_date, end_date
        )
        st.metric(label_text, value_str)
        st.caption(caption_str)

    st.warning("Tidak ada data untuk rentang yang dipilih. Silakan sesuaikan filter di sidebar.")
    st.stop()

with col1:
    total_rentals = int(df_filtered['cnt'].sum())
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    avg_daily = df_filtered['cnt'].mean()
    st.metric("Rata-rata Harian", f"{avg_daily:,.0f}")

with col3:
    max_daily = int(df_filtered['cnt'].max())
    st.metric("Penyewaan Tertinggi per Hari", f"{max_daily:,}")

with col4:
    label_text, value_str, delta_str, caption_str = calculate_growth_metric(
        df_filtered, start_date, end_date
    )
    st.metric(label_text, value_str, delta=delta_str)
    st.caption(caption_str)

st.divider()

# Visualisasi 1: Pola Temporal
st.subheader("Pola Penyewaan per Bulan dan Musim (2011–2012)")
st.markdown("""
**Pertanyaan Bisnis 1:** Bagaimana pola rata-rata jumlah penyewaan sepeda harian 
berdasarkan bulan dan musim selama periode 2011–2012?
""")

monthly_avg = (
    df_filtered.groupby(['yr_label', 'mnth', 'mnth_label'])['cnt']
    .mean()
    .reset_index()
    .sort_values('mnth')
)

fig1, axes = plt.subplots(1, 2, figsize=(14, 5))
fig1.suptitle('Pola Temporal Penyewaan Sepeda (2011–2012)', fontsize=14, fontweight='bold', y=1.02)

ax1 = axes[0]
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
colors_yr = {'2011': '#4C72B0', '2012': '#DD8452'}

for yr, grp in monthly_avg.groupby('yr_label'):
    ax1.plot(
        grp['mnth'], grp['cnt'],
        marker='o', linewidth=2.5, markersize=6,
        color=colors_yr.get(str(yr), '#333333'), label=str(yr)
    )

ax1.set_title('Rata-rata Penyewaan Harian per Bulan', fontsize=12, fontweight='bold')
ax1.set_xlabel('Bulan', fontsize=10)
ax1.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=10)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(month_order, rotation=45)
ax1.legend(title='Tahun', fontsize=9)
ax1.grid(True, alpha=0.4)

ax2 = axes[1]
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_avg = (
    df_filtered.groupby('season_label')['cnt']
    .mean()
    .reindex(season_order)
    .dropna()
)
season_color_map = {
    'Spring': '#55A868',
    'Summer': '#CCB974',
    'Fall': '#C44E52',
    'Winter': '#8172B3'
}
colors_season = [season_color_map[s] for s in season_avg.index]
bars = ax2.bar(season_avg.index, season_avg.values, color=colors_season, edgecolor='white', linewidth=1)
for bar, val in zip(bars, season_avg.values):
    ax2.text(bar.get_x() + bar.get_width() / 2, val + 50, f'{val:,.0f}',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax2.set_title('Rata-rata Penyewaan per Musim', fontsize=12, fontweight='bold')
ax2.set_xlabel('Musim', fontsize=10)
ax2.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=10)
ax2.grid(True, axis='y', alpha=0.4)

plt.tight_layout()
st.pyplot(fig1)
plt.close(fig1)

if not season_avg.empty:
    peak_season = season_avg.idxmax()
    peak_val = season_avg.max()
    low_season = season_avg.idxmin()
    low_val = season_avg.min()
    st.info(f"""
**Kesimpulan:** Penyewaan sepeda menunjukkan pola musiman yang konsisten. 
Musim **{peak_season}** memiliki rata-rata penyewaan harian tertinggi (**{peak_val:,.0f} sepeda/hari**), 
sedangkan musim **{low_season}** terendah (**{low_val:,.0f} sepeda/hari**). 
Pola ini menjadi dasar penting dalam perencanaan kapasitas armada sepeda secara musiman.
""")

st.divider()

# Visualisasi 2: Pola Per Jam
st.subheader("Pola Penyewaan per Jam: Hari Kerja vs Non-Kerja")
st.markdown("""
**Pertanyaan Bisnis 2:** Bagaimana perbedaan pola penyewaan sepeda per jam antara 
hari kerja dan hari non-kerja?
""")

if hour_filtered.empty:
    st.warning("Tidak ada data per jam untuk rentang dan filter yang dipilih.")
else:
    hourly_avg = (
        hour_filtered.groupby(['hr', 'workingday_label'])['cnt']
        .mean()
        .reset_index()
        .sort_values('hr')
    )
    hourly_pivot = hourly_avg.pivot(index='hr', columns='workingday_label', values='cnt').fillna(0)

    fig2, ax = plt.subplots(figsize=(14, 5))

    has_work = 'Yes' in hourly_pivot.columns
    has_nowrk = 'No' in hourly_pivot.columns
    max_y = hourly_pivot.values.max() if hourly_pivot.size > 0 else 1

    if has_work:
        work_data = hourly_pivot['Yes']
        ax.plot(hourly_pivot.index, work_data, marker='o', linewidth=2.5, markersize=5,
                color='#4C72B0', label='Hari Kerja')
        ax.fill_between(hourly_pivot.index, work_data, alpha=0.25, color='#4C72B0')

        peak_work_hr = work_data.idxmax()
        peak_work_val = work_data.max()
        ax.annotate(
            f'Puncak Kerja\n{int(peak_work_hr):02d}:00\n{peak_work_val:,.0f}',
            xy=(peak_work_hr, peak_work_val),
            xytext=(peak_work_hr, peak_work_val + max_y * 0.12),
            ha='center', fontsize=9, color='#4C72B0', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#4C72B0', lw=1.5)
        )

    if has_nowrk:
        nowrk_data = hourly_pivot['No']
        ax.plot(hourly_pivot.index, nowrk_data, marker='o', linewidth=2.5, markersize=5,
                color='#C44E52', label='Hari Non-Kerja')
        ax.fill_between(hourly_pivot.index, nowrk_data, alpha=0.25, color='#C44E52')

        peak_nowrk_hr = nowrk_data.idxmax()
        peak_nowrk_val = nowrk_data.max()
        ax.annotate(
            f'Puncak Non-Kerja\n{int(peak_nowrk_hr):02d}:00\n{peak_nowrk_val:,.0f}',
            xy=(peak_nowrk_hr, peak_nowrk_val),
            xytext=(peak_nowrk_hr, peak_nowrk_val + max_y * 0.12),
            ha='center', fontsize=9, color='#C44E52', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#C44E52', lw=1.5)
        )

    ax.set_ylim(0, max_y * 1.28)
    ax.set_title('Rata-rata Penyewaan per Jam: Hari Kerja vs Non-Kerja', fontsize=13, fontweight='bold')
    ax.set_xlabel('Jam (00:00–23:00)', fontsize=11)
    ax.set_ylabel('Rata-rata Jumlah Penyewaan per Jam', fontsize=11)
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24)], rotation=45)
    ax.legend(title='Tipe Hari', fontsize=10)
    ax.grid(True, alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    col_hour1, col_hour2, col_hour3 = st.columns(3)
    with col_hour1:
        if has_work:
            st.metric("Jam Puncak Hari Kerja", f"{int(work_data.idxmax()):02d}:00", f"{work_data.max():,.0f} sepeda/jam")
        else:
            st.metric("Jam Puncak Hari Kerja", "N/A")
    with col_hour2:
        if has_nowrk:
            st.metric("Jam Puncak Non-Kerja", f"{int(nowrk_data.idxmax()):02d}:00", f"{nowrk_data.max():,.0f} sepeda/jam")
        else:
            st.metric("Jam Puncak Non-Kerja", "N/A")
    with col_hour3:
        total_hourly = int(hour_filtered['cnt'].sum())
        st.metric("Total Penyewaan (Data Per Jam)", f"{total_hourly:,}")

    st.info("""
**Kesimpulan:** Hari kerja membentuk **pola bimodal** (dua puncak tajam): pagi pukul **08:00** dan sore **17:00–18:00** 
yang digerakkan oleh komuter pengguna terdaftar (*Registered*). Sebaliknya, hari non-kerja membentuk **pola unimodal** 
dengan puncak siang sekitar **12:00–14:00** (puncak 13:00) untuk aktivitas rekreasi.
""")

st.divider()

# Visualisasi 3: Pengaruh Cuaca
st.subheader("Pengaruh Cuaca terhadap Penyewaan")
st.markdown("""
**Pertanyaan Bisnis 3:** Bagaimana pengaruh kondisi cuaca dan suhu terhadap jumlah 
penyewaan sepeda?
""")

weather_avg = (
    df_filtered.groupby('weather_label')['cnt']
    .mean()
    .sort_values(ascending=False)
)

fig3, axes = plt.subplots(1, 2, figsize=(14, 5))
fig3.suptitle('Pengaruh Faktor Cuaca terhadap Penyewaan Sepeda', fontsize=14, fontweight='bold', y=1.02)

ax1 = axes[0]
weather_order_plot = ['Clear/Partly Cloudy', 'Mist/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Snow']
weather_plot = weather_avg.reindex([w for w in weather_order_plot if w in weather_avg.index])
weather_color_map = {
    'Clear/Partly Cloudy': '#55A868',
    'Mist/Cloudy': '#CCB974',
    'Light Snow/Rain': '#C44E52',
    'Heavy Rain/Snow': '#8172B3'
}
colors_w = [weather_color_map.get(w, '#4C72B0') for w in weather_plot.index]

bars = ax1.barh(weather_plot.index, weather_plot.values, color=colors_w, edgecolor='white', linewidth=1, height=0.6)
for bar, val in zip(bars, weather_plot.values):
    ax1.text(val + 50, bar.get_y() + bar.get_height() / 2, f'{val:,.0f}',
             va='center', fontsize=9, fontweight='bold')
ax1.set_xlim(0, weather_plot.max() * 1.15 if not weather_plot.empty else 1)
ax1.set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=12, fontweight='bold')
ax1.set_xlabel('Rata-rata Penyewaan Harian', fontsize=10)
ax1.grid(True, axis='x', alpha=0.4)

ax2 = axes[1]
ax2.scatter(df_filtered['temp_celsius'], df_filtered['cnt'], alpha=0.5, s=20, color='#4C72B0')
ax2.set_title('Suhu vs Jumlah Penyewaan', fontsize=12, fontweight='bold')
ax2.set_xlabel('Suhu (°C)', fontsize=10)
ax2.set_ylabel('Jumlah Penyewaan', fontsize=10)
ax2.grid(True, alpha=0.4)

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

if not weather_avg.empty:
    best_weather = weather_avg.idxmax()
    best_weather_val = weather_avg.max()
    worst_weather = weather_avg.idxmin()
    worst_weather_val = weather_avg.min()
    st.info(f"""
**Kesimpulan:** Kondisi cuaca **{best_weather}** menghasilkan rata-rata penyewaan 
tertinggi (**{best_weather_val:,.0f} sepeda/hari**), sedangkan **{worst_weather}** terendah 
(**{worst_weather_val:,.0f} sepeda/hari**). Suhu optimum untuk bersepeda berada pada rentang **20–30°C**.
""")

st.divider()

# Tabel Data Detail
st.subheader("Data Detail")
st.markdown(f"Menampilkan **{len(df_filtered)}** baris data setelah difilter.")
st.dataframe(df_filtered, use_container_width=True, height=400)

st.divider()

# Kesimpulan & Rekomendasi Utama (Selaras dengan Hasil Analisis EDA)
st.subheader("Kesimpulan & Rekomendasi")

st.markdown("""
### Kesimpulan Utama
1. **Pola Temporal & Pertumbuhan:** Penyewaan tertinggi terjadi pada musim **Fall** (rata-rata **5.644 sepeda/hari**) dan terendah pada musim **Spring** (rata-rata **2.604 sepeda/hari**). Secara tahunan, bisnis bertumbuh pesat sebesar **+64,9%** dari tahun 2011 ke 2012.
2. **Perilaku Pengguna per Jam:** Hari kerja membentuk pola **bimodal** komuter dengan puncak pukul **08:00 (477 unit/jam)** dan **17:00 (525 unit/jam)** yang didominasi oleh **86,7% pengguna Registered**. Hari non-kerja membentuk pola **unimodal** rekreasi dengan puncak pukul **13:00 (373 unit/jam)** dan proporsi pengguna **Casual** melonjak hingga **31,6%**.
3. **Pengaruh Cuaca:** Kondisi cerah (*Clear/Partly Cloudy*) menghasilkan rata-rata **4.877 sepeda/hari**, sedangkan hujan/salju (*Light Snow/Rain*) turun **~63,0%** menjadi **1.803 sepeda/hari**. Suhu berkorelasi positif kuat (**r = +0,63**) dengan zona nyaman di rentang **20–30°C**.

### Rekomendasi Action Item
1. **Manajemen Armada Berbasis Musim:** Siagakan 100% kapasitas armada pada musim Summer–Fall (Mei–Oktober), dan jadwalkan perawatan besar (*overhaul*) unit pada musim dingin/low-demand (Desember–Februari).
2. **Redistribusi Dinamis (Rebalancing SOP):** Pasok stasiun permukiman sebelum **07:00 pagi** dan kosongkan dermaga perkantoran sebelum **16:00 sore** pada hari kerja. Untuk akhir pekan, fokuskan armada di area wisata pada pukul **10:00–15:00**.
3. **Promosi Berbasis Cuaca:** Kirimkan notifikasi promosi rute rekreasi otomatis ke pengguna kasual saat prakiraan cuaca cerah di suhu **20–30°C**, serta berikan insentif proteksi hujan untuk menjaga retensi pengguna.
4. **Konversi Casual ke Registered:** Luncurkan promo *weekend pass* dan diskon paket langganan bulanan di stasiun wisata saat porsi pengguna kasual sedang tinggi di akhir pekan.
""")

st.divider()
st.markdown("*Dashboard dibuat untuk proyek analisis data Dicoding — Belajar Fundamental Analisis Data.*")