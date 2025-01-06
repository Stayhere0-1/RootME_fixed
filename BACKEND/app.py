from flask import Flask, request, jsonify, make_response, redirect, render_template
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, set_access_cookies, get_jwt, verify_jwt_in_request, unset_jwt_cookies
from models.user import UserModel
import os
import re
from datetime import timedelta
import hashlib
from functools import wraps
from recovery import send_reset_email, generate_reset_link, verify_reset_token
import urllib.parse
import jwt as jwt1




STREAMLIT_URL = "http://localhost:8501"
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'peduliapagwbjirwkwkakujugamalas!@^^*!******00012839')
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF untuk testing
app.config['JWT_COOKIE_SECURE'] = False  # Set True jika menggunakan HTTPS
jwt = JWTManager(app)

DB_CONFIG = {
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'database': os.environ.get('DB_NAME', 'rootme_db')
}
JWT_SECRET_KEY = "peduliapagwbjirwkwkakujugamalas!@^^*!******00012839" 
user_model = UserModel(DB_CONFIG)

def jwt_cookie_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request(locations=['cookies'])
                return fn(*args, **kwargs)
            except Exception as e:
                return redirect("/")
        return decorator
    return wrapper

def md5encrypt(string):
    plain = string
    return hashlib.md5(plain.encode()).hexdigest()

def validate_token(token):
    try:
        decoded = jwt1.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        print(decoded)
        return decoded
    except jwt1.ExpiredSignatureError:
        return None
    except jwt1.InvalidTokenError:
        return None
    
# HALAMAN INDEX
@app.route('/', methods=['GET'])
def index():
    try:
        # Try to verify the JWT token from cookies
        verify_jwt_in_request(locations=['cookies'])
        claims = get_jwt()
        print(claims)
        role = claims.get("role")
        if role == "Admin" or role == "Player":
            return redirect("/dashboard")
        else :
            return redirect("/")
    except Exception as e:
        # If token is invalid or missing, render the index page
        pass
    return render_template('index.html')

# API REGISTER
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        print(username,password,email)
        # Validasi data ada atau tidak
        if not username or not password or not email:
            return jsonify({"message": "Missing fields"}), 400

        # Validasi panjang username dan password
        if len(username) < 8 or len(password) < 8:
            return jsonify({"message": "Username and password must be at least 8 characters"}), 400

        # Validasi format email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"message": "Invalid email"}), 400

        # Validasi password setidaknya punya huruf besar, huruf kecil, dan angka
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", password):
            return jsonify({"message": "Password must contain at least one lowercase letter, one uppercase letter, one digit, and minimum 8 characters"}), 400

        hashed_password = md5encrypt(password)
        return user_model.create_user(username, hashed_password, email)

    except Exception as e:
        print(e)
        return jsonify({"message": "Registration failed", "error": str(e)}), 400

# API LOGIN
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"message": "Missing fields"}), 400
        
        print(username,password)
        hashed_password = md5encrypt(password)
        print(hashed_password)
        result, status_code = user_model.validate_user(username, hashed_password)

        
        if status_code == 200:
            access_token = result["access_token"]
            response = jsonify({"message": "Login successful"})
            set_access_cookies(response, access_token)
            return response, 200
        else:
            return jsonify({"message": result.get('message')}), status_code
    except Exception as e:
        print(e)
        return jsonify({"message": "Login failed", "error": str(e)}), 400

# ADMIN

@app.route('/dashboard', methods=['GET'])
@jwt_cookie_required()
def admin():
    try:
        claims = get_jwt()
        role = claims.get("role")
        print(role)
        if role == "Admin" or role == "Player":
            print("AKU DISINI")
            #LEADER BOARD
            print(user_model.get_leaderboard())
            auth_token = request.cookies.get('access_token_cookie', 'Tidak ada cookie')
            query_params = urllib.parse.urlencode({"token": auth_token})
            # Kirimkan cookie dalam format JSON
            return redirect(f"{STREAMLIT_URL}?{query_params}")
        else:
            return redirect("/")
    except:
        return redirect("/")
    
@app.route("/admin/api/LOG/<token>", methods=['GET','POST'])
def log(token):
    try:    
        # Validasi token
        token = token
        # Validasi user
        claims = validate_token(token)
        role = claims.get("role")
        if role == "Admin":
            # Ambil data soal dari database
            soal = user_model.log()
            print(soal)
            return jsonify({"soal": soal}), 200
        #GET JSON
        else:
            return "CIHUY"
        
    except :
        return "SALAH APANYA "
