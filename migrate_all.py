"""
migrate_all.py
--------------
Jalankan SEKALI untuk:
1. Import semua menu dari menu_data.py ke MySQL

    python migrate_all.py
"""

from db_connection import get_connection
from menu_data import MENU
from storage import migrate_from_json
from mysql.connector import Error


def migrate_menu():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("TRUNCATE TABLE menu_item")
        cursor.execute("TRUNCATE TABLE kategori")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        for urutan, (nama_kat, items) in enumerate(MENU.items(), start=1):
            cursor.execute(
                "INSERT INTO kategori (nama, urutan) VALUES (%s, %s)",
                (nama_kat, urutan)
            )
            kat_id = cursor.lastrowid
            print(f"  Kategori [{kat_id}] {nama_kat}")

            for item in items:
                cursor.execute(
                    "INSERT INTO menu_item (kategori_id, nama, deskripsi, harga, badge) VALUES (%s,%s,%s,%s,%s)",
                    (kat_id, item["nama"], item["deskripsi"], item["harga"], item.get("badge"))
                )
                print(f"    └─ {item['nama']}")

        conn.commit()
        print("✅ Menu berhasil diimport.\n")
    except Error as e:
        conn.rollback()
        print(f"❌ Error menu: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("=== Migrasi Menu ===")
    migrate_menu()

    print("\n🎉 Selesai! Semua data sudah masuk ke MySQL.")