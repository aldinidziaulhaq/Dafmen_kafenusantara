import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool # <--- Import fitur pooling
import os
from pathlib import Path

def _get_config():
    # Helper untuk mendapatkan path sertifikat
    ca_cert_path = str(Path(__file__).resolve().parent / "ca.pem")
    
    try:
        import streamlit as st
        cfg = st.secrets["mysql"]
        return {
            "host": cfg["host"],
            "port": int(cfg["port"]),
            "user": cfg["user"],
            "password": cfg["password"],
            "database": cfg["database"],
            "ssl_ca": ca_cert_path,
        }
    except (ImportError, FileNotFoundError, KeyError):
        from dotenv import load_dotenv
        env_path = Path(__file__).resolve().parent / ".env"
        load_dotenv(dotenv_path=env_path)

        return {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 3306)),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME"),
            "ssl_ca": ca_cert_path,
        }

# Variabel global untuk menyimpan pool agar tidak dibuat ulang
db_pool = None

def get_connection():
    global db_pool
    # Jika pool belum dibuat, buat satu kali saja dengan 5 koneksi standby
    if db_pool is None:
        try:
            db_pool = MySQLConnectionPool(
                pool_name="cafe_pool",
                pool_size=5,            # Menyiapkan 5 koneksi yang standby
                pool_reset_session=True, 
                **_get_config()
            )
        except Error as e:
            raise ConnectionError(f"Gagal membuat connection pool: {e}")
    
    # Ambil satu koneksi yang sedang nganggur dari pangkalan (pool)
    try:
        return db_pool.get_connection()
    except Error as e:
        raise ConnectionError(f"Gagal mengambil koneksi dari pool: {e}")

def execute_query(query, params=(), fetch=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            return result
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise RuntimeError(f"Query error: {e}")
    finally:
        cursor.close()
        # conn.close() di sini TIDAK lagi mematikan koneksi ke server,
        # melainkan hanya "mengembalikan taksi ke pangkalan (pool)"
        # agar bisa dipakai oleh query berikutnya.
        conn.close()