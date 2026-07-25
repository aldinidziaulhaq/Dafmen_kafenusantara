import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
import os
from pathlib import Path
import streamlit as st # <--- Pastikan streamlit di-import

def _get_config():
    # Helper untuk mendapatkan path sertifikat
    ca_cert_path = str(Path(__file__).resolve().parent / "ca.pem")
    
    try:
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

# 1. KUNCI KOLAM MENGGUNAKAN CACHE STREAMLIT
# Ini akan mencegah pembuatan kolam baru setiap 5 detik saat auto-refresh
@st.cache_resource
def get_connection_pool():
    try:
        pool = MySQLConnectionPool(
            pool_name="cafe_pool",
            pool_size=10,            # Naikkan sedikit jadi 10 agar antrean lebih lega
            pool_reset_session=True, 
            **_get_config()
        )
        return pool
    except Error as e:
        raise ConnectionError(f"Gagal membuat connection pool: {e}")

def get_connection():
    # 2. PANGGIL KOLAM DARI CACHE
    db_pool = get_connection_pool()
    
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