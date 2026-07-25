import base64
from io import BytesIO
import time
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
from PIL import Image, ImageOps

from storage import append_new_order, load_orders
from menu_data import MENU, BADGE_MAP

# Hitung Best Seller (DI-CACHE AGAR TIDAK LEMOT)
@st.cache_data(ttl=60, show_spinner=False) # Menyimpan hasil selama 60 detik
def get_best_sellers():
    semua_pesanan = load_orders()
    penjualan_menu = {}
    for pesanan in semua_pesanan:
        if str(pesanan.get("status", "")).strip().lower() == "selesai":
            for item in pesanan.get("items", []):
                nama = item["nama"]
                qty = item.get("qty", 1)
                penjualan_menu[nama] = penjualan_menu.get(nama, 0) + qty
    top_sellers = sorted(penjualan_menu.items(), key=lambda x: x[1], reverse=True)[:3]
    return [nama for nama, total_qty in top_sellers]

try:
    top_seller_names = get_best_sellers()
except Exception:
    top_seller_names = []

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

@st.cache_data(show_spinner=False)
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

/* 1. Desain untuk Tombol Normal (Tambah, Lanjut, Kosongkan, dll) */
div.stButton > button[kind="primary"],
div.stButton > button[kind="secondary"] {
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

div.stButton > button[kind="primary"]:hover,
div.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #5A4030, #3B2A1E) !important;
    color: #F7F1E1 !important;
}

