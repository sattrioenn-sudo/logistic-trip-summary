import streamlit as st
import mysql.connector
import pandas as pd
import io

# Konfigurasi Tema & Page
st.set_page_config(page_title="Sistem Logistik Pabrik", page_icon="🚚", layout="centered")

# --- STYLE CSS CUSTOM (Untuk mempercantik tampilan) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .login-header {
        text-align: center;
        color: #1e3d59;
        margin-bottom: 2em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KONFIGURASI LOGIN ---
USER_ADMIN = "satrio"
PASS_ADMIN = "kcs_2026"

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # Tampilan Login yang Keren
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<div class='login-header'>", unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/512/2343/2343894.png", width=100) # Ikon Truk
            st.title("Logistics Portal")
            st.write("Silakan login untuk mengakses sistem")
            st.markdown("</div>", unsafe_allow_html=True)

            with st.container():
                user_input = st.text_input("Username", placeholder="Masukkan username anda")
                pass_input = st.text_input("Password", type="password", placeholder="Masukkan password anda")
                login_btn = st.button("Masuk Ke Sistem")
                
                if login_btn:
                    if user_input == USER_ADMIN and pass_input == PASS_ADMIN:
                        st.session_state.logged_in = True
                        st.success("Login Berhasil! Membuka dashboard...")
                        st.rerun()
                    else:
                        st.error("❌ Username atau Password salah!")
        return False
    return True

# --- PROGRAM UTAMA (JIKA SUDAH LOGIN) ---
if check_login():
    # Sidebar untuk info user dan logout
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
        st.write(f"Selamat Datang, **{USER_ADMIN}**")
        st.divider()
        if st.button("🚪 Keluar (Logout)"):
            st.session_state.logged_in = False
            st.rerun()

    # Konten Dashboard Anda
    st.title("🚚 Input Surat Jalan Pabrik")
    # ... (lanjutkan dengan form input data seperti sebelumnya)