# Endpoint untuk membuat soal

@app.route("/admin/api/createSoal/<token>", methods=['GET', 'POST'])
def create_soal(token):
    try:
        # Validasi token
        claims = validate_token(token)
        role = claims.get("role")

        # Hanya admin yang dapat mengakses endpoint ini
        if role != "Admin":
            return redirect('/')

        if request.method == 'POST':
            # Ambil data soal dari request JSON
            quest = request.json  # Membaca JSON dari body request
            print(quest)

            if not quest:
                return jsonify({"error": "JSON tidak ditemukan dalam request"}), 400
            print( quest)
            # Lakukan validasi data yang diterima
            kategori = quest.get("Kategori_id")
            print(kategori)
            nama = quest.get("name")
            deskripsi = quest.get("description")
            flag = quest.get("flag")
            point = quest.get("point")
            attachment = quest.get("attachment")
            kon_info = quest.get("konek_info")

            if not kategori or not nama or not deskripsi or not flag:
                return jsonify({"error": "Semua field (kategori, nama, deskripsi, flag) wajib diisi", "error1": kategori,"error2":nama}), 400

            # Simpan soal ke database (contoh, simpan ke log sebagai mock database)
            soal_baru = {
                "kategori": kategori,
                "nama": nama,
                "deskripsi": deskripsi,
                "flag": flag
            }
            res = user_model.create_soal(kategori,nama,deskripsi,attachment,kon_info,point,flag)
            # Contoh: Simpan ke log atau database
            print("Soal baru dibuat:", soal_baru)  # Debugging
            print(res)

            return jsonify({"message": "Soal berhasil dibuat", "soal": res}), 200

        # Jika metode GET, kembalikan template JSON sebagai panduan
        elif request.method == 'GET':
            return jsonify({
                "message": "Gunakan metode POST untuk membuat soal",
                "example": {
                    "kategori": "Kategori soal",
                    "nama": "Nama soal",
                    "deskripsi": "Deskripsi soal",
                    "flag": "CTF{example_flag}"
                }
            }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401  # Token tidak valid

    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

@app.route("/categories",methods=["GET"])
def get_categories():
    # Kembalikan kategori yang tersedia   
    return user_model.get_kat()

@app.route("/admin/api/soal/<kategori_id>",methods = ["GET"])
def get_soal(kategori_id):
    # Kembalikan soal berdasarkan kategori
    data = user_model.getSoalByKategori(kategori_id)
    print(data)
    return data

@app.route("/admin/api/soal_mov/<soal_id>/<token>", methods=["POST", "PUT"])
def updateSoal(soal_id, token):
    # Validasi token
    soal_id = soal_id
    print(soal_id)
    claims = validate_token(token)
    role = claims.get("role")
    if role != "Admin":
        return jsonify({"error": "Unauthorized"}), 403

    # Tangani metode POST dan PUT
    if request.method == 'POST' or request.method == 'PUT':
        # Ambil data soal dari request JSON
        quest = request.json  # Membaca JSON dari body request
        if not quest:
            return jsonify({"error": "JSON tidak ditemukan dalam request"}), 400

        # Lakukan validasi data yang diterima
        kategori = quest.get("Kategori_id")
        nama = quest.get("name")
        deskripsi = quest.get("description")
        flag = quest.get("flag")
        point = quest.get("point")
        attachment = quest.get("attachment")
        kon_info = quest.get("konek_info")

        if not nama or not deskripsi or not flag:
            return jsonify({
                "error": "Semua field (kategori, nama, deskripsi, flag) wajib diisi",
                "missing_fields": {
                    "nama": nama,
                    "deskripsi": deskripsi,
                    "flag": flag
                }
            }), 400

        # Simpan soal ke database
        res = user_model.edit_soal( nama, deskripsi, attachment, kon_info, point, flag, soal_id)
        print(res)
        if res:
            return jsonify({"message": "Soal berhasil diperbarui", "soal": res}), 200
        else:
            return jsonify({"error": "Gagal memperbarui soal"}), 500

    # Jika metode tidak dikenal
    return jsonify({"error": "Metode HTTP tidak dikenal"}), 405

@app.route("/admin/api/delSoal/<id>/<token>", methods = ["POST","DELETE"])   
def delete_soal(id,token):
    # Kembalikan soal berdasarkan kategori
    claims = validate_token(token)
    role = claims.get("role")
    if role != "Admin":
        return redirect("/")
    if request.method == 'DELETE':
        # Ambil data soal dari request JSON
        res = user_model.delete_soal(id)
        print(res)
        return res
    else :
        return jsonify({"message": "Method tidak dikenal"}), 405

@app.route("/users/api/DATASOAL/<token>", methods = ["GET"])   
def cekSolve(token):
    # Kembalikan soal berdasarkan kategori
    if token is None:
        return jsonify({"error": "Token tidak ditemukan"}), 401
    claims = validate_token(token)
    role = claims.get("role")
    username = claims.get("username")
    id = user_model.get_user_id(username)
    user1 = user_model.cekUsername(id)
    user1 = user1[0]
    user1 = user1['data'][0][0]
    if role != "Admin" and role != "Player":
        return redirect("/")
    if username != user1:
        return jsonify({"error": "Anda tidak memiliki akses untuk melihat soal ini"})
    dataSoal = user_model.getALLSoal()
    dataSoal = dataSoal[0]
    print(dataSoal)
    dataTrue = user_model.massSoalTrue(id)
    dataTrue = dataTrue[0]
    # Proses data
    benar_ids = {item[0] for item in dataTrue['data']}  # Ambil ID dari B, jika ada
    output = [
        (
            item[0],          # ID
            item[2],          # Nama Soal
            item[1],          # Kategori
            item[3],          # Deskripsi
            item[4],          # Info
            item[5],          # IP
            item[6],          # Skor
            item[0] in benar_ids  # True jika ID ada di B, False jika tidak
        )
        for item in dataSoal['data']
    ]
    print(output)
    return jsonify(output)

@app.route('/submit_flag/<token>', methods=['POST'])
def submit_flag(token):
    token = validate_token(token)
    role = token.get("role")
    username = token.get("username")
    id = user_model.get_user_id(username)
    if role != "Admin" and role != "Player":
        return jsonify({"error": "Anda tidak memiliki akses untuk mengirimkan flag"}),401
    data = request.json
    print(data)
    flag = data.get("flag")
    soal_id = data.get("soal_id")
    try:
        
        result, status_code = user_model.submit_flag(id, soal_id, flag)
        return jsonify(result), status_code 
    except Exception as e:
        return jsonify({"message": "Failed to submit flag", "error": str(e), "status": "failed", "soal_id": soal_id}), 400

@app.route("/rank", methods =["GET"])
def rank():
    data = user_model.get_leaderboard()
    return jsonify(data)

@app.route("/resetPass", methods = ["POST"])
def resetPass():
    data = request.json
    email = data.get("email")
    exist = user_model.email_exist(email)
    print(exist)
    if exist :
        reset_link = generate_reset_link(email)
        result = send_reset_email(email, reset_link)
        return jsonify(result)
    else :
        return jsonify({"message": "Email tidak ditemukan"}), 404

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'GET':
        return render_template('resetpass.html', token=token)
    try:
        email = verify_reset_token(token)
        if not email:
            return jsonify({"message": "Invalid or expired token", "status": "failed"}), 400
        
        new_password = request.form.get('password')
        # Validasi password setidaknya punya huruf besar, huruf kecil, dan angka
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$", new_password):
            return jsonify({"message": "Password must contain at least one lowercase letter, one uppercase letter, one digit, and minimum 8 characters"}), 400
        new_password = md5encrypt(new_password)
        user_model.change_pass(email, new_password)
        return jsonify({"message": "Password reset successful", "status": "success"})
    except Exception as e:
        return jsonify({"message": "Failed to reset password", "error": str(e), "status": "failed"}), 400

@app.route("/admin/api/log/<token>", methods = ["GET"])
def get_log(token):
    token = validate_token(token)
    role = token.get("role")
    if role == "Admin":
        data = user_model.log()
        return jsonify(data)
    else :
        return jsonify({"message": "Access denied"}), 403
    
@app.route('/logout', methods=['GET'])
def logout():
    # Buat respons untuk logout
    resp = make_response(redirect('http://localhost:5000/'))
    
    # Hapus cookie dengan mengatur nilainya menjadi kosong dan atur kadaluarsa ke 1 Jan 1970
    resp.set_cookie('access_token_cookie', '', expires=0)
    
    return resp
if __name__ == '__main__':
    app.run(debug=False)
