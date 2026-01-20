import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv
import os

# Load konfigurasi dari file .env
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"]
        )
        return conn
    except Error as e:
        st.error(f"Gagal koneksi ke database: {e}")
        return None

# Fungsi Koneksi Database
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except Error as e:
        st.error(f"Gagal koneksi ke database: {e}")
        return None

# Fungsi untuk Menyimpan Data
def simpan_data(tgl, no_sj, sopir, plat, customer, alamat, keluar, masuk):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        query = """INSERT INTO ringkasan_perjalanan 
                   (tgl_surat_jalan, no_surat_jalan, nama_sopir, plat_nomor, nama_customer, alamat_kirim, jam_keluar, jam_masuk) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (tgl, no_sj, sopir, plat, customer, alamat, keluar, masuk)
        try:
            cursor.execute(query, values)
            conn.commit()
            st.success(f"Data Surat Jalan {no_sj} berhasil disimpan!")
        except Error as e:
            st.error(f"Terjadi kesalahan: {e}")
        finally:
            cursor.close()
            conn.close()

# --- UI STREAMLIT ---
st.set_page_config(page_title="Logistik Trip Summary", layout="wide")

st.title("🚚 Sistem Ringkasan Perjalanan")
st.markdown("Input data pengiriman barang keluar/masuk pabrik.")

# Membuat Form Input
with st.form("form_perjalanan", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        tgl_sj = st.date_input("Tanggal Surat Jalan")
        no_sj = st.text_input("Nomor Surat Jalan", placeholder="Contoh: SJ-2024-001")
        nama_sopir = st.text_input("Nama Sopir")
        plat_nomor = st.text_input("Plat Nomor Kendaraan")

    with col2:
        nama_customer = st.text_input("Nama Customer")
        alamat_kirim = st.text_area("Alamat Pengiriman")
        jam_keluar = st.time_input("Jam Keluar Pabrik")
        jam_masuk = st.time_input("Jam Masuk Pabrik")

    submit_button = st.form_submit_button("Simpan Ringkasan")

if submit_button:
    # Validasi sederhana
    if not no_sj or not nama_sopir:
        st.warning("Nomor SJ dan Nama Sopir wajib diisi!")
    else:
        simpan_data(tgl_sj, no_sj, nama_sopir, plat_nomor, nama_customer, alamat_kirim, 
                    jam_keluar.strftime('%H:%M'), jam_masuk.strftime('%H:%M'))

# Menampilkan Data dari Database
st.divider()
st.subheader("📊 Laporan Perjalanan Terbaru")

conn = get_connection()
if conn:
    query_view = "SELECT * FROM ringkasan_perjalanan ORDER BY created_at DESC LIMIT 10"
    df = pd.read_sql(query_view, conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
