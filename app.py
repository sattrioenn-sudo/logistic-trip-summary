import streamlit as st
import mysql.connector
import pandas as pd
import io

# 1. KONFIGURASI HALAMAN (Tampilan Tab Browser)
st.set_page_config(page_title="Logistik App", page_icon="🚚", layout="wide")

# 2. CUSTOM CSS (Bikin tampilan lebih rapi dan tombol lebih bagus)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div.stButton > button:first-child {
        background-color: #007bff; color: white; border-radius: 8px;
        height: 3em; width: 100%; font-weight: bold; border: none;
    }
    .login-box {
        padding: 30px; background-color: white; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. KREDENSIAL LOGIN (Ganti sesuka Anda)
USER_ADMIN = "satrio"
PASS_ADMIN = "kcs_2026"

# 4. FUNGSI KONEKSI DATABASE (Tetap pakai Secrets Anda)
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"]
    )

# --- FUNGSI TAMPILAN LOGIN ---
def show_login():
    # Membuat grid agar box login ada di tengah
    _, col_mid, _ = st.columns([1, 1.5, 1])
    
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>🚚 LOGISTICS SYSTEM</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Monitoring Surat Jalan Pabrik</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='login-box'>", unsafe_allow_html=True)
            user_in = st.text_input("Username", placeholder="Masukkan ID anda")
            pass_in = st.text_input("Password", type="password", placeholder="Masukkan Password")
            
            if st.button("LOGIN SEKARANG"):
                if user_in == USER_ADMIN and pass_in == PASS_ADMIN:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("Username atau Password Salah!")
            st.markdown("</div>", unsafe_allow_html=True)

# --- LOGIKA APLIKASI ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    show_login()
else:
    # --- TAMPILAN SETELAH LOGIN (DASHBOARD) ---
    with st.sidebar:
        st.title("Admin Panel")
        st.write(f"User: **{USER_ADMIN}**")
        if st.button("Keluar / Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("🚚 Input Data Perjalanan")
    
    # FORM INPUT DATA
    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            tgl = st.date_input("Tanggal Surat Jalan")
            no_sj = st.text_input("Nomor Surat Jalan")
            sopir = st.text_input("Nama Sopir")
            plat = st.text_input("Plat Nomor Kendaraan")
        with c2:
            customer = st.text_input("Nama Customer")
            alamat = st.text_area("Alamat Pengiriman")
            keluar = st.time_input("Jam Keluar")
            masuk = st.time_input("Jam Masuk")
        
        btn_simpan = st.form_submit_button("SIMPAN DATA KE DATABASE")

    if btn_simpan:
        try:
            db = get_connection()
            curr = db.cursor()
            query = "INSERT INTO ringkasan_perjalanan (tgl_surat_jalan, no_surat_jalan, nama_sopir, plat_nomor, nama_customer, alamat_kirim, jam_keluar, jam_masuk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            curr.execute(query, (tgl, no_sj, sopir, plat, customer, alamat, str(keluar), str(masuk)))
            db.commit()
            st.success("✅ Berhasil! Data sudah tersimpan di TiDB Cloud.")
            db.close()
        except Exception as e:
            st.error(f"Error Database: {e}")

    # TABEL LAPORAN & DOWNLOAD EXCEL
    st.divider()
    st.subheader("📋 Data Perjalanan Terbaru")
    try:
        db = get_connection()
        df = pd.read_sql("SELECT * FROM ringkasan_perjalanan ORDER BY created_at DESC LIMIT 15", db)
        db.close()

        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Persiapan Download Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Download Data ke Excel",
                data=output.getvalue(),
                file_name="Laporan_Logistik.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except:
        st.info("Sistem siap. Belum ada data masuk.")
        # --- FITUR HAPUS DATA ---
st.divider()
st.subheader("🗑️ Hapus Data Surat Jalan")

with st.expander("Klik di sini jika ingin menghapus data"):
    no_sj_hapus = st.text_input("Masukkan Nomor Surat Jalan yang ingin dihapus")
    konfirmasi_hapus = st.checkbox("Saya yakin ingin menghapus data ini secara permanen")
    btn_hapus = st.button("HAPUS SEKARANG", type="primary")

    if btn_hapus:
        if not no_sj_hapus:
            st.warning("Silakan masukkan Nomor Surat Jalan terlebih dahulu.")
        elif not konfirmasi_hapus:
            st.warning("Silakan centang kotak konfirmasi untuk menghapus.")
        else:
            try:
                db = get_connection()
                curr = db.cursor()
                
                # Cek dulu apakah datanya ada
                curr.execute("SELECT * FROM ringkasan_perjalanan WHERE no_surat_jalan = %s", (no_sj_hapus,))
                data_ada = curr.fetchone()
                
                if data_ada:
                    # Jalankan perintah hapus
                    query_delete = "DELETE FROM ringkasan_perjalanan WHERE no_surat_jalan = %s"
                    curr.execute(query_delete, (no_sj_hapus,))
                    db.commit()
                    st.success(f"✅ Data dengan No SJ {no_sj_hapus} berhasil dihapus!")
                    db.close()
                    # Refresh otomatis agar tabel terupdate
                    st.rerun()
                else:
                    st.error("❌ Nomor Surat Jalan tidak ditemukan di database.")
                    db.close()
            except Exception as e:
                st.error(f"Gagal menghapus: {e}")
