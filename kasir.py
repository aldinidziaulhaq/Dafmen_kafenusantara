# Halaman Kasir

# Import
import base64
import datetime
from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps
from streamlit_autorefresh import st_autorefresh

from storage import clear_all_done, load_orders, update_order_status

# Config Streamlit
st.set_page_config(
    page_title="Kasir - Kafe Nusantara",
    page_icon="assets/kopi.png",
    layout="wide",
)

# Helper Function
def get_image_base64(path: str, size: tuple = (50, 50)) -> str | None:
    """Buka gambar, resize, dan konversi ke base64 PNG."""
    try:
        img = Image.open(path)
        img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None
    
def format_rupiah(amount: int | float) -> str:
    """Format angka menjadi Rupiah dengan pemisah titik."""
    return f"Rp {amount:,.0f}".replace(",", ".")

def now_str() -> tuple[str, str]:
    """Kembalikan (tanggal_WIB, jam_WIB) sebagai string."""
    tz = datetime.timezone(datetime.timedelta(hours=7))
    now = datetime.datetime.now(tz)
    HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    BULAN = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    tgl = f"{HARI[now.weekday()]}, {now.day} {BULAN[now.month]} {now.year}"
    jam = now.strftime("%H:%M") + " WIB"
    return tgl, jam