/* 2. Desain Container Tombol + dan - (Tertiary) */
div.stButton > button[kind="tertiary"] {
    background: transparent !important;
    color: #3B2A1E !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    min-height: 40px !important; 
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div.stButton > button[kind="tertiary"]:hover {
    background: transparent !important;
    color: #C9A06C !important; /* Warna ikon berubah emas saat disorot */
    transform: scale(1.15); /* Efek sedikit membesar saat di-hover */
    transition: all 0.2s ease-in-out;
}

/* 3. Menargetkan teks <p> di dalam tombol + dan - agar ukurannya membesar & pas di tengah */
div.stButton > button[kind="tertiary"] p {
    font-size: 30px !important;
    font-weight: 500 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 0.5 !important;
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

# ── PELACAK STATUS PESANAN & ALARM ──────────────────────────────────────────
if st.session_state.get("last_order_id"):
    # Refresh halaman tiap 60 detik
    st_autorefresh(interval=60000, key="tunggu_pesanan")
    
    semua_pesanan = load_orders()
    pesanan_saya = next((o for o in semua_pesanan if o["id"] == st.session_state.last_order_id), None)
    
    if pesanan_saya:
        status_pesanan = str(pesanan_saya.get("status", "")).lower()
        
        if status_pesanan == "selesai":
            st.success(f"*HORE! Pesanan Anda (Nama : {pesanan_saya['meja']}) sudah siap di Kasir!*")
            
            import time
            waktu_trigger = time.time()
            
            # --- CEK APAKAH INI BUNYI PERTAMA KALI ---
            is_first_time = not st.session_state.get("notif_completed_played", False)
            
            if is_first_time:
                # Jika pertama kali, setting bunyi 3 kali
                js_beep_script = """
                    bunyiBeep();
                    setTimeout(bunyiBeep, 1000);
                    setTimeout(bunyiBeep, 2000);
                """
                # Tandai bahwa bunyi 3x sudah dimainkan
                st.session_state.notif_completed_played = True
            else:
                # Jika refresh selanjutnya (belum diambil), bunyi 1 kali saja
                js_beep_script = """
                    bunyiBeep();
                """
            
            # Jalankan script suara sesuai kondisi di atas
            components.html(f"""
            <script>
            // Stempel Waktu: {waktu_trigger}
            (function() {{
                try {{
                    var ctx = new (window.AudioContext || window.webkitAudioContext)();
                    function bunyiBeep() {{
                        var o = ctx.createOscillator();
                        var g = ctx.createGain();
                        o.connect(g);
                        g.connect(ctx.destination);
                        o.frequency.value = 880; 
                        o.type = 'sine';
                        g.gain.setValueAtTime(0.3, ctx.currentTime);
                        g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
                        o.start(ctx.currentTime);
                        o.stop(ctx.currentTime + 0.4);
                    }}
                    
                    {js_beep_script}
                    
                }} catch(e) {{ console.log("Audio Error:", e); }}
            }})();
            </script>
            """, height=0, width=0)
            
            if st.button("Oke, Pesanan Saya Ambil Sekarang!", type="primary", use_container_width=True):
                # Bersihkan semua jejak pesanan dari memori agar bisa pesan lagi
                st.session_state.last_order_id = None
                st.session_state.notif_completed_played = False
                st.rerun()
                
        elif status_pesanan in ["baru", "diproses"]:
            st.info(f"Memantau pesanan... Tejadi Refresh Otomatis 30 Detik sekali... Saat ini sedang *{status_pesanan.upper()}* di kasir.")
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
            st.session_state.temp_meja = st.text_input("Masukkan Nama : (Contoh : Aldi) Pembayaran QRIS Wajib menggunakan nama sesuai pembayaran", value=st.session_state.temp_meja)
            if st.button("Lanjut ke Pembayaran", use_container_width=True, type="primary"):
                if not st.session_state.temp_meja.strip():
                    st.warning("Isi Nama dulu ya!")
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
                    # ---> TAMBAHKAN 'metode' DI BAGIAN AKHIR KURUNG <---
                    order_id = append_new_order(st.session_state.temp_meja.strip(), st.session_state.keranjang, metode)
                    
                    # ---> KODE BARU: MENYIMPAN ID UNTUK DILACAK <---
                    st.session_state.last_order_id = order_id
                    
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

# ── Fungsi Penghitung Callback ──
def kurangi_qty(key):
    if st.session_state[key] > 1:
        st.session_state[key] -= 1

def tambah_qty(key):
    if st.session_state[key] < 10: # Maksimal 10 porsi
        st.session_state[key] += 1

@st.fragment
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
    qty_key = f"qty_{key_base}" # Kunci penyimpanan state
    col_qty, col_btn = st.columns([1, 2])
    
    # Inisialisasi awal jika belum ada
    if qty_key not in st.session_state:
        st.session_state[qty_key] = 1
    
    with col_qty:
        # Kolom disamaratakan pembagiannya dengan gap yang kecil agar rapi
        c1, c2, c3 = st.columns([1, 1, 1], gap="small")
        with c1:
            # Menggunakan simbol minus biasa (bukan emoji)
            st.button("−", key=f"minus_{key_base}", on_click=kurangi_qty, args=(qty_key,), type="tertiary")
            
        with c2:
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    height:40px; /* Disamakan presisi dengan min-height tombol CSS */
                    font-size:22px;
                    font-weight:700;
                    color:#3B2A1E;
                ">
                    {st.session_state[qty_key]}
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with c3:
            # Menggunakan simbol plus biasa (bukan emoji)
            st.button("+", key=f"plus_{key_base}", on_click=tambah_qty, args=(qty_key,), type="tertiary")
                    
    with col_btn:
        if st.button("Tambah", key=f"add_{key_base}", use_container_width=True):
            qty_sekarang = st.session_state[qty_key]
            found = False
            for k in st.session_state.keranjang:
                if k["nama"] == item["nama"]:
                    k["qty"] += qty_sekarang
                    found = True
                    break
            if not found:
                st.session_state.keranjang.append({
                    "nama": item["nama"],
                    "harga": item["harga"],
                    "qty": qty_sekarang,
                })
            
            # Reset angka ke 1 setelah sukses ditambahkan
            st.session_state[qty_key] = 1 
            st.toast(f"{qty_sekarang} {item['nama']} masuk keranjang!") 
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