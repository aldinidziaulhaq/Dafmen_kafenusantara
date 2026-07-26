import mysql.connector
from mysql.connector import pooling
import streamlit as st

# Menggunakan cache_resource agar pool tidak dibuat berulang kali saat layar refresh
@st.cache_resource (show_spinner=False)
def get_connection_pool():
    dbconfig = {
        "host": st.secrets["mysql"]["host"],
        "user": st.secrets["mysql"]["user"],
        "password": st.secrets["mysql"]["password"],
        "database": st.secrets["mysql"]["database"],
        "port": st.secrets["mysql"].get("port", 3306),
        "autocommit": True  # Otomatis commit untuk operasi INSERT/UPDATE
    }
    # pool_size=5 sangat aman untuk shared-hosting/PlanetScale tanpa menyebabkan overload
    return pooling.MySQLConnectionPool(pool_name="kafe_pool", pool_size=5, **dbconfig)

# Inisialisasi pool
pool = get_connection_pool()

def execute_query(query, params=None, fetch=False):
    connection = None
    cursor = None
    try:
        # Mengambil koneksi yang nganggur dari pool
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(query, params or ())
        
        if fetch:
            return cursor.fetchall()
        else:
            connection.commit()
            
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None if fetch else False
        
    finally:
        # Pastikan cursor ditutup
        if cursor:
            cursor.close()
        # Mengembalikan koneksi ke pool (BUKAN menutup/memutus total)
        if connection and connection.is_connected():
            connection.close()