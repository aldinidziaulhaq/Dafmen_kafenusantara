from db_connection import execute_query

try:
    execute_query("ALTER TABLE pesanan ADD COLUMN metode_pembayaran VARCHAR(50) DEFAULT 'Cash (Bayar di Kasir)';")
    print("✅ Kolom metode_pembayaran berhasil ditambahkan ke database!")
except Exception as e:
    print("Gagal atau kolom sudah ada:", e)