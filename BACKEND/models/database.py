import mysql.connector
from mysql.connector import errorcode

# Class Database
class database:
        def __init__(self, config):
                self.config = config
        
        # KONEKSI KE DATABASE
        def get_con(self):
                try:
                        conn = mysql.connector.connect(**self.config)
                        return conn
                except mysql.connector.Error as error :
                        if error.errno == errorcode.ER_ACCESS_DENIED_ERROR : 
                                raise Exception("SQL USERNAME ATAU PASSWORD SALAH")
                        elif error.errorno == error.ER_BAD_DB_ERROR :
                                raise Exception("Database tidak ditemukan atau anda salah masukan nama database")
                        else: 
                                raise Exception(error)
                        
