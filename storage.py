"""
storage.py
----------
Semua operasi baca/tulis pesanan ke MySQL.
Menggantikan pesanan.json + file lock sebelumnya.
API-nya sengaja dibuat sama persis agar Menu.py & Kasir.py
tidak perlu banyak diubah.
"""

import uuid
from datetime import datetime
from db_connection import execute_query


# ─────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────

def load_orders() -> list:
    """
    Ambil semua pesanan beserta item-nya dari database MySQL.
    """
    pesanan_rows = execute_query(
        """
        SELECT id, meja, waktu, status, selesai_jam, metode_pembayaran
        FROM   pesanan
        WHERE status IN ('baru','diproses','selesai')
        ORDER  BY waktu DESC
        """,
        fetch=True,
    )

    result = []
    for p in pesanan_rows:
        items = execute_query(
            """
            SELECT nama_item AS nama, harga_satuan AS harga, jumlah AS qty
            FROM   pesanan_item
            WHERE  pesanan_id = %s
            """,
            (p["id"],),
            fetch=True,
        )
        result.append({
            "id":                p["id"],
            "meja":              p["meja"],
            "waktu":             str(p["waktu"]),
            "status":            p["status"],
            "selesai_jam":       str(p["selesai_jam"]) if p["selesai_jam"] else None,
            "metode_pembayaran": p.get("metode_pembayaran", "Cash"),
            "items":             items,
        })
    return result


def get_order_by_id(order_id: str) -> dict | None:
    """Ambil satu pesanan berdasarkan ID."""
    orders = load_orders()
    return next((o for o in orders if str(o["id"]) == str(order_id)), None)


def get_orders_by_status(status: str) -> list:
    """Ambil pesanan berdasarkan status: baru / diproses / selesai."""
    pesanan_rows = execute_query(
        """
        SELECT id, meja, waktu, status, selesai_jam
        FROM   pesanan
        WHERE  status = %s
        ORDER  BY waktu DESC
        """,
        (status,),
        fetch=True,
    )

    result = []
    for p in pesanan_rows:
        items = execute_query(
            "SELECT nama_item AS nama, harga_satuan AS harga, jumlah AS qty FROM pesanan_item WHERE pesanan_id = %s",
            (p["id"],),
            fetch=True,
        )
        result.append({
            "id":          p["id"],
            "meja":        p["meja"],
            "waktu":       str(p["waktu"]),
            "status":      p["status"],
            "selesai_jam": str(p["selesai_jam"]) if p["selesai_jam"] else None,
            "items":       items,
        })
    return result

def get_top_sellers_from_db(limit: int = 3) -> list:
    """Ambil top menu terlaris langsung dari database (jauh lebih ringan)."""
    query = """
        SELECT pi.nama_item, SUM(pi.jumlah) as total_terjual
        FROM pesanan_item pi
        JOIN pesanan p ON pi.pesanan_id = p.id
        WHERE p.status = 'selesai'
        GROUP BY pi.nama_item
        ORDER BY total_terjual DESC
        LIMIT %s
    """
    hasil = execute_query(query, (limit,), fetch=True)
    return [row["nama_item"] for row in hasil]

# ─────────────────────────────────────────────
# WRITE
# ─────────────────────────────────────────────

# Tambahkan argumen metode_pembayaran
def append_new_order(meja: str, items: list, metode_pembayaran: str = "Cash") -> str:
    order_id    = uuid.uuid4().hex[:8].upper()
    waktu_kini  = datetime.now().strftime("%H:%M:%S")
    total_harga = sum(i["harga"] * i["qty"] for i in items)

    # Tambahkan metode_pembayaran ke dalam query INSERT
    execute_query(
        """
        INSERT INTO pesanan (id, meja, total_harga, status, waktu, metode_pembayaran)
        VALUES (%s, %s, %s, 'baru', %s, %s)
        """,
        (order_id, meja, total_harga, waktu_kini, metode_pembayaran),
    )


    for item in items:
        execute_query(
            """
            INSERT INTO pesanan_item (pesanan_id, menu_item_id, nama_item, harga_satuan, jumlah)
            VALUES (%s,
                    (SELECT id FROM menu_item WHERE nama = %s LIMIT 1),
                    %s, %s, %s)
            """,
            (order_id, item["nama"], item["nama"], item["harga"], item["qty"]),
        )

    return order_id


def update_order_status(order_id: str, status: str) -> None:
    """Update status pesanan ke database."""
    if status == "selesai":
        # Gunakan 'datetime.now()' karena sudah diimport dari modul datetime
        waktu_selesai = datetime.now().strftime("%H:%M:%S")
        execute_query(
            "UPDATE pesanan SET status=%s, selesai_jam=%s WHERE id=%s",
            (status, waktu_selesai, str(order_id)),
        )
    else:
        # Menangani status 'diproses' dan 'batal'
        execute_query(
            "UPDATE pesanan SET status=%s WHERE id=%s",
            (status, str(order_id)),
        )


# ─────────────────────────────────────────────
# MIGRASI — import dari pesanan.json lama
# ─────────────────────────────────────────────

def migrate_from_json(json_path: str = "pesanan.json") -> int:
    """
    Import data lama dari pesanan.json ke MySQL.
    Jalankan sekali: python -c "from storage import migrate_from_json; migrate_from_json()"
    Return jumlah pesanan yang berhasil diimport.
    """
    import json, os
    if not os.path.exists(json_path):
        print(f"File {json_path} tidak ditemukan.")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        orders = json.load(f)

    count = 0
    for o in orders:
        order_id    = str(o["id"])
        total_harga = sum(i["harga"] * i.get("qty", 1) for i in o.get("items", []))

        # Skip jika sudah ada
        existing = execute_query(
            "SELECT id FROM pesanan WHERE id = %s", (order_id,), fetch=True
        )
        if existing:
            continue

        execute_query(
            """
            INSERT INTO pesanan (id, meja, total_harga, status, waktu, selesai_jam)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                order_id,
                o.get("meja", "-"),
                total_harga,
                o.get("status", "selesai"),
                o.get("waktu", "00:00:00"),
                o.get("selesai_jam"),
            ),
        )

        for item in o.get("items", []):
            execute_query(
                """
                INSERT INTO pesanan_item (pesanan_id, menu_item_id, nama_item, harga_satuan, jumlah)
                VALUES (%s,
                        (SELECT id FROM menu_item WHERE nama = %s LIMIT 1),
                        %s, %s, %s)
                """,
                (order_id, item["nama"], item["nama"], item["harga"], item.get("qty", 1)),
            )
        count += 1

    print(f"✅ Berhasil import {count} pesanan dari {json_path}")
    return count
def clear_all_done():
    """
    Hapus semua pesanan yang statusnya selesai (Hapus item dulu, baru pesanannya)
    """
    execute_query(
        """
        DELETE pi FROM pesanan_item pi 
        JOIN pesanan p ON pi.pesanan_id = p.id 
        WHERE p.status = 'selesai'
        """
    )
    execute_query(
        "DELETE FROM pesanan WHERE status = 'selesai'"
    )