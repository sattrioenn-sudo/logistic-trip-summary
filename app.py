import streamlit as st
import mysql.connector
import pandas as pd
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Logistics Dashboard", page_icon="📊", layout="wide")

# 2. STYLE CSS CUSTOM (Bikin Tampilan Mewah)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 25px; color: #007bff; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .main-header { text-align: center; padding: 20px; background: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. KREDENSIAL LOGIN
USER_ADMIN = "satrio"
PASS_ADMIN = "kcs_2026"

# 4. FUNGSI KONEKSI DATABASE
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

# --- FUNGSI LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br><h1 style='text-align: center;'>🚚 LOGIN SYSTEM</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("MASUK"):
                if u == USER_ADMIN and p == PASS_ADMIN:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else: st.error("Akses Ditolak!")
    st.stop()

# --- DASHBOARD UTAMA (SETELAH LOGIN) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1532/1532674.png", width=100)
    st.title("Admin Panel")
    st.write(f"Logged in: **{USER_ADMIN}**")
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

# --- BAGIAN HEADER & STATISTIK ---
st.markdown("<div class='main-header'><h1>📊 LOGISTICS COMMAND CENTER</h1></div>", unsafe_allow_html=True)

try:
    db = get_connection()
    df_stat = pd.read_sql("SELECT * FROM ringkasan_perjalanan", db)
    db.close()
    
    # Barisan Statistik Cepat (KPI)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Pengiriman", f"{len(df_stat)} Trip")
    m2.metric("Total Sopir", f"{df_stat['nama_sopir'].nunique()} Orang")
    m3.metric("Total Customer", f"{df_stat['nama_customer'].nunique()} PT/Toko")
    m4.metric("Update Terakhir", df_stat['tgl_surat_jalan'].max() if not df_stat.empty else "-")
except:
    st.warning("Gagal memuat statistik. Pastikan database terhubung.")

# --- TABS (MENU) ---
tab1, tab2, tab3 = st.tabs(["➕ Input Data Baru", "📋 Laporan & Download", "🗑️ Pengaturan / Hapus"])

with tab1:
    st.subheader("Form