# Style Css
MASTER_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background-color: #F7F1E1 !important;
    color: #4A3826;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
}
[data-testid="stHeader"]          { background: transparent !important; }
[data-testid="stSidebar"]         { background-color: #F0E6D2 !important;
                                    border-right: 1px solid #E3D6B8 !important; }
[data-testid="stSidebarContent"]  { padding-top: 1.5rem; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #F0E6D2; }
::-webkit-scrollbar-thumb { background: #C9A06C; border-radius: 3px; }

/* ══════════════════════════════
   HERO BANNER
══════════════════════════════ */
.hero-wrap {
    text-align: center;
    padding: 1.8rem 1rem 1.4rem;
    border-bottom: 1px solid #E3D6B8;
    margin-bottom: 2rem;
}
.hero-eyebrow {
    font-size: 0.72rem;
    letter-spacing: 0.4em;
    text-transform: uppercase;
    color: #9C8362;
    margin-bottom: 0.3rem;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 900;
    color: #3B2A1E;
    letter-spacing: 0.06em;
    line-height: 1;
    margin: 0;
}
.hero-sub {
    font-size: 0.8rem;
    color: #B8A48A;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.35rem;
}
.hero-divider {
    width: 70px; height: 2px;
    background: linear-gradient(90deg, transparent, #C9A06C, transparent);
    margin: 0.9rem auto;
}
.hero-meta {
    display: flex;
    justify-content: center;
    gap: 1.8rem;
    font-size: 0.82rem;
    color: #9C8362;
    margin-top: 0.8rem;
    flex-wrap: wrap;
}
.hero-meta span { display: flex; align-items: center; gap: 0.3rem; }

/* ══════════════════════════════
   STAT CARDS
══════════════════════════════ */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #FFFFFF;
    border: 1.5px solid #E9DCC0;
    border-radius: 20px;
    padding: 1.3rem 1.2rem;
    text-align: center;
    box-shadow: 0 6px 20px rgba(60,40,20,.07);
    transition: transform .22s ease, box-shadow .22s ease;
}
.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(60,40,20,.12);
}
.stat-icon  { font-size: 1.5rem; margin-bottom: 0.3rem; }
.stat-num   {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: #3B2A1E;
    line-height: 1;
}
.stat-label {
    font-size: 0.68rem;
    color: #9C8362;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 0.35rem;
}

/* ══════════════════════════════
   SECTION HEADER & ORDER CARDS
══════════════════════════════ */
.section-hdr {
    font-family: 'Playfair Display', serif;
    font-size: 1.3rem;
    color: #3B2A1E;
    border-bottom: 1px solid #E3D6B8;
    padding-bottom: 0.55rem;
    margin: 2rem 0 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.count-pill {
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8rem;
    font-family: 'Inter', sans-serif;
    font-weight: 700;
}

.order-card {
    background: #FFFFFF;
    border: 1.5px solid #E9DCC0;
    border-radius: 22px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(60,40,20,.07);
    transition: transform .25s ease, box-shadow .25s ease;
}
.order-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 32px rgba(60,40,20,.13);
}
.order-card-baru  { border-color: #C9A06C; }
.order-card-proses { border-color: #A66A2E; background: #FFFDF8; }

.badge {
    display: inline-block;
    border-radius: 20px;
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 700;
    padding: 3px 10px;
    vertical-align: middle;
    margin-left: 6px;
}
.badge-baru   { background:#FCEBD5; color:#A66A2E; border:1px solid #C9A06C; }
.badge-proses { background:#FFF8E1; color:#8B5E00; border:1px solid #D4A820; }
.badge-selesai{ background:#EDF5EC; color:#3F7A52; border:1px solid #7CB87A; }

.order-meta { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.order-id   { font-size: 0.83rem; font-weight: 700; color: #9C8362; letter-spacing: 0.08em; }
.order-time { font-size: 0.78rem; color: #B8A48A; }
.order-meja {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem;
    font-weight: 900;
    color: #3B2A1E;
    margin-bottom: 0.6rem;
}
.order-divider { height:1px; background:#F0E8D8; margin: 0.6rem 0; }
.order-item-row { display: flex; justify-content: space-between; padding: 0.15rem 0; }
.order-item-name { color: #5A4030; }
.order-item-price{ color: #9C8362; font-size: 0.85rem; }
.order-total-row {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    margin-top: 0.7rem;
    padding-top: 0.5rem;
    border-top: 1.5px dashed #E9DCC0;
}
.order-total-label { font-size: 0.8rem; color: #9C8362; text-transform: uppercase; letter-spacing: 0.1em; }
.order-total-value { font-size: 1.05rem; font-weight: 700; color: #A66A2E; }

/* ══════════════════════════════
   BUTTONS & FORMS
══════════════════════════════ */
div.stButton > button {
    border: none !important;
    border-radius: 14px !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 0.62rem 1rem !important;
    width: 100%;
    background: #3B2A1E !important;
    color: #F7F1E1 !important;
    transition: filter .18s ease, transform .12s ease;
}
div.stButton > button:hover { filter: brightness(1.2); color: #F7F1E1 !important; }
div.stButton > button:active { transform: scale(0.98) !important; }

/* Green buttons via key prefix */
button[data-testid="baseButton-secondary"][title*="selesai"],
div[data-testid*="selesai_"] button,
div[data-testid*="done_"] button {
    background: #2D6A4F !important;
    color: #fff !important;
}

[data-testid="stForm"] {
    max-width: 400px;
    margin: 0 auto;
    padding: 2.5rem 2rem;
    background: #FFFFFF;
    border: 1.5px solid #E9DCC0;
    border-radius: 24px;
    box-shadow: 0 16px 48px rgba(60,40,20,.10);
}
div[data-testid="stFormSubmitButton"] > button {
    border: none !important;
    border-radius: 14px !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 0.62rem 1rem !important;
    width: 100%;
    background: #3B2A1E !important;
    color: #F7F1E1 !important;
}
[data-testid="stTextInput"] input {
    background: #FAF5EB !important;
    border: 1px solid #DDD0B0 !important;
    border-radius: 10px !important;
    color: #4A3826 !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #C9A06C !important;
    box-shadow: 0 0 0 3px rgba(201,160,108,.2) !important;
}

/* ══════════════════════════════
   SIDEBAR & TIMELINE & FOOTER
══════════════════════════════ */
.sb-section {
    background: #FFFFFF;
    border: 1px solid #E9DCC0;
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.9rem;
    font-size: 0.85rem;
    color: #7A6248;
}
.sb-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; color: #B8A48A; margin-bottom: 0.2rem; }
.sb-value { font-weight: 600; color: #3B2A1E; }
.timeline-item { display: flex; gap: 0.9rem; margin-bottom: 0.8rem; align-items: flex-start; }
.timeline-dot { width: 10px; height: 10px; background: #C9A06C; border-radius: 50%; margin-top: 0.35rem; flex-shrink: 0; }
.timeline-card { background: #FAFAF6; border: 1px solid #EAE1CB; border-radius: 14px; padding: 0.75rem 1rem; flex: 1; }
.timeline-header { display: flex; justify-content: space-between; font-size: 0.82rem; }
.timeline-id   { font-weight: 700; color: #7A6248; }
.timeline-total{ font-weight: 700; color: #A66A2E; font-size: 0.9rem; margin-top: 0.2rem; }
.footer { text-align: center; color: #B8A48A; font-size: 0.78rem; padding: 2.5rem 0 1rem; border-top: 1px solid #E3D6B8; margin-top: 3rem; }
</style>
"""

# Login Logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(MASTER_CSS, unsafe_allow_html=True)

    logo_b64 = get_image_base64("assets/kopi.png", size=(52, 52))
    logo_tag  = f'<img src="data:image/png;base64,{logo_b64}" width="48" style="margin-bottom:.4rem;">' if logo_b64 else "☕"

    st.markdown(f"""
    <div style='text-align:center; padding: 3.5rem 0 2rem;'>
        {logo_tag}
        <div class='hero-eyebrow' style='margin-top:.5rem;'>Kafe Nusantara</div>
        <div class='hero-title' style='font-size:2.6rem;'>Panel Kasir</div>
        <div class='hero-sub'>Cashier Operations Dashboard</div>
        <div class='hero-divider'></div>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        gembok_b64 = get_image_base64("assets/gembok.png", size=(20, 20))
        gembok_tag = f'<img src="data:image/png;base64,{gembok_b64}" width="18" style="vertical-align:middle; margin-right:6px; margin-bottom:3px;">' if gembok_b64 else "🔐"
        
        # Load gambar kunci (untuk tombol)
        kunci_b64 = get_image_base64("assets/kunci.png", size=(18, 18))
        if kunci_b64:
            st.markdown(f"""
            <style>
            div[data-testid="stFormSubmitButton"] > button p::before {{
                content: "";
                display: inline-block;
                width: 18px;
                height: 18px;
                margin-right: 8px;
                vertical-align: middle;
                background-image: url('data:image/png;base64,{kunci_b64}');
                background-size: contain;
                background-repeat: no-repeat;
            }}
            </style>
            """, unsafe_allow_html=True)

        with st.form("login_panel", clear_on_submit=False):
            st.markdown(
                f"<p style='text-align:center; color:#9C8362; font-size:.85rem;"
                f"letter-spacing:.15em; text-transform:uppercase; margin-bottom:1.5rem; font-weight: 600;'>"
                f"{gembok_tag} Masuk ke Panel</p>",
                unsafe_allow_html=True,
            )
            username = st.text_input("Username", placeholder="Masukkan username", label_visibility="collapsed")
            st.markdown("<div style='margin:.4rem 0;'></div>", unsafe_allow_html=True)
            password = st.text_input("Password", type="password", placeholder="Masukkan password", label_visibility="collapsed")
            st.markdown("<div style='margin:.8rem 0;'></div>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Masuk ke Panel Kasir", use_container_width=True)
            if submitted:
                if (username == st.secrets["kasir"]["username"] and password == st.secrets["kasir"]["password"]):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah.")

    st.markdown("<div class='footer'>☕ <strong>KAFE NUSANTARA</strong> &nbsp;·&nbsp; Cashier Dashboard v2.0</div>", unsafe_allow_html=True)
    st.stop()

# Auto Refresh & Data
st_autorefresh(interval=60_000, key="kasir_refresh")
orders = load_orders()
baru = [o for o in orders if o.get("status") == "baru"]
proses = [o for o in orders if o.get("status") == "proses"]
selesai = [o for o in orders if o.get("status") == "selesai"]
omzet = sum(sum(i["harga"] * i["qty"] for i in o["items"]) for o in selesai)

# <--- TARUH KODE FILTERNYA DI SINI
baru = [o for o in orders if o.get("status") == "baru"]
proses = [o for o in orders if o.get("status") == "diproses"]
selesai = [o for o in orders if o.get("status") == "selesai"]
omzet = sum(sum(i["harga"] * i["qty"] for i in o["items"]) for o in selesai)
# ---> SELESAI

# Notifikasi Bunyi
if baru:
    st.markdown("""
    <script>
    (function() {
        try {
            var ctx = new (window.AudioContext || window.webkitAudioContext)();
            function beep(f,d,t,tp){
                setTimeout(function(){
                    var o=ctx.createOscillator(),g=ctx.createGain();
                    o.connect(g);g.connect(ctx.destination);
                    o.frequency.value=f;o.type=tp||'square';
                    g.gain.setValueAtTime(0.3,ctx.currentTime);
                    g.gain.exponentialRampToValueAtTime(0.001,ctx.currentTime+d);
                    o.start(ctx.currentTime);o.stop(ctx.currentTime+d);
                },t);
            }
            beep(660,.12,0); beep(880,.12,140); beep(1100,.18,280); beep(880,.12,460); beep(1100,.25,600);
        } catch(e){}
    })();
    </script>
    """, unsafe_allow_html=True)

# CSS & Assets Utama Dashboard
st.markdown(MASTER_CSS, unsafe_allow_html=True)
tgl_str, jam_str = now_str()

# Menyiapkan gambar
logo_b64 = get_image_base64("assets/kopi.png", size=(52, 52))
logo_tag  = f'<img src="data:image/png;base64,{logo_b64}" width="46" style="vertical-align:middle; margin-right:10px;">' if logo_b64 else "☕ "

rp_b64 = get_image_base64("assets/rp.png", size=(40, 40))
rp_tag = f'<img src="data:image/png;base64,{rp_b64}" width="35" style="vertical-align:middle; margin-right:6px;">' if rp_b64 else "💰"

kalender_b64 = get_image_base64("assets/kalender.png", size=(24, 24))
kalender_tag = f'<img src="data:image/png;base64,{kalender_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if kalender_b64 else "📅"

jam_b64 = get_image_base64("assets/jam.png", size=(24, 24))
jam_tag = f'<img src="data:image/png;base64,{jam_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if jam_b64 else "🕒"

loop_b64 = get_image_base64("assets/loop.png", size=(24, 24))
loop_tag = f'<img src="data:image/png;base64,{loop_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if loop_b64 else "🔄"

server_b64 = get_image_base64("assets/server.png", size=(24, 24))
server_tag = f'<img src="data:image/png;base64,{server_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if server_b64 else "🟢"

lokasi_b64 = get_image_base64("assets/lokasi.png", size=(50, 50))
lokasi_tag = f'<img src="data:image/png;base64,{lokasi_b64}" width="40" style="vertical-align:middle; margin-right:6px;">' if lokasi_b64 else "🪑"

kasir_b64 = get_image_base64("assets/kasir.png", size=(24, 24))
kasir_tag = f'<img src="data:image/png;base64,{kasir_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if kasir_b64 else "👤"

lonceng_b64 = get_image_base64("assets/lonceng.jpeg", size=(24, 24))
lonceng_tag = f'<img src="data:image/png;base64,{lonceng_b64}" width="16" style="vertical-align:middle; margin-right:4px;">' if lonceng_b64 else "🔔"

grafik_b64 = get_image_base64("assets/grafik.png", size=(24, 24))
grafik_tag = f'<img src="data:image/png;base64,{grafik_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if grafik_b64 else "📊"

subjam_b64 = get_image_base64("assets/jam.png", size=(24, 24))
subjam_tag = f'<img src="data:image/png;base64,{subjam_b64}" width="20" style="vertical-align:middle; margin-right:4px;">' if subjam_b64 else "🕒"

# Hero
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-eyebrow">Panel Kasir</div>
    <div class="hero-title">{logo_tag}Kafe Nusantara</div>
    <div class="hero-sub">Cashier Operations Dashboard</div>
    <div class="hero-divider"></div>
    <div class="hero-meta">
        <span>{kalender_tag} {tgl_str}</span>
        <span>{jam_tag} {jam_str}</span>
        <span>{loop_tag} Auto Refresh 1 Menit</span>
        <span>{server_tag} Server Online</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Statistik
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">🔴</div>
        <div class="stat-num" style="color:#8B3A3A">{len(baru)}</div>
        <div class="stat-label">Pesanan Baru</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">🟠</div>
        <div class="stat-num" style="color:#A66A2E">{len(proses)}</div>
        <div class="stat-label">Diproses</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-num">{len(selesai)}</div>
        <div class="stat-label">Selesai Hari Ini</div>
    </div>""", unsafe_allow_html=True)

with c4:
    # Memasukkan custom image RP (rp_tag) menggantikan emotikon uang
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon" style="margin-bottom: -5px;">{rp_tag}</div>
        <div class="stat-num" style="font-size:1.45rem; padding-top:.5rem; color:#A66A2E">
            {format_rupiah(omzet)}
        </div>
        <div class="stat-label">Omzet Selesai</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    sb_logo = f'<img src="data:image/png;base64,{logo_b64}" width="34" style="vertical-align:middle; margin-right:6px;">' if logo_b64 else "☕ "
    st.markdown(f"""
    <div style='text-align:center; padding:0 0 1rem;'>
        <div style='font-family:Playfair Display,serif; font-size:1.35rem; font-weight:900; color:#3B2A1E; display:flex; align-items:center; justify-content:center; gap:6px;'>
            {sb_logo} Kafe Nusantara
        </div>
        <div style='font-size:.68rem; color:#B8A48A; letter-spacing:.2em; text-transform:uppercase; margin-top:4px;'>
            Cashier Panel
        </div>
    </div>
    """, unsafe_allow_html=True)

    kasir_name = st.session_state.get("kasir_name", "Admin")
    st.markdown(f"""
    <div class="sb-section">
        <div class="sb-label">{kasir_tag} Kasir</div>
        <div class="sb-value">{kasir_name.title()}</div>
    </div>
    <div class="sb-section">
        <div class="sb-label">{kalender_tag} Waktu</div>
        <div class="sb-value" style="font-size:.82rem">{tgl_str}</div>
        <div class="sb-value">{jam_str}</div>
    </div>
    """, unsafe_allow_html=True)

    status_color = "#8B3A3A" if baru else "#3F7A52"
    status_text  = f"{lonceng_tag} {len(baru)} Pesanan Baru!" if baru else "Semua Clear"
    st.markdown(f"<div class='sb-section' style='text-align:center; color:{status_color}; font-weight:700;'>{status_text}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:.4rem 0'></div>", unsafe_allow_html=True)
    if st.button("Refresh Sekarang", use_container_width=True):
        st.rerun()

    st.markdown("<div style='margin:.4rem 0'></div>", unsafe_allow_html=True)
    if st.button("Hapus Semua Selesai", use_container_width=True):
        clear_all_done()
        st.success("Riwayat selesai dihapus.")
        st.rerun()

    st.markdown("<div style='margin:.4rem 0'></div>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown(f"""
    <div class="sb-section" style="margin-top:.5rem;">
        <div class="sb-label">{grafik_tag} Hari Ini</div>
        <div style="font-size:.82rem; color:#7A6248; line-height:1.9;">
            🔴 Baru &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>{len(baru)}</b><br>
            🟠 Diproses &nbsp; <b>{len(proses)}</b><br>
            🟢 Selesai &nbsp;&nbsp;&nbsp; <b>{len(selesai)}</b><br>
            {rp_tag} Omzet &nbsp;&nbsp;&nbsp;&nbsp; <b style='color:#A66A2E'>{format_rupiah(omzet)}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-section" style="font-size:.78rem; color:#9C8362; margin-top:.3rem;">
        ☕ Kafe Nusantara<br>Jl. Kopi Sejati No. 17<br>Buka: 07.00 – 22.00<br><br>
        <span style='color:#C9A06C;'>⚙️ v2.0.0 — 2026</span>
    </div>
    """, unsafe_allow_html=True)

# Helper Function Render Order Cards
def _items_html(items: list) -> str:
    rows = "".join(
        f"<div class='order-item-row'>"
        f"<span class='order-item-name'>{i['nama']} &nbsp;×{i['qty']}</span>"
        f"<span class='order-item-price'>{format_rupiah(i['harga'] * i['qty'])}</span>"
        f"</div>"
        for i in items
    )
    return rows

def render_order_card(order: dict, card_class: str, badge_class: str, badge_label: str) -> None:
    total  = sum(i["harga"] * i["qty"] for i in order["items"])
    items  = _items_html(order["items"])
    waktu  = order.get("waktu", "-")
    # Memasukkan custom image RP (rp_tag) ke bagian total harga di tengah
    st.markdown(f"""
    <div class="order-card {card_class}">
        <div class="order-meta">
            <div>
                <span class="order-id">#{order['id']}</span>
                <span class="badge {badge_class}">{badge_label}</span>
            </div>
            <span class="order-time">{subjam_tag} {waktu}</span>
        </div>
        <div class="order-meja">{lokasi_tag} {order['meja']}</div>
        <div class="order-divider"></div>
        <div class="order-item">{items}</div>
        <div class="order-total-row">
            <span class="order-total-label" style="display:flex; align-items:center; justify-content:center; width:100%;">
                {rp_tag} Total
            </span>
            <span class="order-total-value" style="text-align:center; width:100%;">{format_rupiah(total)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 1. Section Pesanan BARU
for order in reversed(baru):
    render_order_card(order, "order-card-baru", "badge-baru", "🔴 BARU")
    col1, col2, spacer = st.columns([1.5, 1.5, 11])
    with col1:
        if st.button(f"Proses", key=f"proses_{order['id']}"):
            update_order_status(order["id"], "diproses")
            st.rerun()
    with col2:
        if st.button(f"Batal", key=f"batal_{order['id']}"):
            update_order_status(order["id"], "batal")
            st.rerun()

# 2. Section Pesanan DIPROSES
for order in reversed(proses):
    render_order_card(order, "order-card-proses", "badge-proses", "🟡 PROSES")
    if st.button(f"Selesai — #{order['id']}", key=f"selesai_{order['id']}"):
        update_order_status(order["id"], "selesai")
        st.rerun()

# 3. Section Riwayat SELESAI
# (Otomatis muncul di expander riwayat karena statusnya 'selesai')
# Section: Riwayat Selesai
st.markdown("<br>", unsafe_allow_html=True)
with st.expander(f"Riwayat Selesai  ({len(selesai)} pesanan)"):
    if not selesai:
        st.markdown("<small style='color:#9C8362; font-style:italic;'>Belum ada pesanan selesai hari ini.</small>", unsafe_allow_html=True)
    else:
        timeline_html = ""
        for order in reversed(selesai):
            total   = sum(i["harga"] * i["qty"] for i in order["items"])
            items_s = ", ".join(f"{i['nama']} ×{i['qty']}" for i in order["items"])
            jam     = order.get("selesai_jam", order.get("waktu", "-"))
            timeline_html += f"""
            <div class="timeline-item">
                <div><div class="timeline-dot"></div></div>
                <div class="timeline-card">
                    <div class="timeline-header">
                        <span class="timeline-id">#{order['id']} — {order['meja']}</span>
                        <span class="timeline-jam">✅ {jam}</span>
                    </div>
                    <div class="timeline-items">{items_s}</div>
                    <div class="timeline-total">{format_rupiah(total)}</div>
                </div>
            </div>
            """
        st.markdown(timeline_html, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    ☕ &nbsp; <strong>KAFE NUSANTARA</strong> &nbsp; ✦ &nbsp;
    Cashier Operations Dashboard &nbsp; ✦ &nbsp;
    Version 2.0 &nbsp; ✦ &nbsp; © 2026
</div>
""", unsafe_allow_html=True)