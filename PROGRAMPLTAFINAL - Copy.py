# -*- coding: utf-8 -*-
"""
Created on Wed Dec 31 19:04:38 2025

@author: Alfauziyah
"""
# ==================================================
# STREAMLIT WEB APP - FORECASTING POTENSI PLTA
# ==================================================

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

st.set_page_config(page_title="Forecasting PLTA", layout="centered")

# --------------------------------------------------
# JUDUL
# --------------------------------------------------
st.title("Aplikasi Forecasting Potensi PLTA")
st.caption("Analisis Debit Sungai dan Daya PLTA")

# --------------------------------------------------
# INPUT DATA SUNGAI
# --------------------------------------------------
st.header("Input Data Sungai")

nama_sungai = st.text_input("Nama Sungai")
Q_dasar = st.number_input(
    "Debit rata-rata sungai (m³/s)",
    min_value=0.1,
    value=5.0
)
head = st.number_input(
    "Head / Tinggi jatuh air (m)",
    min_value=1.0,
    value=10.0
)

# --------------------------------------------------
# PILIH BULAN
# --------------------------------------------------
st.header("Pilih Bulan Forecast")

nama_bulan = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

bulan_dipilih = st.multiselect(
    "Pilih bulan yang ingin dianalisis",
    nama_bulan
)

# --------------------------------------------------
# INPUT FAKTOR IKLIM
# --------------------------------------------------
st.header("Faktor Iklim Bulanan")

curah_hujan = {}
suhu = {}
kelembaban = {}

for bulan in bulan_dipilih:
    st.subheader(f"Bulan {bulan}")
    curah_hujan[bulan] = st.number_input(
        f"Curah hujan (mm) - {bulan}",
        value=200.0
    )
    suhu[bulan] = st.number_input(
        f"Suhu rata-rata (°C) - {bulan}",
        value=27.0
    )
    kelembaban[bulan] = st.number_input(
        f"Kelembaban (%) - {bulan}",
        value=75.0
    )

# --------------------------------------------------
# PROSES FORECASTING
# --------------------------------------------------
if st.button("Jalankan Forecast") and bulan_dipilih:

    # Konstanta fisika
    rho = 1000  # kg/m3
    g = 9.81    # m/s2

    # Koefisien pengaruh iklim
    k_r = 0.001   # curah hujan
    k_t = 0.01    # suhu (evaporasi)
    k_h = 0.002   # kelembaban

    data = []

    for bulan in bulan_dipilih:
        R = curah_hujan[bulan]
        T = suhu[bulan]
        H = kelembaban[bulan] / 100

        Q_forecast = Q_dasar * (1 + k_r*R - k_t*T + k_h*H)
        P_forecast = rho * g * Q_forecast * head / 1000  # kW

        data.append([
            bulan, R, T, H*100, Q_forecast, P_forecast
        ])

    df = pd.DataFrame(
        data,
        columns=[
            "Bulan",
            "Curah Hujan (mm)",
            "Suhu (°C)",
            "Kelembaban (%)",
            "Debit Forecast (m3/s)",
            "Daya PLTA (kW)"
        ]
    )

    # --------------------------------------------------
    # OUTPUT HASIL
    # --------------------------------------------------
    st.subheader("Hasil Forecasting")
    st.write(f"**Nama Sungai:** {nama_sungai}")
    st.write(f"**Daya Rata-rata:** {df['Daya PLTA (kW)'].mean():.2f} kW")

    # Kelayakan PLTA
    Q_rata = df["Debit Forecast (m3/s)"].mean()

    if Q_rata >= 5:
        status = "Sangat Layak (PLTA Mini)"
    elif Q_rata >= 1:
        status = "Layak (PLTA Mikro)"
    else:
        status = "Kurang Layak"

    st.success(f"Status Kelayakan: **{status}**")

    st.subheader("Tabel Data Forecast")
    st.dataframe(df)

    # --------------------------------------------------
    # BAR CHART DEBIT
    # --------------------------------------------------
    st.subheader("Grafik Debit Forecast")

    fig1, ax1 = plt.subplots()
    ax1.bar(df["Bulan"], df["Debit Forecast (m3/s)"])
    ax1.set_xlabel("Bulan")
    ax1.set_ylabel("Debit (m³/s)")
    ax1.set_title("Debit Sungai Hasil Forecast")
    ax1.grid(axis="y")

    st.pyplot(fig1)

    # --------------------------------------------------
    # BAR CHART DAYA PLTA
    # --------------------------------------------------
    st.subheader("Grafik Daya PLTA")

    fig2, ax2 = plt.subplots()
    ax2.bar(df["Bulan"], df["Daya PLTA (kW)"])
    ax2.set_xlabel("Bulan")
    ax2.set_ylabel("Daya (kW)")
    ax2.set_title("Potensi Daya PLTA")
    ax2.grid(axis="y")

    st.pyplot(fig2)
    
    st.dataframe(df)
# =========================================
# LINE CHART FORECAST DAYA PLTA
# =========================================
st.subheader("Grafik Time Series Daya PLTA (Forecast)")

# Urutan bulan (boleh pakai ulang)
urutan_bulan = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

# Pastikan kolom forecast ada
if "Bulan" in df.columns and "Daya PLTA (kW)" in df.columns:

    # Set kategori bulan (AMAN meskipun sudah diset sebelumnya)
    df["Bulan"] = pd.Categorical(
        df["Bulan"],
        categories=urutan_bulan,
        ordered=True
    )

    df = df.sort_values("Bulan")

    # Buat figure BARU (tidak ganggu bar chart)
    fig3, ax3 = plt.subplots()

    ax3.plot(
        df["Bulan"],
        df["Daya PLTA (kW)"],
        marker='o',
        linewidth=2
    )

    ax3.set_xlabel("Bulan")
    ax3.set_ylabel("Daya (kW)")
    ax3.set_title("Tren Forecast Daya PLTA")
    ax3.grid(True)

    st.pyplot(fig3)

else:
    st.warning("Kolom 'Bulan' atau 'Daya PLTA (kW)' tidak ditemukan")
