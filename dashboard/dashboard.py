import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100

@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "day_data.csv")
    df = pd.read_csv(csv_path)
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df


@st.cache_data
def load_hour_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "hour_data.csv")
    hour_df = pd.read_csv(csv_path)
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return hour_df


df = load_data()
hour_df = load_hour_data()

st.sidebar.title("Bike Sharing")
st.sidebar.markdown("### Filter Data")

season_options = sorted(df['season_label'].unique())
season_selected = st.sidebar.multiselect(
    "Pilih Musim:", options=season_options, default=season_options
)

year_options = sorted(df['yr_label'].unique())
year_selected = st.sidebar.multiselect(
    "Pilih Tahun:", options=year_options, default=year_options
)

date_min = df['dteday'].min()
date_max = df['dteday'].max()
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal:", value=(date_min, date_max),
    min_value=date_min, max_value=date_max
)

weather_options = sorted(df['weather_label'].unique())
weather_selected = st.sidebar.multiselect(
    "Pilih Kondisi Cuaca:", options=weather_options, default=weather_options
)

mask = (
    df['season_label'].isin(season_selected) &
    df['yr_label'].isin(year_selected) &
    df['weather_label'].isin(weather_selected)
)

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    mask = mask & (df['dteday'] >= start_date) & (df['dteday'] <= end_date)

df_filtered = df[mask]

st.title("Bike Sharing Data Analysis Dashboard")
st.markdown("""
Dashboard ini menyajikan hasil analisis data penyewaan sepeda berdasarkan 
**Bike Sharing Dataset** (2011–2012, Washington D.C.). 
Gunakan filter di sidebar untuk menyesuaikan tampilan data.
""")
st.divider()
st.subheader("Ringkasan Metrik")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rentals = int(df_filtered['cnt'].sum())
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    avg_daily = df_filtered['cnt'].mean()
    st.metric("Rata-rata Harian", f"{avg_daily:,.0f}")

with col3:
    max_daily = df_filtered['cnt'].max()
    st.metric("Penyewaan Tertinggi per Hari", f"{max_daily:,}")

with col4:
    growth = ((df_filtered[df_filtered['yr_label'] == '2012']['cnt'].sum() -
               df_filtered[df_filtered['yr_label'] == '2011']['cnt'].sum()) /
              df_filtered[df_filtered['yr_label'] == '2011']['cnt'].sum() * 100
              if len(df_filtered[df_filtered['yr_label'] == '2011']) > 0 else 0)
    st.metric("Pertumbuhan 2011→2012", f"{growth:+.1f}%")

st.divider()

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
        grp['mnth_label'], grp['cnt'],
        marker='o', linewidth=2.5, markersize=6,
        color=colors_yr.get(yr, '#333333'), label=yr
    )
ax1.set_title('Rata-rata Penyewaan Harian per Bulan', fontsize=12, fontweight='bold')
ax1.set_xlabel('Bulan', fontsize=10)
ax1.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=10)
ax1.set_xticks(range(12))
ax1.set_xticklabels(month_order, rotation=45)
ax1.legend(title='Tahun', fontsize=9)
ax1.grid(True, alpha=0.4)

ax2 = axes[1]
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
season_avg = (
    df_filtered.groupby('season_label')['cnt']
    .mean()
    .reindex(season_order)
)
colors_season = ['#55A868', '#CCB974', '#C44E52', '#8172B3']
bars = ax2.bar(season_avg.index, season_avg.values, color=colors_season, edgecolor='white', linewidth=1)
for bar, val in zip(bars, season_avg.values):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 50, f'{val:,.0f}',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax2.set_title('Rata-rata Penyewaan per Musim', fontsize=12, fontweight='bold')
ax2.set_xlabel('Musim', fontsize=10)
ax2.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=10)
ax2.grid(True, axis='y', alpha=0.4)

plt.tight_layout()
st.pyplot(fig1)

peak_season = season_avg.idxmax()
peak_val = season_avg.max()
low_season = season_avg.idxmin()
low_val = season_avg.min()
st.info(f"""
**Kesimpulan:** Penyewaan sepeda menunjukkan pola musiman yang konsisten. 
Musim **{peak_season}** memiliki rata-rata penyewaan harian tertinggi ({peak_val:,.0f} sepeda), 
sedangkan musim **{low_season}** terendah ({low_val:,.0f} sepeda). 
Pola ini dapat digunakan sebagai dasar perencanaan armada sepeda secara musiman.
""")

