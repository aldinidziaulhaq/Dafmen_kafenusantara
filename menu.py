import base64
from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps

from storage import append_new_order, load_orders
from menu_data import MENU, BADGE_MAP

#Hitung Best Seller
try:
    semua_pesanan = load_orders()
    penjualan_menu = {}
    
    # Menjumlahkan porsi tiap menu (hanya dari pesanan berstatus 'selesai')
    for pesanan in semua_pesanan:
        if str(pesanan.get("status", "")).strip().lower() == "selesai":
            for item in pesanan.get("items", []):
                nama = item["nama"]
                qty = item.get("qty", 1) # Ambil qty, default 1 jika tidak ada
                penjualan_menu[nama] = penjualan_menu.get(nama, 0) + qty

    # Ambil 3 besar nama menu dengan penjualan terbanyak
    top_sellers = sorted(penjualan_menu.items(), key=lambda x: x[1], reverse=True)[:3]
    top_seller_names = [nama for nama, total_qty in top_sellers]
except Exception:
    top_seller_names = [] # Jika database error/kosong, jangan sampai aplikasi crash

# Menimpa badge bawaan di dictionary MENU
for kategori, items in MENU.items():
    for item in items:
        # Hapus badge 'best' manual dari menu_data.py
        if item.get("badge") == "best":
            item["badge"] = None
        # Pasang badge 'best' HANYA jika menu tersebut masuk top 3
        if item["nama"] in top_seller_names:
            item["badge"] = "best"

menu = MENU

st.set_page_config(
    page_title="Cafe Nusantara — Menu",
    page_icon="assets/logo_kafe.png",
    layout="wide",
)


def get_image_base64(path, size=(400, 280)):
    """Buka & crop gambar, lalu kembalikan sebagai base64 PNG agar bisa
    ditempel langsung di dalam kartu HTML (menyatu dengan teks, bukan
    elemen terpisah seperti sebelumnya)."""
    try:
        img = Image.open(path)
        img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return None

# ── CSS — palet warna ala "Caffire": krem & coklat tua, elegan ──────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

* { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #F7F1E1;
    color: #4A3826;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background-color: #F0E6D2; border-right: 1px solid #E3D6B8; }

.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    border-bottom: 1px solid #E3D6B8;
    margin-bottom: 2rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 5rem;
    font-weight: 900;
    color: #3B2A1E;
    letter-spacing: 0.05em;
    line-height: 1;
    margin: 0;
}
.hero-sub {
    font-size: 0.9rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #9C8362;
    margin-top: 0.5rem;
}
.hero-divider {
    width: 80px; height: 2px;
    background: linear-gradient(90deg, transparent, #C9A06C, transparent);
    margin: 1rem auto;
}
.category-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    color: #3B2A1E;
    border-bottom: 1px solid #E3D6B8;
    padding-bottom: 0.5rem;
    margin: 2rem 0 1.2rem;
}

.menu-card {
    background: #FFFFFF;
    border: 1px solid #E9DCC0;
    border-radius: 24px;
    overflow: hidden;
    transition: all .3s ease;
    box-shadow: 0 10px 25px rgba(60,40,20,.08);
    min-height: 160px;
}
.menu-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: #C9A06C;
    box-shadow: 0 15px 30px rgba(60,40,20,.15);
}
.menu-card-body {
    padding: 16px 18px 20px;
}
.product-image {
    width: 100%;
    height: 220px;
    object-fit: cover;
    display: block;
    margin: 0;
}

