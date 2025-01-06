import streamlit as st
import json
import os
import jwt
from flask import redirect
import requests
import pandas as pd

SECRET_KEY = "peduliapagwbjirwkwkakujugamalas!@^^*!******00012839"
API_BASE_URL = "http://localhost:5000/admin/api"

# Fungsi untuk mendapatkan daftar kategori dari API
def get_categories():
    try:
        response = requests.get(f"http://localhost:5000//categories")  # Endpoint untuk mengambil kategori
        if response.status_code == 200:
            data = response.json()
            categories = {cat[1]: cat[0] for cat in data["categories"]}  # Mapping nama kategori ke ID
            return categories
        else:
            st.error(f"Gagal mengambil data kategori. Status code: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"Error: {e}")
        return {}

# Fungsi untuk redirect ke halaman login
def redirect_to_login():
    redirect_html = """
    <meta http-equiv="refresh" content="0; url=http://localhost:5000/logout">
    <p>Redirecting to <a href="http://localhost:5000/logout">http://localhost:5000/logout</a></p>
    """
    
    st.markdown(redirect_html, unsafe_allow_html=True)
    requests.get("http://localhost:5000/logout")
    st.stop()

# Fungsi untuk memvalidasi token
def validate_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        st.error("Token sudah kedaluwarsa.")
        return None
    except jwt.InvalidTokenError:
        st.error("Token tidak valid.")
        return None

# Fungsi untuk memeriksa autentikasi
def check_authentication():
    token = st.query_params.get("token", None)

    if token is None:
        redirect_to_login()
    
    decoded_token = validate_token(token)
    if not decoded_token:
        redirect_to_login()
    
    st.session_state["token"] = token
    st.session_state["user"] = decoded_token["sub"]
    st.session_state["role"] = decoded_token.get("role")

    return decoded_token.get("role")

# Fungsi untuk mengambil soal berdasarkan kategori
def get_questions_by_category(kategori_id):
    try:
        response = requests.get(f"{API_BASE_URL}/soal/{kategori_id}")
        if response.status_code == 200:
            return response.json()  # Mengembalikan list soal
        else:
            st.error(f"Gagal mengambil soal untuk kategori: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error mengambil soal: {e}")
        return []

# Fungsi untuk menghapus soal
def delete_question(soal_id, token):
    try:
        response = requests.delete(f"{API_BASE_URL}/delSoal/{soal_id}/{token}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Gagal menghapus soal: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error menghapus soal: {e}")
        return None

# === Admin Panel ===
def admin_panel():
    # Sidebar menu
    st.sidebar.title("Admin Panel")
    menu = st.sidebar.radio("Menu", ["Buat Soal", "Edit Soal", "Delete Soal", "Log Jawaban"])

    # ========== Tombol Logout di Sidebar (ADMIN) ==========
    # Tambahan LOGOUT
    if st.sidebar.button("Logout"):
        # Panggil endpoint logout di server
        redirect_to_login()
        requests.get("http://localhost:5000/logout")

        st.session_state.clear()
        st.success("Anda sudah logout. Silakan tutup tab atau kembali ke halaman login.")
        st.stop()

    # Ambil kategori soal dari API
    categories = get_categories()

    # === Menu Buat Soal ===
    if menu == "Buat Soal":
        st.title("Buat Soal Baru")
        
        # Dropdown untuk memilih kategori berdasarkan API
        if categories:
            category_name = st.selectbox("Pilih Kategori Soal", list(categories.keys()))  # Nama kategori
            kategori_id = categories[category_name]  # Ambil ID kategori berdasarkan nama yang dipilih

            # Input data soal lainnya
            name = st.text_input("Nama Soal")
            description = st.text_area("Deskripsi Soal")
            flag = st.text_input("Flag")
            point = st.number_input("Poin", min_value=1, max_value=1000, step=1)
            attachment = st.text_input("Lampiran (Opsional)")
            konek_info = st.text_input("Informasi Koneksi (Opsional)")

            if st.button("Tambahkan Soal"):
                # Buat data soal dalam format JSON
                soal_data = {
                    "Kategori_id": kategori_id,
                    "name": name,
                    "description": description,
                    "flag": flag,
                    "point": point,
                    "attachment": attachment,
                    "konek_info": konek_info,
                }

                # Kirim data ke API
                try:
                    token = st.session_state["token"]
                    response = requests.post(f"{API_BASE_URL}/createSoal/{token}", json=soal_data)
                    if response.status_code == 200:
                        st.success("Soal berhasil ditambahkan!")
                    else:
                        st.error(f"Gagal menambahkan soal: {response.status_code}")
                        st.json(response.json())
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.error("Tidak ada kategori tersedia. Pastikan API berjalan dengan benar.")

    # === Menu Edit Soal ===
    elif menu == "Edit Soal":
        st.title("Edit Soal")
        
        # Dropdown untuk memilih kategori berdasarkan API
        if categories:
            category_name = st.selectbox("Pilih Kategori Soal", list(categories.keys()))  # Nama kategori
            kategori_id = categories[category_name]  # Ambil ID kategori berdasarkan nama yang dipilih

            # Ambil soal berdasarkan kategori
            questions = get_questions_by_category(kategori_id)
            raw_questions = questions.get("data", [])
            questions = [
                {
                    "id": q[0], 
                    "name": q[2],
                    "Deskripsi": q[3], 
                    "Attachment": q[4], 
                    "Konek Info": q[5],
                    "point": q[6],
                    "flag": q[7]
                } for q in raw_questions
            ]
            if questions:
                # Dropdown untuk memilih soal
                question_name = st.selectbox(
                    "Pilih Soal", 
                    [q["name"] for q in questions]  # Nama soal untuk ditampilkan di dropdown
                )
                selected_question = next(q for q in questions if q["name"] == question_name)

                # Form untuk mengedit soal
                st.subheader("Edit Soal")
                name = st.text_input("Nama Soal", selected_question["name"])
                description = st.text_area("Deskripsi Soal", selected_question["Deskripsi"])
                flag = st.text_input("Flag", selected_question["flag"])
                point = st.number_input("Poin", min_value=1, max_value=1000, value=int(selected_question["point"]), step=1)
                attachment = st.text_input("Lampiran (Opsional)", selected_question.get("Attachment", ""))
                konek_info = st.text_input("Informasi Koneksi (Opsional)", selected_question.get("Konek Info", ""))

                if st.button("Simpan Perubahan"):
                    # Buat data soal dalam format JSON
                    soal_data = {
                        "name": name,
                        "description": description,
                        "flag": flag,
                        "point": point,
                        "attachment": attachment,
                        "konek_info": konek_info,
                    }

                    # Kirim data ke API
                    try:
                        token = st.session_state["token"]
                        response = requests.put(f"{API_BASE_URL}/soal_mov/{selected_question['id']}/{token}", json=soal_data)
                        if response.status_code == 200:
                            st.success("Soal berhasil diperbarui!")
                        else:
                            st.error(f"Gagal memperbarui soal: {response.status_code}")
                            st.json(response.json())
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Tidak ada soal untuk kategori ini.")
        else:
            st.error("Tidak ada kategori tersedia. Pastikan API berjalan dengan benar.")

    # === Menu Delete Soal ===
    elif menu == "Delete Soal":
        st.title("Hapus Soal")
        categories = get_categories()

        if categories:
            # Dropdown untuk memilih kategori
            category_name = st.selectbox("Pilih Kategori", list(categories.keys()))
            kategori_id = categories[category_name]

            questions = get_questions_by_category(kategori_id)
            raw_questions = questions.get("data", [])
            questions = [{"id": q[0], "name": q[2]} for q in raw_questions]

            if questions:
                # Dropdown untuk memilih soal
                question_name = st.selectbox(
                    "Pilih Soal",
                    [q["name"] for q in questions]
                )
                selected_question = next(q for q in questions if q["name"] == question_name)

                if st.button("Hapus Soal"):
                    token = st.session_state["token"]
                    response = delete_question(selected_question["id"], token)
                    if response:
                        st.success("Soal berhasil dihapus!")
            else:
                st.warning("Tidak ada soal di kategori ini.")
        else:
            st.error("Kategori tidak ditemukan.")

    elif menu == "Log Jawaban":
        st.title("Log Jawaban")
        token = st.query_params.get("token", None)
        log_jawaban = requests.get(f"http://localhost:5000/admin/api/log/{token}")
        log_jawaban = log_jawaban.json()
        raw_data = log_jawaban[0]["data"]
        columns = ["user_name", "soal_name", "status", "flag"]
        log_jawaban = pd.DataFrame(raw_data, columns=columns)
        

        if not log_jawaban.empty:
            st.write("Berikut adalah **log jawaban** dari pengguna yang telah dikirimkan ke sistem:")

            st.sidebar.header("Filter Data")
            username_filter = st.sidebar.multiselect("Pilih Username", options=log_jawaban["user_name"].unique())
            status_filter = st.sidebar.radio("Pilih Status Jawaban", options=["Semua", "Benar", "Salah"])

            filtered_data = log_jawaban
            if username_filter:
                filtered_data = filtered_data[filtered_data["user_name"].isin(username_filter)]
            if status_filter != "Semua":
                filtered_data = filtered_data[filtered_data["status"] == status_filter]

            def highlight_row(row):
                if row.status == "Benar":
                    return ['background-color: #d4edda; color: #155724;'] * len(row)
                else:
                    return ['background-color: #f8d7da; color: #721c24;'] * len(row)

            st.dataframe(filtered_data.style.apply(highlight_row, axis=1),use_container_width=True)

            st.write("### Statistik Log Jawaban")
            total_jawaban = len(log_jawaban)
            total_benar = len(log_jawaban[log_jawaban["status"] == "Benar"])
            total_salah = len(log_jawaban[log_jawaban["status"] == "Salah"])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Jawaban", total_jawaban)
            with col2:
                st.metric("Jawaban Benar", total_benar)
            with col3:
                st.metric("Jawaban Salah", total_salah)
        else:
            st.warning("Tidak ada data log jawaban yang tersedia.")


def player_panel():
    st.set_page_config(layout="wide", page_title="Player Panel", page_icon="🎮")

    # ===== Custom CSS untuk styling =====
    CUSTOM_CSS = """
    <style>

    /* Sidebar styling */
    .css-1cpxqw2 {
        background-color:rgb(34, 170, 175);
    }

    /* Teks sidebar */
    .css-1544g2n {
        color: #ffffff !important;
    }

    /* Judul challenge card */
    .challenge-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0px 1px 4px rgba(124, 172, 35, 0.81);
        transition: transform 0.2s ease;
    }
    .challenge-card:hover {
        transform: scale(1.02);
    }

    /* Challenge solved (hijau) */
    .challenge-solved {
        background-color: #d4edda; /* latar hijau lembut */
    }

    /* Container scoreboard (kanan) */
    .scoreboard-container {
        background-color: #f1f1f1;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0px 1px 4px rgba(0,0,0,0.2);
        margin-bottom: 16px;
    }

    /* Info player di scoreboard */
    .player-info-title {
        font-size: 220px;
        font-weight: bold;
        margin-bottom: 100px;
    }

    /* Scrollable log */
    .log-box {
        max-height: 200px;
        overflow-y: auto;
        background-color: #f1f3f5;
        padding: 10px;
        border-radius: 5px;
        font-size: 14px;
    }
    </style>
    """

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ========== Sidebar: Challenges + Logout (PLAYER) ==========
    st.sidebar.title("Challenges")
    category_list = ["All", "PWN", "Web Exploitation", "Reverse", "Forensics", "Cryptography", "Misc", "Mobile","Blockchain"]
    selected_category = st.sidebar.radio("Kategori", category_list, index=0)

    hide_solved = st.sidebar.checkbox("Hide Solved")

    # ========== Tombol Logout (PLAYER) ==========
    # Tambahan LOGOUT
    if st.sidebar.button("Logout"):
        # Panggil endpoint logout di server
        redirect_to_login()
        st.session_state.clear()
        st.success("Anda sudah logout. Silakan tutup tab atau kembali ke halaman login.")
        st.stop()

    # ========== Bagian Kanan: Scoreboard & Info Player ==========
    body_col1, body_col2 = st.columns([4, 1])  # 4:1 rasio lebar

    token = st.query_params.get("token", None)
    claims = validate_token(token)
    name = claims.get("username")

    # Data leaderboard
    leaderboard = requests.get(f"http://localhost:5000/rank").json()
    lb_dict = leaderboard[0]
    lb_list = lb_dict["leaderboard"]

    # Cari rank user
    player_rank = "N/A"
    player_score = 0
    found = False
    rank = "N/A"
    point = 0
    for i, item in enumerate(lb_list):
        if item["username"] == name:
            found = True
            rank = i + 1
            point = item["total_point"]
            break
    if found:
        player_rank = rank
        player_score = point
    else:
        player_rank = "N/A"
        player_score = 0

    with body_col2:
        st.markdown('<div class="scoreboard-container">', unsafe_allow_html=True)
        st.markdown("<h2 class='player-info-title'>Player Info</h2>", unsafe_allow_html=True)

        # Ambil data challenge (API)
        challenges_data = requests.get(f"http://localhost:5000/users/api/DATASOAL/{token}").json()

        solved_challenges = [item for item in challenges_data if item[7]]  # item[7] = apakah solved?
        total_challenges = len(challenges_data)
        solved_count = len(solved_challenges)

        st.write(f"**Username:** {name}")
        st.write(f"**Rank:** #{player_rank}")
        st.write(f"**Score:** {player_score}")
        st.write(f"**Solved Challenges:** {solved_count} / {total_challenges}")

        if total_challenges > 0:
            st.progress(solved_count / total_challenges)
        else:
            st.progress(0)

        st.write("---")
        st.write("# ==TOP 10 == #")
        for i, player in enumerate(lb_list[:10]):
            rank = i + 1
            username = player["username"]
            points = player["total_point"]

            if rank == 1:
                bg_color = "linear-gradient(to right,rgb(31, 96, 110), #56d4ff)"  # Diamond
            elif rank == 2:
                bg_color = "linear-gradient(to right,rgb(109, 92, 9),rgb(238, 217, 153))"  # Gold
            elif rank == 3:
                bg_color = "linear-gradient(to right,rgb(104, 80, 80),rgb(230, 225, 225))"  # Silver
            else:
                bg_color = "#000df"  # Default

            st.markdown(
                f"""
                <div style="
                    background: {bg_color};
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;">
                    <span style="font-weight: bold;">#{rank}</span>
                    <span>{username}</span>
                    <span style="font-weight: bold;">{points} pts</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ========== Bagian Tengah: Title + Grid Challenges ==========
    with body_col1:
        st.title(">$RootME CTF")
        st.caption("Go... Go... GO....")

        # Filter by selected_category
        filtered_challenges = []
        for item in challenges_data:
            c_id = item[0]
            c_cat = item[2]
            c_name = item[1]
            c_solved = item[-1]

            if selected_category != "All" and c_cat != selected_category:
                continue
            if hide_solved and c_solved:
                continue
            filtered_challenges.append(item)

        n_cols = 3
        rows = len(filtered_challenges) // n_cols + 1

        idx = 0
        for _r in range(rows):
            cols = st.columns(n_cols)
            for c in range(n_cols):
                if idx >= len(filtered_challenges):
                    break

                item = filtered_challenges[idx]
                idx += 1

                c_id       = item[0]
                c_cat      = item[2]
                c_name     = item[1]
                c_desc     = item[3]
                c_info     = item[4]
                c_ip       = item[5]
                c_score    = item[6]
                c_solved   = item[7]

                card_class = "challenge-card"
                if c_solved:
                    card_class += " challenge-solved"

                with cols[c]:
                    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
                    st.write(f"**{c_name}**")
                    st.write(f"**{c_score} pts**")
                    st.write(f"Kategori: {c_cat}")

                    with st.expander("Detail & Submit Flag"):
                        st.write(f"**Deskripsi:** {c_desc}")
                        st.write(f"**Info:** {c_info}")
                        st.write(f"**IP/Host:** {c_ip}")
                        st.write(f"Status: {'Solved' if c_solved else 'Unsolved'}")

                        user_flag = st.text_input(f"Submit Flag untuk '{c_name}'", key=f"flag_{c_id}")
                        if st.button(f"Kirim Flag {c_id}", key=f"btn_{c_id}"):
                            token = st.session_state.get("token", None)
                            if not token:
                                st.error("Anda belum login atau token tidak ditemukan.")
                            else:
                                submit_url = f"http://localhost:5000/submit_flag/{token}"
                                payload = {
                                    "flag": user_flag,
                                    "soal_id": c_id
                                }
                                try:
                                    response = requests.post(submit_url, json=payload)
                                    if response.status_code == 200:
                                        st.rerun()
                                        st.success("Flag submitted: correct")
                                    else:
                                        st.error("Gagal submit flag: Incorrect")
                                except Exception as e:
                                    st.error(f"Terjadi kesalahan saat submit flag: {e}")

                    st.markdown("</div>", unsafe_allow_html=True)
        st.write("")  # spacing at bottom

# Tentukan panel berdasarkan role
role = check_authentication()
if role == "Admin":
    admin_panel()
else:
    player_panel()
