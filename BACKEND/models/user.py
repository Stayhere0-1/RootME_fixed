from flask import jsonify, redirect, make_response
import mysql.connector
from .database import database
from flask_jwt_extended import create_access_token
import datetime

class UserModel:
    def __init__(self, db_config):
        self.db = database(db_config)

    def username_exist(self, username):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT username FROM User WHERE username = %s", (username,))
            exist = cursor.fetchone() is not None
            return exist  # Kembalikan boolean saja

        except Exception as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def email_exist(self, mail):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT Mail FROM User WHERE mail = %s", (mail,))
            exist = cursor.fetchone() is not None
            return exist  # Kembalikan boolean saja

        except Exception as e:
            print(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def create_user(self, username, password, mail, role="Player"):
        conn = None
        cursor = None
        try:
            # Cek username terlebih dahulu
            if self.username_exist(username):
                return jsonify({
                    "message": "Username already exists",
                    "status": "failed"
                }), 409

            conn = self.db.get_con()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO User (username, mail, password_md5, role) VALUES (%s, %s, %s, %s)",
                (username, mail, password, role)
            )
            conn.commit()

            return jsonify({
                "message": "User  created successfully",
                "status": "success"
            }), 201

        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            return jsonify({
                "message": "Database error",
                "error": str(e),
                "status": "failed"
            }), 500
        except Exception as e:
            if conn:
                conn.rollback()
            return jsonify({
                "message": "Unexpected error",
                "error": str(e),
                "status": "failed"
            }), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    def get_user_id(self, username):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT id FROM User WHERE username = %s", (username,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_kategori_id(self, kategori_name):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT Kategori_id FROM kategori_soal WHERE Kategori_name = %s"
            cursor.execute(query, (kategori_name,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            print(e)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()            
    def validate_user(self, username, password):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            cursor.execute("SELECT id, password_md5, role FROM User WHERE username = %s", (username,))
            row = cursor.fetchone()
            
            if row and row[1] == password:
                buat_cookie = {
                    "username": username,
                    "role": row[2]
                }
                
                expires = datetime.timedelta(hours=3)
                access_token = create_access_token(
                    identity=row[0],
                    additional_claims=buat_cookie,
                    expires_delta=expires
                )
                
                return {
                    "status": "success",
                    "message": "Login successful",
                    "access_token": access_token
                }, 200
            else:
                return {
                    "status": "failed",
                    "message": "Invalid username or password"
                }, 401

        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def create_soal(self, kategori_id, soal_name, soal_isi, attachment, koneksi_info, value, flag):
            try:
                conn = self.db.get_con()
                cursor = conn.cursor()
                query = """
                    INSERT INTO soal (Kategori_id, Soal_name, Soal_Isi, Attachment, Koneksi_Info, Value, flag)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (kategori_id, soal_name, soal_isi, attachment, koneksi_info, value,flag))
                conn.commit()
                return {"message": "Soal created successfully", "status": "success"}
            except mysql.connector.Error as err:
                return {"message": "Failed to create soal", "error": str(err), "status": "failed"}
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

    def edit_soal(self, soal_name, soal_isi,attachment, koneksi_info, new_value,flag, soal_id):
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            # 1) Ambil old_value (poin lama) dari tabel soal
            cursor.execute("SELECT Value FROM soal WHERE soal_id = %s", (soal_id,))
            row = cursor.fetchone()
            if not row:
                return {"message": "Soal not found", "status": "failed"}
            old_value = row[0]

            # Jika type None, anggap 0
            if not old_value:
                old_value = 0

            # 2) Bandingkan old_value & new_value
            if new_value != old_value:
                diff = new_value - old_value  # bisa positif / negatif

                # 3) Cari user mana saja yang solve soal ini (status=Benar)
                #    Misal kolom 'status' = 'Benar' di tabel 'submit'
                #    user_id di kolom 'ID'
                cursor.execute("""
                    SELECT ID
                    FROM submit
                    WHERE Soal_ID = %s AND Benar_Salah = 'Benar'
                """, (soal_id,))
                solved_users = cursor.fetchall()  # list of (user_id,)

                # 4) Update poin user
                for (user_id,) in solved_users:
                    # ambil total_point user sekarang
                    cursor.execute("SELECT total_point FROM leaderboard WHERE ID = %s", (user_id,))
                    user_row = cursor.fetchone()
                    if user_row:
                        current_point = user_row[0] or 0
                        new_point = current_point + diff

                        # optional: jangan sampai minus
                        if new_point < 0:
                            new_point = 0

                        cursor.execute("""
                            UPDATE leaderboard 
                            SET total_point = %s
                            WHERE ID = %s
                        """, (new_point, user_id))

            # 5) Update data soal di DB
            query = """
                UPDATE soal
                SET Soal_name = %s,
                    Soal_Isi  = %s,
                    Attachment= %s,
                    Koneksi_Info = %s,
                    Value     = %s,
                    flag      = %s
                WHERE soal_id = %s
            """
            cursor.execute(query, (soal_name, soal_isi, attachment, koneksi_info, new_value, flag, soal_id))

            conn.commit()
            return {"message": "Soal updated successfully", "status": "success"}

        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return {"message": "Failed to update soal", "error": str(err), "status": "failed"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_soal(self, soal_id):
        try:
            conn = self.db.get_con()
            cursor = conn.cursor()
            # 1) Cari nilai point dari soal
            cursor.execute("SELECT Value FROM soal WHERE soal_id = %s", (soal_id,))
            row = cursor.fetchone()
            if not row:
                return {"message": "Soal not found", "status": "failed"}
            soal_point = row[0]

            # 2) Cari semua user_id yang sudah menjawab soal ini dengan status benar
            #    Misal status `Benar` di kolom `status` pada tabel `submit`
            cursor.execute("""
                SELECT ID 
                FROM submit
                WHERE Soal_ID = %s AND Benar_Salah = 'Benar'
            """, (soal_id,))
            user_ids = cursor.fetchall()  # list of tuples (user_id,)

            # Jika tidak ada user yang pernah solve soal ini
            if user_ids:
                # 3) Untuk masing-masing user, ambil total_point
                #    Lalu kurangi dengan `soal_point`
                for (u_id,) in user_ids:
                    # Ambil total point user
                    cursor.execute("SELECT total_point FROM leaderboard WHERE ID = %s", (u_id,))
                    user_row = cursor.fetchone()
                    if user_row:
                        current_point = user_row[0] or 0
                        new_point = current_point - soal_point
                        if new_point < 0:
                            new_point = 0  # misal tidak boleh minus

                        # 4) Update total point user
                        cursor.execute(
                            "UPDATE leaderboard SET total_point = %s WHERE ID = %s",
                            (new_point, u_id)
                        )

            # 5) Hapus data soal
            cursor.execute("DELETE FROM soal WHERE soal_id = %s", (soal_id,))
            conn.commit()

            return {
                "message": "Soal deleted successfully",
                "status": "success"
            }

        except mysql.connector.Error as err:
            return {
                "message": "Failed to delete soal",
                "error": str(err),
                "status": "failed"
            }
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        
    
    
    #GET MAIL from DATABASE baseon Username
    def get_mail(self, username):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            
            query = "SELECT mail FROM User WHERE username = %s"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "status": "success",
                    "mail": row[0]
                }, 200
            else:
                return {
                    "status": "failed",
                    "message": "User not found"
                }, 404

        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    def change_pass(self, mail, new_pass):
        print("MAIL:",mail)
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "UPDATE User SET password_md5 = %s WHERE mail = %s"
            cursor.execute(query, (new_pass,mail ))
            conn.commit()
            
            return jsonify({
                "message": "Password updated successfully",
                "status": "success"
            }), 200
        
        #DEBUG DEFAULT:)
        except mysql.connector.Error as e:
            if conn:
                conn.rollback()
            return jsonify({
                "message": "Database error",
                "error": str(e),
                "status": "failed"
            }), 500
        except Exception as e:
            if conn:
                conn.rollback()
            return jsonify({
                "message": "Unexpected error",
                "error": str(e),
                "status": "failed"
            }), 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def isuserSubmit(self, user_id, soal_id):
        print(user_id)
        print(soal_id)
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)

        try: 
            query = "SELECT Benar_Salah FROM submit WHERE ID=%s AND soal_id=%s AND Benar_Salah='Benar' LIMIT 1"
            cursor.execute(query, (user_id, soal_id))
            result = cursor.fetchone()
            if result:
                print(result)
                if result[0] == "Benar":
                    return True
                else:
                    return False
            else :
                return False
        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close() 

    def submit_flag(self, user_id, soal_id, flag):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT flag, Value FROM soal WHERE Soal_id = %s"
            cursor.execute(query, (soal_id,))
            row = cursor.fetchone()
            
            if row:
                correct_flag = row[0]
                value = row[1]
                status = 'Benar' if correct_flag == flag else 'Salah'
                
                if status == 'Benar':
                    print(soal_id)
                    cek_IsSolve = self.isuserSubmit(user_id, soal_id)
                    print(cek_IsSolve)
                    
                    if cek_IsSolve == True:
                        return {
                        "status": "failed",
                        "message": "Sudah solve"
                    },200
                    else: 
                        query = "SELECT Total_Point FROM leaderboard WHERE ID = %s"
                        cursor.execute(query, (user_id,))
                        row = cursor.fetchone()
                        
                        if row:
                            total_point = row[0] + value
                            query = "UPDATE leaderboard SET Total_Point = %s WHERE ID = %s"
                            cursor.execute(query, (total_point, user_id))
                        else:
                            query = "INSERT INTO leaderboard (ID, Total_Point) VALUES (%s, %s)"
                            cursor.execute(query, (user_id, value))

                        query1 = """
                        INSERT INTO submit (ID, Soal_ID, Record_Submit, Benar_Salah)
                        VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(query1, (user_id, soal_id, flag, status))
                        conn.commit()
                        
                        return {
                            "status": "success",
                            "message": "Flag submitted successfully"
                        }, 200
                else:
                    query1 = """
                        INSERT INTO submit (ID, Soal_ID, Record_Submit, Benar_Salah)
                        VALUES (%s, %s, %s, %s)
                        """
                    cursor.execute(query1, (user_id, soal_id, flag, status))
                    conn.commit()

                    return {
                        "status": "failed",
                        "message": "Incorrect flag"
                    }, 400
                
                
            else:
                return {
                    "status": "failed",
                    "message": "Soal not found"
                }, 404

        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_leaderboard(self):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = """
                SELECT u.Username, l.Total_Point
                FROM leaderboard l
                JOIN User u ON l.ID = u.ID
                ORDER BY l.Total_Point DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            leaderboard = [{"username": row[0], "total_point": row[1]} for row in rows]
            return {
                "leaderboard": leaderboard
            }, 200

        except mysql.connector.Error as e:
            return {
                "status": "failed",
                "message": "Database error",
                "error": str(e)
            }, 500
        except Exception as e:
            return {
                "status": "failed",
                "message": "Unexpected error",
                "error": str(e)
            }, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    #GET LOG
    def log(self):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT user.Username AS user_name, soal.Soal_name AS soal_name, submit.Benar_Salah AS status, submit.Record_Submit AS flag FROM submit JOIN user ON submit.ID = user.id JOIN soal ON submit.soal_id = soal.Soal_id"
            cursor.execute(query)
            rows = cursor.fetchall()
            return {"status": "success", "data": rows}, 200
        except:
            return {"status": "failed", "message": "Database error"}, 500
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # GET SOAL by KATEGORI
    def getSoalByKategori(self, kategori):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "Select * from soal where kategori_id = %s"
            cursor.execute(query, (kategori,))
            rows = cursor.fetchall()
            return {"data": rows}, 200
        except mysql.connector.Error as e:
            return {"status": "failed", "message": "Database error"}, 500

    #GET KATEGORI
    def get_kat(self):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT Kategori_id, Kategori_name FROM kategori_soal"
            cursor.execute(query)
            categories = cursor.fetchall()  # [(1, 'Blockchain'), (2, 'Web Exploitation'), ...]

            return jsonify({"categories": categories}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def massSoalTrue(self,id):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "Select Soal_ID from submit where Benar_Salah = 'Benar' and id = %s"
            cursor.execute(query,(id,))
            rows = cursor.fetchall()
            # Rturn json
            return {"data": rows}, 200
        except Exception as e:
            return {"status": "failed", "message": e}, 500
    
    def cekUsername(self,id):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT Username FROM user WHERE id = %s"
            cursor.execute(query, (id,))
            rows = cursor.fetchall()
            return {"data": rows}, 200
        except Exception as e:
            return {"status": "failed", "message":e}, 500
    
    def getALLSoal(self):
        conn = self.db.get_con()
        cursor = conn.cursor(buffered=True)
        try:
            query = "SELECT soal.soal_id, kategori_soal.kategori_name AS kategori, soal.soal_name, soal.soal_isi, soal.attachment, soal.koneksi_info, soal.value FROM soal JOIN kategori_soal ON soal.kategori_id = kategori_soal.kategori_id"
            cursor.execute(query)
            rows = cursor.fetchall()
            return {"data": rows}, 200
        except Exception as e:
            return {"status": "failed", "message": e}, 500
        


        
        


    