.item-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #3B2A1E;
    font-weight: 700;
    margin: 0 0 0.3rem;
    min-height: 55px;
    line-height: 1.4;
}
.item-desc {
    font-size: 0.89rem;
    color: #9C8362;
    margin: 0 0 0.5rem;
    min-height: 60px;
    line-height: 1.5;
}
.item-price { font-size: 1rem; font-weight: 700; color: #A66A2E; }

.badge { display: inline-block; font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase;
         padding: 2px 8px; border-radius: 20px; margin-left: 8px; vertical-align: middle; }
.badge-new  { background:#EFE2C5; color:#8B5E34; border:1px solid #C9A06C; }
.badge-hot  { background:#F5DEDA; color:#B05B45; border:1px solid #B05B4566; }
.badge-best { background:#DCEAD9; color:#3F7A52; border:1px solid #3F7A5266; }

.footer { text-align:center; color:#9C8362; font-size:0.8rem; padding:2rem 0 1rem;
          border-top:1px solid #E3D6B8; margin-top:3rem; letter-spacing:0.1em; }

div.stButton > button {
    background: #3B2A1E !important;
    color: #F7F1E1 !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 0.7rem 1rem !important;
    width: 100%;
    padding-left: 0 !important;
    padding-right: 0 !important;
    margin: 0 !important; 
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #5A4030, #3B2A1E) !important;
    color: #F7F1E1 !important;
}

[data-testid="stMetricLabel"] p {
    color: #3B2A1E !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #3B2A1E !important;
    font-weight: 700 !important;
}
/* KUSTOMISASI INPUT MEJA & NAMA AGAR LEBIH TERLIHAT */
div[data-testid="stTextInput"] label {
    background-color: #DCEAD9 !important;
    color: #3F7A52 !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    font-weight: bold !important;
    display: inline-block;
}
div[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    border: 2px solid #3F7A52 !important;
    color: #3B2A1E !important;
    font-weight: bold !important;
}    
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

st.image("assets/banner_cafe.png", use_container_width=True)

if "checkout_stage" not in st.session_state:
    st.session_state.checkout_stage = "input"
if "temp_meja" not in st.session_state:
    st.session_state.temp_meja = ""
if "notif_sukses" not in st.session_state:
    st.session_state.notif_sukses = ""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("assets/logo_kafe.png", width=220)
    st.markdown("<br>", unsafe_allow_html=True)
    icon_col, text_col = st.columns([1, 3])
    with icon_col:
        st.image("assets/pencarian.png", width=50)
    with text_col:
        st.markdown("### Filter Menu")
    kategori_pilihan = st.selectbox("KATEGORI", ["Semua"] + list(MENU.keys()))

    # Filter produk sesuai kategori
    if kategori_pilihan == "Semua":
        produk_tersedia = ["Semua"] + [
            item["nama"]
            for items in MENU.values()
            for item in items
        ]
    else:
        produk_tersedia = ["Semua"] + [
            item["nama"]
            for item in MENU[kategori_pilihan]
        ]

    cari_produk = st.selectbox(
        "CARI MENU",
        produk_tersedia,
        key=f"cari_{kategori_pilihan}"  # ← reset otomatis saat kategori ganti
    )
    harga_max = st.slider("HARGA MAKSIMAL (Rp)", 20000, 70000, 70000, step=5000, format="Rp %d")

    st.markdown("---")
    jumlah_item = sum(item["qty"] for item in st.session_state.keranjang)
    icon_col, text_col = st.columns([1, 3])
    with icon_col:
        st.image("assets/keranjang.png", width=50)
    with text_col:
        st.info(f"{jumlah_item} item dipilih")
    
    if st.session_state.notif_sukses:
        st.success(st.session_state.notif_sukses)
        st.session_state.notif_sukses = ""

    if st.session_state.keranjang:
        total = 0
        for item in st.session_state.keranjang:
            subtotal = item["harga"] * item["qty"]
            st.markdown(
                f"<small>• {item['nama']} ×{item['qty']} — Rp {subtotal:,}</small>",
                unsafe_allow_html=True,
            )
            total += subtotal
        st.success(f"Total Bayar: Rp {total:,}")

        # ALUR PEMBAYARAN
        if st.session_state.checkout_stage == "input":
            st.session_state.temp_meja = st.text_input("Masukkan : Nomor Meja & Nama (Contoh : Meja 5 - Aldi) Pembayaran QRIS Wajib menggunakan nama sesuai pembayaran", value=st.session_state.temp_meja)
            if st.button("Lanjut ke Pembayaran", use_container_width=True, type="primary"):
                if not st.session_state.temp_meja.strip():
                    st.warning("Isi nomor meja & nama dulu ya!")
                else:
                    st.session_state.checkout_stage = "payment"
                    st.rerun()

        elif st.session_state.checkout_stage == "payment":
            st.markdown("---")
            st.subheader("Pilih Pembayaran")
            metode = st.radio("Metode:", ["Scan QRIS", "Cash (Bayar di Kasir)"])
            
            if metode == "Scan QRIS":
                st.info("Silakan scan QRIS di bawah ini:")
                st.image("assets/qris.jpeg", caption="QRIS Kafe Nusantara")
                # Fitur Download QRIS
                try:
                    with open("assets/qris.jpeg", "rb") as file:
                        st.download_button(
                            label="Download Gambar QR Code",
                            data=file,
                            file_name="QRIS_Kafe_Nusantara.jpeg",
                            mime="image/jpeg",
                            use_container_width=True
                        )
                except Exception:
                    st.error("File QRIS tidak ditemukan di folder assets.")
            else:
                st.write("Silakan menuju kasir untuk pembayaran tunai.")

            # Layout tombol dibuat simetris dengan st.columns
            col_back, col_pay = st.columns(2)
            with col_back:
                if st.button("Kembali", use_container_width=True):
                    st.session_state.checkout_stage = "input"
                    st.rerun()
            with col_pay:
                if st.button("Selesaikan", use_container_width=True):
                    order_id = append_new_order(st.session_state.temp_meja.strip(),st.session_state.keranjang)
                    
                    # Kembalikan semua ke kondisi awal
                    st.session_state.keranjang = []
                    st.session_state.temp_meja = ""                  # KOSONGKAN KOLOM NAMA
                    st.session_state.checkout_stage = "input"        # KEMBALIKAN KE TAHAP INPUT
                    
                    # Simpan notifikasi ke session_state agar bertahan setelah rerun
                    st.session_state.notif_sukses = f"Pesanan #{order_id} Berhasil Terkirimkan!!"
                    st.rerun()

        if st.button("Kosongkan Keranjang", use_container_width=True):
            st.session_state.keranjang = []
            st.session_state.temp_meja = ""
            st.session_state.checkout_stage = "input"
            st.rerun()
    else:
        st.markdown("<small style='color:#9C8362'>Keranjang masih kosong.</small>", unsafe_allow_html=True)

    st.markdown("---")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='hero'>
    <div class='hero-sub'>Rasa Nusantara Dalam Setiap Cangkir</div>
    <div class='hero-title'>CAFE<br>NUSANTARA</div>
    <div class='hero-divider'></div>
    <p style='max-width:700px; margin:auto; color:#9C8362; line-height:1.8;'>
        Nikmati Kopi Pilihan Nusantara, Makanan Premium, Dan Dessert Spesial
        Yang Dibuat Dari Bahan Berkualitas Terbaik.
    </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.image(
        "assets/kopi.png",
        width=50
    )
    st.metric("Total Menu", sum(len(v) for v in MENU.values()))
with c2:
    st.image("assets/seller.png",width=65)
    st.metric("Best Seller", sum(1 for cat in MENU.values() for item in cat if item["badge"] == "best"))
with c3:
    st.image("assets/laris.png",width=50)
    st.metric("Menu Terlaris", sum(1 for cat in MENU.values() for item in cat if item["badge"] == "hot"))

# ── Fungsi render kartu menu FAVORIT (tanpa tombol tambah) ──
def render_kartu_menu_favorit(item, kategori):
    badge_html = ""
    if item.get("badge") and item["badge"] in BADGE_MAP:
        label, cls = BADGE_MAP[item["badge"]]
        badge_html = f'<span class="badge {cls}">{label}</span>'

    img_html = ""
    if "gambar" in item:
        b64 = get_image_base64(item["gambar"])
        if b64:
            img_html = f'<img src="data:image/png;base64,{b64}" class="product-image">'

    st.markdown(f"""
    <div class="menu-card">
        {img_html}
        <div class="menu-card-body">
            <div class="item-name">{item['nama']}{badge_html}</div>
            <div class="item-desc">{item['deskripsi']}</div>
            <div class="item-price">Rp {item['harga']:,}</div>
        </div>
    </div>
    <div style='margin-bottom:1rem'></div>
    """, unsafe_allow_html=True)
# ── Fungsi render satu kartu menu (dipakai ulang utk Favorit & daftar menu) ──
def render_kartu_menu(item, kategori, key_prefix=""):
    badge_html = ""
    if item.get("badge") and item["badge"] in BADGE_MAP:
        label, cls = BADGE_MAP[item["badge"]]
        badge_html = f'<span class="badge {cls}">{label}</span>'

    img_html = ""
    if "gambar" in item:
        b64 = get_image_base64(item["gambar"])
        if b64:
            img_html = f'<img src="data:image/png;base64,{b64}" class="product-image">'

    st.markdown(f"""
    <div class="menu-card">
        {img_html}
        <div class="menu-card-body">
            <div class="item-name">{item['nama']}{badge_html}</div>
            <div class="item-desc">{item['deskripsi']}</div>
            <div class="item-price">Rp {item['harga']:,}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    key_base = f"{key_prefix}{kategori}_{item['nama']}"
    col_qty, col_btn = st.columns([1, 2])
    #simpan product tambah dan kurang
    if f"qty_{key_base}" not in st.session_state:
        st.session_state[f"qty_{key_base}"] = 1
    qty = st.session_state[f"qty_{key_base}"]
    with col_qty:
        c1, c2, c3 = st.columns([0.8, 0.6, 0.8],gap="small")
        with c1:
            if st.button("➖", key=f"minus_{key_base}"):
                if st.session_state[f"qty_{key_base}"] > 1:
                    st.session_state[f"qty_{key_base}"] -= 1
        with c2:
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    height:52px;
                    font-size:24px;
                    font-weight:700;
                    color:#3B2A1E;
                ">
                    {st.session_state[f"qty_{key_base}"]}
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            if st.button("➕", key=f"plus_{key_base}"):
                if st.session_state[f"qty_{key_base}"] < 10:
                    st.session_state[f"qty_{key_base}"] += 1
                    qty = st.session_state[f"qty_{key_base}"]
    with col_btn:
        if st.button("🛒 Tambah", key=f"add_{key_base}", use_container_width=True):
            found = False
            for k in st.session_state.keranjang:
                if k["nama"] == item["nama"]:
                    k["qty"] += qty
                    found = True
                    break
            if not found:
                st.session_state.keranjang.append({
                    "nama": item["nama"],
                    "harga": item["harga"],
                    "qty": qty,
                })
            st.rerun()

    st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)


# ── Menu Favorit (Best Seller) ────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
icon_col, text_col = st.columns([0.4, 8])
with icon_col:
    st.image("assets/favorit.png",width=60)
with text_col:
    st.subheader("Menu Favorit")

best_seller = [
    (kategori, item)
    for kategori, items in MENU.items()
    for item in items
    if item["badge"] == "best"
]

if best_seller:
    cols_fav = st.columns(3)
    for i, (kategori, item) in enumerate(best_seller):
        with cols_fav[i % 3]:
            render_kartu_menu_favorit(item, kategori)
else:
    st.markdown(
        "<small style='color:#9C8362'>Belum ada menu favorit.</small>",
        unsafe_allow_html=True,
    )

# ── Daftar Menu ───────────────────────────────────────────────────────────────
categories_to_show = {
    k: v for k, v in MENU.items()
    if kategori_pilihan == "Semua" or k == kategori_pilihan
}
total_tampil = 0

for kategori, items in categories_to_show.items():
    filtered=[
        it for it in items
        if (cari_produk == "Semua" or it["nama"] == cari_produk)
        and it["harga"] <= harga_max
    ]
    if not filtered:
        continue

    ICON_MAP = {
    "Kopi": "assets/kopi.png",
    "Non-Kopi": "assets/nonkopi.png",
    "Makanan": "assets/makanan.png",
    "Dessert": "assets/dessert.png"
}
    st.markdown(
        "<div style='margin-top:60px; '></div>",
        unsafe_allow_html=True
    )
    icon_col, text_col = st.columns([1, 8])

    with icon_col:
        st.markdown(
            """
            <div style='margin-top:20px; margin-left:70px;'>
            """,
            unsafe_allow_html=True
        )

        st.image(ICON_MAP[kategori], width=60)

        st.markdown("</div>", unsafe_allow_html=True)

    with text_col:
        st.markdown(
            f"""
            <div class="category-header">
                {kategori}
            </div>
            """,
            unsafe_allow_html=True
        )
    cols = st.columns(3)

    for i, item in enumerate(filtered):
        with cols[i % 3]:
            render_kartu_menu(item, kategori)
        total_tampil += 1

if total_tampil == 0:
    st.markdown(
        "<br><center style='color:#9C8362'>Tidak ada menu yang cocok dengan filter.</center>",
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footer">✦ &nbsp; KAFE NUSANTARA &nbsp; ✦ &nbsp; Nomor WA Pembuatan Web : 0895624997600  &nbsp; ✦</div>',
    unsafe_allow_html=True,
)