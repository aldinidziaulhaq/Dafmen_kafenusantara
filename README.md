# Kafe Nusantara — Sistem Pemesanan

Aplikasi pemesanan kafe berbasis Streamlit dengan dua tampilan:
- **Menu** (pelanggan) — browse menu & kirim pesanan
- **Kasir** (kasir) — monitor pesanan real-time dengan auto-refresh
- **Admin** (bos) - Riwayat penjualan, Diagram penjualan, Download excel & csv
---


## Alur Kerja

```
Pelanggan (menu.py)
  └─ Pilih menu → Tambah ke keranjang → Isi Nama → Pilih metode pembayaran → Pesan → Menunggu pesanan   

Kasir (kasir.py)  [auto-refresh tiap 60 detik]
  └─ Lihat pesanan BARU → klik Proses → klik Selesai

Admin (admin.py)
  └─ Lihat seluruh riwayat penjualan → Lihat menu terlaris → Download excel & csv
```
---

## Status Pesanan

| Status      | Warna  | Keterangan                        |
|-------------|--------|-----------------------------------|
| `Baru`      | 🔴 Merah | Pesanan baru masuk, belum diproses |
| `Diproses`  | 🟠 Oren | Sedang dibuat di dapur/bar        |
| `Selesai`   | 🟢 Hijau | Sudah disajikan ke pelanggan      |

---

## Akses

- [Menu_Dashboard](https://menu-kafenusantara-2026.streamlit.app/)
- [Kasir_Dashboard](https://kasir-kafenusantara-2026.streamlit.app/)
- [Admin_Dashboard](https://laporaneksekutif-kafenusantara-2026.streamlit.app/)

## Colaboration Or Order

Whatsapp : 0895624997600