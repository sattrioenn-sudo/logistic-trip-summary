import streamlit as st
import mysql.connector
import pandas as pd
import io
import plotly.express as px

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Logistics Command Center", page_icon="📊", layout="wide")

# 2. STYLE CSS CUSTOM
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007bff; font-weight: bold; }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    .main-header { text-align: center; padding: 15px; background: white; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
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
        st.markdown("<br><br><h1 style='text-align: center;'>🚚 LOGISTICS LOGIN</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("MASUK KE SISTEM"):
                if u == USER_ADMIN and p == PASS_ADMIN:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else: st.error("Akses Ditolak!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1532/1532674.png", width=80)
    st.title("Admin Panel")
    st.write(f"User: **{USER_ADMIN}**")
    if st.button("🚪 Logout"):
        st.session_state["logged_in"] = False
        st.rerun()

# --- HEADER & AMBIL DATA ---
st.markdown("<div class='main-header'><h1>📊 LOGISTICS COMMAND CENTER</h1></div>", unsafe_allow_html=True)

try:
    db = get_connection()
    df_full = pd.read_sql("SELECT * FROM ringkasan_perjalanan", db)
    db.close()
except:
    df_full = pd.DataFrame()

# --- BAGIAN 1: STATISTIK & GRAFIK ---
if not df_full.empty:
    # KPI Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Pengiriman", f"{len(df_full)} Trip")
    m2.metric("Sopir Aktif", f"{df_full['nama_sopir'].nunique()} Orang")
    m3.metric("Customer", f"{df_full['nama_customer'].nunique()} PT/Toko")
    m4.metric("Update Terakhir", str(df_full['tgl_surat_jalan'].max()))

    # Grafik Performa Sopir
    st.divider()
    st.subheader("📊 Grafik Distribusi Tugas Sopir")
    df_grafik = df_full['nama_sopir'].value_counts().reset_index()
    df_grafik.columns = ['Nama Sopir', 'Jumlah Trip']
    
    fig = px.bar(df_grafik, x='Nama Sopir', y='Jumlah Trip', text='Jumlah Trip',
                 color='Jumlah Trip', color_continuous_scale='Blues')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# --- BAGIAN 2: TABS MENU ---
st.divider()
tab1, tab2, tab3 = st.tabs(["➕ Input Trip", "📋 Laporan & Download", "🗑️ Hapus Data"])

with tab1:
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal")
            no_sj = st.text_input("No. Surat Jalan")
            sopir = st.text_input("Nama Sopir")
            plat = st.text_input("Plat Nomor")
        with c2:
            cust = st.text_input("Customer")
            alamat = st.text_area("Alamat")
            jam_k = st.time_input("Jam Keluar")
            jam_m = st.time_input("Jam Masuk")
        
        if st.form_submit_button("SIMPAN DATA"):
            try:
                db = get_connection()
                cursor = db.cursor()
                sql = "INSERT INTO ringkasan_perjalanan (tgl_surat_jalan, no_surat_jalan, nama_sopir, plat_nomor, nama_customer, alamat_kirim, jam_keluar, jam_masuk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (tgl, no_sj, sopir, plat, cust, alamat, str(jam_k), str(jam_m)))
                db.commit()
                db.close()
                st.success("✅ Berhasil Disimpan!")
                st.rerun()
            except Exception as e: st.error(e)

with tab2:
    if not df_full.empty:
        search = st.text_input("🔍 Cari Sopir/Customer/No SJ", "")
        df_filtered = df_full[df_full.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(df_filtered, use_container_width=True)
        
        # Download Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_filtered.to_excel(writer, index=False)
        st.download_button("📥 Download Excel", output.getvalue(), "Laporan_Logistik.xlsx", "application/vnd.ms-excel")
    else: st.info("Data kosong.")

with tab3:
    no_del = st.text_input("No. SJ yang akan dihapus")
    confirm = st.checkbox("Konfirmasi hapus permanen")
    if st.button("HAPUS SEKARANG", type="primary"):
        if no_del and confirm:
            try:
                db = get_connection()
                cursor = db.cursor()
                cursor.execute("DELETE FROM ringkasan_perjalanan WHERE no_surat_jalan = %s", (no_del,))
                db.commit()
                db.close()
                st.success("Terhapus!")
                st.rerun()
            except Exception as e: st.error(e)
