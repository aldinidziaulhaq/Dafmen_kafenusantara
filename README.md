# ☕ Kafe Nusantara — Sistem Pemesanan

Aplikasi pemesanan kafe berbasis Streamlit dengan dua tampilan:
- **Menu** (pelanggan) — browse menu & kirim pesanan
- **Kasir** — monitor pesanan real-time dengan auto-refresh

---

## Cara Menjalankan

### 1. Install dependensi
```bash
pip install streamlit
```

### 2. Jalankan aplikasi
```bash
streamlit run Menu.py
```


## Alur Kerja

```
Pelanggan (Menu.py)
  └─ Pilih menu → tambah ke keranjang → isi nomor meja → Pesan    

Kasir (pages/Kasir.py)  [auto-refresh tiap 40 detik]
  └─ Lihat pesanan BARU → klik Proses → klik Selesai
```
---

## Status Pesanan

| Status      | Warna  | Keterangan                        |
|-------------|--------|-----------------------------------|
| `baru`      | 🔴 Hijau | Pesanan baru masuk, belum diproses |
| `diproses`  | 🟡 Kuning | Sedang dibuat di dapur/bar        |
| `selesai`   | ⚫ Abu   | Sudah disajikan ke pelanggan      |

---

