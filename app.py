# --- SISTEM LOGIN (COLORFUL EDITION) ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    # Custom CSS untuk Background Gradasi dan Card Login
    st.markdown("""
        <style>
        /* Mengubah background seluruh halaman login */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        /* Style untuk kotak login */
        .login-card {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            text-align: center;
        }
        .login-title {
            color: #4a4a4a;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 800;
            margin-bottom: 10px;
        }
        /* Mempercantik input field */
        .stTextInput>div>div>input {
            border-radius: 10px;
        }
        /* Tombol Login Berwarna */
        div.stButton > button:first-child {
            background: linear-gradient(to right, #6a11cb 0%, #2575fc 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 18px;
            transition: 0.3s;
        }
        div.stButton > button:first-child:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        </style>
    """, unsafe_allow_html=True)

    _, col_mid, _ = st.columns([1, 1.5, 1])
    
    with col_mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Pembungkus Card Login
        with st.container():
            st.markdown("""
                <div class="login-card">
                    <img src="https://cdn-icons-png.flaticon.com/512/5637/5637217.png" width="80">
                    <h1 class="login-title">LOGISTICS PORTAL</h1>
                    <p style="color: #666;">Silakan masukkan kredensial Anda</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Form login diletakkan di bawah visual card
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="Admin ID")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("MASUK SEKARANG")
                
                if submit:
                    if u == USER_ADMIN and p == PASS_ADMIN:
                        st.session_state["logged_in"] = True
                        st.balloons() # Efek balon saat berhasil login
                        st.rerun()
                    else:
                        st.error("Username atau Password salah!")
    st.stop()