st.divider()

st.subheader("Pola Penyewaan per Jam: Kerja vs Non-Kerja")
st.markdown("""
**Pertanyaan Bisnis 2:** Bagaimana pola penyewaan sepeda per jam beda antara 
hari kerja dan hari non-kerja?
""")

# Filter hour_df berdasarkan filter yang sama (season, year, date range)
hour_mask = (
    hour_df['season_label'].isin(season_selected) &
    hour_df['yr_label'].isin(year_selected) &
    hour_df['weather_label'].isin(weather_selected)
)

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    hour_mask = hour_mask & (hour_df['dteday'] >= start_date) & (hour_df['dteday'] <= end_date)

hour_filtered = hour_df[hour_mask]

# Rata-rata penyewaan per jam, grouped by workingday_label
hourly_avg = (
    hour_filtered.groupby(['hr', 'workingday_label'])['cnt']
    .mean()
    .reset_index()
    .sort_values('hr')
)

# Pivot untuk plotting
hourly_pivot = hourly_avg.pivot(index='hr', columns='workingday_label', values='cnt').fillna(0)

fig2, ax = plt.subplots(figsize=(14, 5))

work_data = hourly_pivot['Yes'] if 'Yes' in hourly_pivot.columns else hourly_pivot.iloc[:, 0]
nowrk_data = hourly_pivot['No'] if 'No' in hourly_pivot.columns else hourly_pivot.iloc[:, -1]

ax.plot(hourly_pivot.index, work_data, marker='o', linewidth=2.5, markersize=5,
        color='#4C72B0', label='Hari Kerja')
ax.plot(hourly_pivot.index, nowrk_data, marker='o', linewidth=2.5, markersize=5,
        color='#C44E52', label='Hari Non-Kerja')

ax.fill_between(hourly_pivot.index, work_data, alpha=0.25, color='#4C72B0')
ax.fill_between(hourly_pivot.index, nowrk_data, alpha=0.25, color='#C44E52')

# Annotasi puncak
if len(work_data) > 0:
    peak_work_hr = work_data.idxmax()
    peak_work_val = work_data.max()
    ax.annotate(
        'Puncak Kerja\\n{}:00\\n{:,.0f}'.format(int(peak_work_hr), peak_work_val),
        xy=(peak_work_hr, peak_work_val),
        xytext=(peak_work_hr, peak_work_val + max(work_data.max(), nowrk_data.max()) * 0.15),
        ha='center', fontsize=9, color='#4C72B0', fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='#4C72B0', lw=1.5)
    )

if len(nowrk_data) > 0:
    peak_nowrk_hr = nowrk_data.idxmax()
    peak_nowrk_val = nowrk_data.max()
    ax.annotate(
        'Puncak Non-Kerja\\n{}:00\\n{:,.0f}'.format(int(peak_nowrk_hr), peak_nowrk_val),
        xy=(peak_nowrk_hr, peak_nowrk_val),
        xytext=(peak_nowrk_hr, peak_nowrk_val + max(work_data.max(), nowrk_data.max()) * 0.15),
        ha='center', fontsize=9, color='#C44E52', fontweight='bold',
        arrowprops=dict(arrowstyle='->', color='#C44E52', lw=1.5)
    )

ax.set_title('Rata-rata Penyewaan per Jam: Hari Kerja vs Non-Kerja', fontsize=13, fontweight='bold')
ax.set_xlabel('Jam (0-23)', fontsize=11)
ax.set_ylabel('Rata-rata Jumlah Penyewaan per Jam', fontsize=11)
ax.set_xticks(range(0, 24))
ax.set_xticklabels(['{}:00'.format(h) for h in range(0, 24)], rotation=45)
ax.legend(title='Tipe Hari', fontsize=10)
ax.grid(True, alpha=0.4)
plt.tight_layout()
st.pyplot(fig2)

# Metrik tambahan per jam
col_hour1, col_hour2, col_hour3 = st.columns(3)
with col_hour1:
    if len(work_data) > 0:
        st.metric("Jam Puncak Kerja", '{}:00'.format(int(work_data.idxmax())), '{:,.0f} sepeda'.format(work_data.max()))
