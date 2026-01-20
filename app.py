import streamlit as st
import mysql.connector
import pandas as pd
import io

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Logistics Dashboard", page_icon="📊", layout="wide")

# 2. STYLE CSS CUSTOM (Tampilan Modern)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007bff; font-weight: bold; }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    .main-header { text-align: center; padding: 15px; background: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .footer { text-align: center; color: gray; font-size: 12px; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 3. KREDENSIAL LOGIN
USER_ADMIN = "admin"
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

# --- SISTEM LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br><h1 style='text-align: center;'>🚚 LOGIN PORTAL</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("MASUK KE SISTEM"):
                if u == USER_ADMIN and p == PASS_ADMIN:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else: st.error("Akses Ditolak! Periksa kembali Username/Password.")
    st.stop()

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1532/1532674.png", width=80)
    st.title("Admin Panel")
    st.write(f"Login sebagai: **{USER_ADMIN}**")
    st.divider()
    if st.button("🚪 Keluar (Logout)"):
        st.session_state["logged_in"] = False
        st.rerun()

# --- HEADER & KPI STATISTIK ---
st.markdown("<div class='main-header'><h1>📊 LOGISTICS COMMAND CENTER</h1></div>", unsafe_allow_html=True)

try:
    db = get_connection()
    df_full = pd.read_sql("SELECT * FROM ringkasan_perjalanan", db)
    db.close()
    
    # KPI Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Pengiriman", f"{len(df_full)} Trip")
    m2.metric("Sopir Aktif", f"{df_full['nama_sopir'].nunique()} Orang")
    m3.metric("Customer Terdaftar", f"{df_full['nama_customer'].nunique()} PT/Toko")
    last_date = df_full['tgl_surat_jalan'].max() if not df_full.empty else "-"
    m4.metric("Update Terakhir", str(last_date))
except:
    st.warning("Menunggu koneksi database...")
    df_full = pd.DataFrame()

# --- MENU TABS ---
tab1, tab2, tab3 = st.tabs(["➕ Input Data Baru", "📋 Laporan & Filter", "🗑️ Manajemen Data"])

with tab1:
    st.subheader("📝 Form Input Surat Jalan")
    with st.form("input_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            tgl = st.date_input("Tanggal Surat Jalan")
            no_sj = st.text_input("Nomor Surat Jalan", placeholder="Contoh: SJ-001")
            sopir = st.text_input("Nama Sopir")
            plat = st.text_input("Plat Nomor")
        with col_b:
            cust = st.text_input("Nama Customer")
            alamat = st.text_area("Alamat Lengkap", placeholder="Jl. Raya...")
            jam_k = st.time_input("Jam Keluar")
            jam_m = st.time_input("Jam Masuk")
        
        if st.form_submit_button("SIMPAN DATA SEKARANG"):
            if not no_sj or not sopir:
                st.error("No. Surat Jalan dan Nama Sopir wajib diisi!")
            else:
                try:
                    db = get_connection()
                    cursor = db.cursor()
                    sql = "INSERT INTO ringkasan_perjalanan (tgl_surat_jalan, no_surat_jalan, nama_sopir, plat_nomor, nama_customer, alamat_kirim, jam_keluar, jam_masuk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (tgl, no_sj, sopir, plat, cust, alamat, str(jam_k), str(jam_m)))
                    db.commit()
                    db.close()
                    st.success("✅ Data berhasil masuk ke database!")
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")

with tab2:
    st.subheader("🔍 Laporan Perjalanan")
    if not df_full.empty:
        # Filter Pencarian
        search = st.text_input("Cari Nama Sopir atau Customer", "")
        df_filtered = df_full[df_full.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        
        st.dataframe(df_filtered, use_container_width=True)
        
        # Download Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False)
        st.download_button("📥 Download Hasil Filter ke Excel", output.getvalue(), "Laporan_Logistik.xlsx", "application/vnd.ms-excel")
    else:
        st.info("Belum ada data di database.")

with tab3:
    st.subheader("⚠️ Hapus Data")
    st.write("Gunakan menu ini untuk menghapus data yang salah input.")
    no_del = st.text_input("Masukkan No. SJ yang ingin dihapus")
    confirm = st.checkbox("Saya sadar data ini akan dihapus permanen")
    
    if st.button("HAPUS DATA", type="primary"):
        if no_del and confirm:
            try:
                db = get_connection()
                cursor = db.cursor()
                cursor.execute("DELETE FROM ringkasan_perjalanan WHERE no_surat_jalan = %s", (no_del,))
                db.commit()
                db.close()
                st.success(f"Berhasil menghapus No. SJ: {no_del}")
                st.rerun()
            except Exception as e: st.error(e)
        else:
            st.warning("Mohon isi No. SJ dan centang konfirmasi.")

st.markdown("<div class='footer'>Logistics Dashboard v2.0 © 2026</div>", unsafe_allow_html=True)
