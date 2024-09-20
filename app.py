import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile

# Membuka file ZIP dan membaca dataset
with zipfile.ZipFile("data1.zip", "r") as zip_ref:
    zip_ref.extractall(".")

# Membaca file CSV setelah diekstrak
data = pd.read_csv("data1.csv")

# Mengatur tema warna untuk background dan teks
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        color: #333333;
    }
    .stSidebar {
        background-color: #2c3e50;
        color: #ffffff;
    }
    h1 {
        color: #2980b9;
    }
    h3 {
        color: #e74c3c;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar untuk filter tahun, bulan, stasiun, dan metrik
st.sidebar.header('Filter Dashboard')

# Pilih Tahun
year_filter = st.sidebar.selectbox('Pilih Tahun', options=sorted(data['year'].unique()))

# Pilih Bulan
month_filter = st.sidebar.selectbox('Pilih Bulan', options=sorted(data['month'].unique()))

# Pilih Stasiun
station_filter = st.sidebar.selectbox('Pilih Stasiun', options=['Shunyi', 'Changping'])

# Pilih Metrik
metric_filter = st.sidebar.selectbox('Pilih Metrik', ['PM2.5', 'PM10', 'NO2', 'CO dan RAIN'])

# Filter data berdasarkan pilihan tahun dan bulan
data_filtered = data[(data['year'] == year_filter) & (data['month'] == month_filter)]

# Header utama
st.markdown(f"<h1>Dashboard Polusi Udara di Stasiun {station_filter} ({year_filter})</h1>", unsafe_allow_html=True)
st.markdown(f"<h3>Analisis untuk Bulan {month_filter} - {metric_filter}</h3>", unsafe_allow_html=True)

# 1. Analisis PM2.5, PM10, dan NO2 di Stasiun Shunyi
def analyze_pm_temperature_shunyi(df):
    df_shunyi = df[(df['station'] == 'Shunyi') & (df['year'] == year_filter) & (df['month'] == month_filter)]
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_shunyi, x='PM2.5', y='TEMP', label='PM2.5 vs TEMP', color='#3498db')
    sns.scatterplot(data=df_shunyi, x='PM10', y='TEMP', label='PM10 vs TEMP', color='#e74c3c')
    plt.title(f'PM2.5, PM10 vs Suhu di Stasiun Shunyi ({month_filter}/{year_filter})', fontsize=16, color='#2c3e50')
    plt.xlabel('PM2.5 dan PM10', fontsize=12, color='#2c3e50')
    plt.ylabel('Suhu', fontsize=12, color='#2c3e50')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(plt)
    
    st.markdown("### Insight PM2.5 dan PM10 vs Suhu:")
    st.write("""
    - **Korelasi positif lemah** ditemukan antara **PM2.5, PM10, dan Suhu**, yang berarti kenaikan polutan ini tidak secara signifikan mempengaruhi suhu.
    - Polusi udara tinggi mungkin tidak langsung meningkatkan suhu, tetapi tetap berbahaya bagi kesehatan manusia.
    """)

    return df_shunyi[['PM2.5', 'PM10', 'TEMP']].corr()

# 2. Analisis Korelasi CO dan Hujan di Stasiun Changping
def analyze_co_rain_changping(df):
    df_changping = df[(df['station'] == 'Changping') & (df['year'] == year_filter) & (df['month'] == month_filter)]
    correlation = df_changping[['CO', 'RAIN']].corr()
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df_changping, x='CO', y='RAIN', hue='CO', palette='coolwarm')
    plt.title(f'Korelasi antara CO dan Hujan di Stasiun Changping ({month_filter}/{year_filter})', fontsize=16, color='#2c3e50')
    plt.xlabel('CO', fontsize=12, color='#2c3e50')
    plt.ylabel('Hujan (RAIN)', fontsize=12, color='#2c3e50')
    st.pyplot(plt)
    
    st.markdown("### Insight Korelasi CO dan Hujan:")
    st.write("""
    - Terdapat **korelasi negatif** antara **CO dan curah hujan**, yang menunjukkan bahwa hujan membantu membersihkan polusi CO dari atmosfer.
    - Curah hujan tinggi dapat membantu mengurangi polusi udara, terutama konsentrasi CO, yang membuat kondisi udara lebih bersih.
    """)

    return correlation

# 3. Kenaikan Konsentrasi NO2 di atas 50 µg/m³
def visualize_no2_spikes(df):
    df_no2_spikes = df[df['NO2'] > 50]
    plt.figure(figsize=(10,6))
    plt.plot(df['day'], df['NO2'], label='Konsentrasi NO2', color='blue', alpha=0.6)
    plt.scatter(df_no2_spikes['day'], df_no2_spikes['NO2'], color='red', label='NO2 > 50 µg/m³', alpha=0.8)
    plt.axhline(y=50, color='red', linestyle='--', label='Threshold: 50 µg/m³')
    plt.title('Kenaikan NO2 di atas 50 µg/m³')
    plt.xlabel('Hari')
    plt.ylabel('Konsentrasi NO2 (µg/m³)')
    plt.legend()
    st.pyplot(plt)
    
    st.markdown("### Insight Kenaikan NO2 di atas 50 µg/m³:")
    st.write("""
    - Konsentrasi **NO2** beberapa kali melewati ambang batas aman **50 µg/m³**, yang dapat berdampak buruk bagi kesehatan.
    - Monitoring yang ketat diperlukan untuk mencegah kenaikan polusi ini, terutama di daerah yang rawan.
    """)

# Eksekusi berdasarkan filter stasiun dan metrik
if station_filter == 'Shunyi':
    if metric_filter in ['PM2.5', 'PM10', 'NO2']:
        pm_temperature_correlation = analyze_pm_temperature_shunyi(data_filtered)
        st.write(pm_temperature_correlation)
elif station_filter == 'Changping' and metric_filter == 'CO dan RAIN':
    co_rain_correlation = analyze_co_rain_changping(data_filtered)
    st.write(co_rain_correlation)
    st.write("Korelasi antara CO dan hujan menunjukkan bahwa cuaca memiliki dampak langsung pada konsentrasi polusi udara.")