with col_hour2:
    if len(nowrk_data) > 0:
        st.metric("Jam Puncak Non-Kerja", '{}:00'.format(int(nowrk_data.idxmax())), '{:,.0f} sepeda'.format(nowrk_data.max()))
with col_hour3:
    total_hourly = int(hour_filtered['cnt'].sum())
    st.metric("Total Penyewaan per Jam", '{:,}'.format(total_hourly))

st.info("""
**Kesimpulan:** Hari kerja (Senin–Jumat) cenderung memiliki **pola bimodal** (dua puncak): 
pagi sekitar **08:00** (commute ke kantor) dan sore **17:00–18:00** (pulang kerja) — 
pola khas pengguna commuter. Hari non-kerja (Sabtu–Minggu) menunjukkan **pola unimodal**: 
penyewaan mulai naik pagi dan mencapai puncak sekitar **12:00–15:00** — pola rekreasi. 
Ini relevan untuk pengaturan redistribusi armada sepeda per jam.
""")

st.divider()

st.subheader("Pengaruh Cuaca terhadap Penyewaan")
st.markdown("""
**Pertanyaan Bisnis 3:** Bagaimana pengaruh kondisi cuaca terhadap jumlah 
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
colors_w = ['#55A868', '#CCB974', '#C44E52', '#8172B3']
colors_w = colors_w[:len(weather_plot)]
bars = ax1.barh(weather_plot.index, weather_plot.values, color=colors_w, edgecolor='white', linewidth=1, height=0.6)
for bar, val in zip(bars, weather_plot.values):
    ax1.text(val + 50, bar.get_y() + bar.get_height()/2, f'{val:,.0f}',
             va='center', fontsize=9, fontweight='bold')
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

st.info(f"""
**Kesimpulan:** Kondisi cuaca **Clear/Partly Cloudy** menghasilkan rata-rata penyewaan 
tertinggi ({weather_avg.max():,.0f} sepeda/hari), sedangkan cuaca buruk (hujan/salju) 
menurunkan penyewaan secara signifikan. Suhu optimum untuk penyewaan berada pada kisaran 
20–30°C. Informasi ini dapat digunakan untuk program promosi berbasis cuaca.
""")

st.divider()

st.subheader("Data Detail")
st.markdown(f"Menampilkan {len(df_filtered)} baris data setelah difilter.")
st.dataframe(df_filtered, use_container_width=True, height=400)

st.divider()

st.subheader("Kesimpulan & Rekomendasi")

st.markdown("""
### Kesimpulan Utama
1. **Pola Musiman:** Penyewaan tertinggi terjadi di musim Fall (Gugur), terutama September–Oktober. 
   Penyewaan terendah di musim Spring (Semi), khususnya Januari.
2. **Pola Per Jam/Hari:** Hari kerja menunjukkan pola bimodal (puncak pagi dan sore) 
   khas commuter, sedangkan akhir pekan menunjukkan pola unimodal (puncak siang) 
   untuk rekreasi.
3. **Pengaruh Cuaca:** Cuaca cerah dan suhu hangat (20–30°C) mendorong penyewaan, 
   sedangkan cuaca buruk (hujan/salju) mengurangi penyewaan hingga 63%.

### Rekomendasi Action Item
1. **Optimasi Armada Berbasis Musim:** Tambah armada 30–40% di musim Fall, 
   kurangi operasional dan lakukan maintenance di musim Winter–Spring.
2. **Redistribusi Sepeda:** Rebalancing otomatis sebelum jam puncak commuter (07:30 dan 16:30), 
   prioritas area rekreasi di akhir pekan (10:00–14:00).
3. **Promosi Berbasis Cuaca:** Notifikasi diskon ke pengguna casual saat cuaca cerah 
   dan suhu 20–28°C.
4. **Konversi Casual ke Registered:** Kampanye konversi di akhir pekan, trial membership 
   30 hari di musim Summer dan Fall.
""")

st.divider()
st.markdown("""
*Dashboard dibuat untuk proyek analisis data Dicoding - Belajar Fundamental Analisis Data.*  
*Sumber data: Bike Sharing Dataset (Hadi Fanaee-T, University of Porto)*
""")
st.divider()
