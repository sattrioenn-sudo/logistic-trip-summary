import streamlit as st
import mysql.connector
import pandas as pd
import io
import plotly.express as px

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Logistik Command Center", page_icon="📊", layout="wide")

# 2. KREDENSIAL LOGIN & DATABASE
USER_ADMIN = "admin"
PASS_ADMIN = "kcs_2026"

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        ssl_verify_cert=False, # Penting untuk TiDB Cloud Serverless
        ssl_disabled=False     # Mengaktifkan SSL
    )

# 3. SISTEM LOGIN (TAMPILAN BERWARNA)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown("""
        <style>
        .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .login-card {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px; border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center; margin-top: -30px;
        }
        div.stButton > button:first-child {
            background: linear-gradient(to right, #6a11cb 0%, #2575fc 100%);
            color: white; border: none; border-radius: 10px; height: 3.5em; font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="login-card"><h1 style="color: #4a4a4a;">🚚 LOGISTICS</h1><p style="color: #666;">Silakan Login</p></div>', unsafe_allow_html=True)
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("MASUK SEKARANG"):
                    if u == USER_ADMIN and p == PASS_ADMIN:
                        st.session_state["logged_in"] = True
                        st.balloons()
                        st.rerun()
                    else: st.error("Username atau Password Salah!")
    st.stop()

# 4. DASHBOARD UTAMA (SETELAH LOGIN)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1532/1532674.png", width=80)
    st.title("Admin Panel")
    if st.button("🚪 Keluar (Logout)"):
        st.session_state["logged_in"] = False
        st.rerun()

st.markdown("<h1 style='text-align: center;'>📊 LOGISTICS COMMAND CENTER</h1>", unsafe_allow_html=True)

# AMBIL DATA DARI DATABASE
try:
    db = get_connection()
    df_full = pd.read_sql("SELECT * FROM ringkasan_perjalanan ORDER BY created_at DESC", db)
    list_sopir = pd.read_sql("SELECT nama_sopir FROM master_sopir ORDER BY nama_sopir", db)['nama_sopir'].tolist()
    list_plat = pd.read_sql("SELECT plat_nomor FROM master_plat ORDER BY plat_nomor", db)['plat_nomor'].tolist()
    db.close()
except Exception as e:
    st.error(f"Koneksi Database Gagal: {e}")
    df_full, list_sopir, list_plat = pd.DataFrame(), [], []

# 5. KPI & GRAFIK (RINGKASAN)
if not df_full.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Trip", f"{len(df_full)}x")
    m2.metric("Sopir Aktif", f"{df_full['nama_sopir'].nunique()}")
    m3.metric("Customer", f"{df_full['nama_customer'].nunique()}")
    
    st.divider()
    df_grafik = df_full['nama_sopir'].value_counts().reset_index()
    df_grafik.columns = ['Nama Sopir', 'Jumlah Trip']
    fig = px.bar(df_grafik, x='Nama Sopir', y='Jumlah Trip', color='Jumlah Trip', color_continuous_scale='Purples', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# 6. MENU UTAMA DALAM TABS
tab1, tab2, tab3, tab4 = st.tabs(["➕ Input Trip", "📋 Laporan Perjalanan", "⚙️ Master Data", "🗑️ Hapus Data"])

with tab1:
    st.subheader("📝 Input Surat Jalan")
    with st.form("input_trip", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal")
            no_sj = st.text_input("No. Surat Jalan")
            sopir_p = st.selectbox("Pilih Sopir", ["-- Pilih --"] + list_sopir)
            plat_p = st.selectbox("Pilih Kendaraan", ["-- Pilih --"] + list_plat)
        with c2:
            cust = st.text_input("Nama Customer")
            alamat = st.text_area("Alamat Pengiriman")
            jam_k = st.time_input("Jam Keluar")
            jam_m = st.time_input("Jam Masuk")
        
        if st.form_submit_button("SIMPAN DATA KE DATABASE"):
            if "-- Pilih --" in [sopir_p, plat_p] or not no_sj:
                st.warning("Mohon isi semua data (No SJ, Sopir, & Plat)!")
            else:
                db = get_connection(); cur = db.cursor()
                sql = "INSERT INTO ringkasan_perjalanan (tgl_surat_jalan, no_surat_jalan, nama_sopir, plat_nomor, nama_customer, alamat_kirim, jam_keluar, jam_masuk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                cur.execute(sql, (tgl, no_sj, sopir_p, plat_p, cust, alamat, str(jam_k), str(jam_m)))
                db.commit(); db.close(); st.success("✅ Data Berhasil Disimpan!"); st.rerun()

with tab2:
    st.subheader("📋 Laporan Pengiriman")
    if not df_full.empty:
        st.dataframe(df_full, use_container_width=True)
        # Bagian Download Excel dengan indentasi yang benar
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df_full.to_excel(writer, index=False)
        st.download_button(label="📥 Download Laporan (Excel)", data=out.getvalue(), file_name="Laporan_Logistik.xlsx")
    else: st.info("Belum ada data.")

with tab3:
    st.subheader("⚙️ Manajemen Master Data")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Daftar Sopir")
        ns = st.text_input("Tambah Nama Sopir Baru")
        if st.button("Simpan Nama Sopir"):
            db = get_connection(); cur = db.cursor()
            cur.execute("INSERT INTO master_sopir (nama_sopir) VALUES (%s)", (ns,))
            db.commit(); db.close(); st.success("Sopir ditambahkan!"); st.rerun()
        st.write(list_sopir)
    with col_b:
        st.write("### Daftar Plat Nomor")
        np = st.text_input("Tambah Plat Nomor Baru")
        if st.button("Simpan Plat Nomor"):
            db = get_connection(); cur = db.cursor()
            cur.execute("INSERT INTO master_plat (plat_nomor) VALUES (%s)", (np,))
            db.commit(); db.close(); st.success("Plat ditambahkan!"); st.rerun()
        st.write(list_plat)

with tab4:
    st.subheader("🗑️ Hapus Surat Jalan")
    no_h = st.text_input("Masukkan No SJ yang ingin dihapus")
    yakin = st.checkbox("Saya yakin akan menghapus data ini")
    if st.button("Hapus Secara Permanen", type="primary"):
        if no_h and yakin:
            db = get_connection(); cur = db.cursor()
            cur.execute("DELETE FROM ringkasan_perjalanan WHERE no_surat_jalan = %s", (no_h,))
            db.commit(); db.close(); st.success(f"SJ {no_h} Terhapus!"); st.rerun()
        else: st.warning("Masukkan No SJ dan centang konfirmasi!")
