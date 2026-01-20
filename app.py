import streamlit as st
import mysql.connector
import pandas as pd
import io

# --- KONFIGURASI LOGIN ---
# Silakan ganti username dan password sesuai keinginan Anda
USER_ADMIN = "satrio"
PASS_ADMIN = "kcs_2026"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 Login Sistem Logistik")
        with st.form("login_form"):
            user_input = st.text_input("Username")
            pass_input = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Masuk")
            
            if login_btn:
                if user_input == USER_ADMIN and pass_input == PASS_ADMIN:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Username atau Password salah!")
        return False
    return True

# --- FUNGSI KONEKSI DATABASE ---
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

# --- PROGRAM UTAMA ---
if check_login():
    # Tombol Logout di Sidebar
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🚚 Input Surat Jalan Pabrik")

    # Form Input
    with st.form("input_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            tgl = st.date_input("Tanggal")
            no_sj = st.text_input("Nomor Surat Jalan")
            sopir = st.text_input("Nama Sopir")
            plat = st.text_input("Plat Nomor")
        with col2:
            customer = st.text_input("Customer")
            alamat = st.text_area("Alamat")
            keluar = st.time_input("Jam Keluar")
            masuk = st.time_input("Jam Masuk")
        
        submit = st.form_submit_button("Simpan Data")

    if submit:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            sql = """INSERT INTO ringkasan_perjalanan 
                     (tgl_surat_jalan, no_surat_jalan, nama_sopir, plat_nomor, nama_customer, alamat_kirim, jam_keluar, jam_masuk) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (tgl, no_sj, sopir, plat, customer, alamat, str(keluar), str(masuk)))
            conn.commit()
            st.success("✅ Data Berhasil Disimpan!")
            conn.close()
        except Exception as e:
            st.error(f"Gagal Simpan: {e}")

    # Tabel Laporan & Download
    st.divider()
    st.subheader("📋 Laporan Perjalanan Terbaru")
    try:
        conn = get_connection()
        query = "SELECT * FROM ringkasan_perjalanan ORDER BY created_at DESC LIMIT 20"
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Fitur Download Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Download Laporan ke Excel",
                data=output.getvalue(),
                file_name="Laporan_Logistik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.info("Belum ada data untuk ditampilkan.")
