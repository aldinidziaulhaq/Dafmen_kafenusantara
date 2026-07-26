import base64
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageOps
from storage import load_orders

st.set_page_config(
    page_title="Laporan Eksekutif — Cafe Nusantara",
    page_icon="assets/logo_kafe.png",
    layout="wide",
)

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL STYLE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&display=swap');

/* ── Reset & Base ────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #F7F1E1;
    color: #3B2A1E;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #F0E6D2 !important;
    border-right: 1px solid #E9DCC0;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { padding-top: 0.5rem; }
section[data-testid="stSidebarContent"] { padding: 1rem 1rem 2rem; }

/* ── Sidebar nav items ───────────────────────────────────────── */
[data-testid="stSidebarNavItems"] a {
    color: #6B5140 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    padding: 0.45rem 0.75rem !important;
}
[data-testid="stSidebarNavItems"] a:hover { background: #E9DCC0 !important; }

/* ── Buttons ─────────────────────────────────────────────────── */
div.stButton > button {
    background: #3B2A1E !important;
    color: #F7F1E1 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.1rem !important;
    transition: background 0.15s !important;
}
div.stButton > button:hover { background: #5A4030 !important; }
div.stDownloadButton > button {
    background: #3B2A1E !important;
    color: #F7F1E1 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.1rem !important;
}

/* ── Inputs ──────────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
    background: #FAF6ED !important;
    border: 1.5px solid #E3D6B8 !important;
    border-radius: 8px !important;
    color: #3B2A1E !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #C9A06C !important;
    box-shadow: 0 0 0 3px #C9A06C22 !important;
}

/* ── Metric cards ────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E9DCC0 !important;
    border-radius: 12px !important;
    padding: 1rem 1.1rem !important;
}
[data-testid="stMetricLabel"] p {
    color: #9C8362 !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stMetricValue"] {
    color: #3B2A1E !important;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ── Dataframe & Charts ──────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #E9DCC0 !important;
}
[data-baseweb="radio"] label { font-size: 0.82rem !important; color: #6B5140 !important; }
</style>
""", unsafe_allow_html=True)

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
# ---------------------------------

riwayat_b64 = get_image_base64("assets/riwayat.png", size=(24,24))
riwayat_tag = f'<img src="data:image/png;base64,{riwayat_b64}" width="20" style="vertical-align:middle;margin-right:6px;">' if riwayat_b64 else "📋"

piala_b64 = get_image_base64("assets/piala.png", size=(24,24))
piala_tag = f'<img src="data:image/png;base64,{piala_b64}" width="20" style="vertical-align:middle;margin-right:6px;">' if piala_b64 else "🏆"

unduh_b64 = get_image_base64("assets/unduh_utama.png", size=(24,24))
unduh_tag = f'<img src="data:image/png;base64,{unduh_b64}" width="20" style="vertical-align:middle;margin-right:6px;">' if unduh_b64 else "📥"

pencarian_b64 = get_image_base64("assets/pencarian.png", size=(24,24))
pencarian_tag = f'<img src="data:image/png;base64,{pencarian_b64}" width="20" style="vertical-align:middle;margin-right:6px;">' if pencarian_b64 else "🔍"
# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def section(icon: str, title: str, caption: str = ""):
    cap_html = f"<div style='font-size:.75rem;color:#9C8362;margin-top:2px'>{caption}</div>" if caption else ""
    st.markdown(f"""
    <div style="margin:1.5rem 0 .75rem">
      <div style="display:flex;align-items:center;gap:8px;border-bottom:1.5px solid #E3D6B8;padding-bottom:.5rem">
        <span style="font-size:1rem;color:#C9A06C">{icon}</span>
        <span style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:#3B2A1E">{title}</span>
      </div>
      {cap_html}
    </div>
    """, unsafe_allow_html=True)

def to_excel(df_main: pd.DataFrame, df_rank: pd.DataFrame) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_main.to_excel(w, index=False, sheet_name="Riwayat Penjualan")
        df_rank.to_excel(w, index=False, sheet_name="Menu Terlaris")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════
if "admin_ok" not in st.session_state:
    st.session_state.admin_ok = False

if not st.session_state.admin_ok:
    # Menggunakan 3 kolom agar login box berada presisi di tengah
    _, col, _ = st.columns([1, 1.2, 1]) 
    
    with col:
        st.markdown("""
        <div style="text-align:center; margin-top:2rem; margin-bottom:1.5rem;">
          <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:#3B2A1E">
            Laporan Eksekutif
          </div>
          <div style="font-size:.82rem;color:#9C8362;margin-top:.25rem">
            Kafe Nusantara &nbsp;·&nbsp; Masuk untuk melihat laporan penjualan
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            if st.button("Masuk", use_container_width=True):
                if (username == st.secrets["admin"]["username"]
                        and password == st.secrets["admin"]["password"]):
                    st.session_state.admin_ok = True
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════════
# LOAD & PREPARE DATA (FOKUS PADA LAPORAN / TRANSAKSI SELESAI)
# ═══════════════════════════════════════════════════════════════════════════════
all_orders = load_orders()

# Karena ini untuk laporan perusahaan (Bos), kita asumsikan data yang dihitung 
# adalah omzet dari pesanan yang sudah berstatus 'Selesai'.
selesai_orders = [
    o for o in all_orders
    if str(o.get("status", "")).strip().lower() == "selesai"
]
total_omzet = sum(i["harga"] * i["qty"] for o in selesai_orders for i in o["items"])
total_item_terjual = sum(i["qty"] for o in selesai_orders for i in o["items"])

# 1. Siapkan DataFrame Penjualan
rows = []
for o in selesai_orders:
    total = sum(i["harga"] * i["qty"] for i in o["items"])
    items_str = ", ".join(f"{i['nama']} ×{i['qty']}" for i in o["items"])
    rows.append({
        "ID Transaksi": o["id"], 
        "Nama / Meja": o["meja"],
        "Rincian Item": items_str, 
        "Waktu": o["waktu"],
        "Total Penjualan": total,
    })
df_sales = pd.DataFrame(rows) if rows else pd.DataFrame()

# 2. Siapkan DataFrame Menu Terlaris
menu_cnt: dict = {}
for o in selesai_orders:
    for i in o["items"]:
        menu_cnt[i["nama"]] = menu_cnt.get(i["nama"], 0) + i["qty"]

df_rank = (
    pd.DataFrame([{"Menu": k, "Terjual": v} for k, v in menu_cnt.items()])
    .sort_values("Terjual", ascending=False)
    .reset_index(drop=True)
) if menu_cnt else pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    try:
        st.image("assets/logo_kafe.png", width=160)
    except Exception:
        st.markdown("*☕ Cafe Nusantara*")

    st.markdown("""
    <div style="font-size:.7rem;color:#9C8362;line-height:1.7;margin:.5rem 0 1rem">
      Laporan Internal Perusahaan<br>
      Data Khusus Transaksi Selesai
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.65rem;font-weight:600;letter-spacing:.1em;"
        "text-transform:uppercase;color:#9C8362;margin-bottom:.4rem'>Menu Laporan</div>",
        unsafe_allow_html=True,
    )
    
    # Hanya ada 3 Navigasi Sesuai Permintaan
    nav = st.radio(
        "nav", ["Total Penjualan", "Menu Terlaris", "Export Laporan"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    now = datetime.now().strftime("%A, %d %b %Y")
    st.markdown(f"<div style='font-size:.7rem;color:#9C8362'>{now}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Keluar Akun", use_container_width=True):
        st.session_state.admin_ok = False
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1.25rem">
  <div>
    <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:#3B2A1E">
      {nav}
    </div>
    <div style="font-size:.78rem;color:#9C8362;margin-top:3px">
      Kafe Nusantara &nbsp;·&nbsp; Ringkasan Laporan Perusahaan
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TOTAL PENJUALAN
# ═══════════════════════════════════════════════════════════════════════════════
if nav == "Total Penjualan":
    # 3 Metrik Inti Saja
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Omzet", f"Rp {total_omzet:,.0f}", help="Total pendapatan kotor dari transaksi selesai")
    c2.metric("Total Transaksi", len(selesai_orders), help="Jumlah struk/order yang berhasil diselesaikan")
    c3.metric("Total Item Terjual", total_item_terjual, help="Total kuantitas makanan/minuman yang laku")

    st.markdown("<div style='margin:.75rem 0'></div>", unsafe_allow_html=True)
    section(riwayat_tag, "Riwayat Penjualan", "Daftar seluruh transaksi masuk (Selesai)")

    if not df_sales.empty:
        # Pilihan urutan untuk bos yang mengecek laporan
        sort_order = st.selectbox("Urutkan Berdasarkan:", ["Terbaru", "Terlama", "Nilai Transaksi Tertinggi"], key="sort1")
        
        df_view = df_sales.copy()
        if sort_order == "Terbaru":
            df_view = df_view.sort_values("Waktu", ascending=False)
        elif sort_order == "Terlama":
            df_view = df_view.sort_values("Waktu", ascending=True)
        else:
            df_view = df_view.sort_values("Total Penjualan", ascending=False)

        st.dataframe(
            df_view.reset_index(drop=True),
            use_container_width=True, hide_index=True,
            column_config={
                "Total Penjualan": st.column_config.NumberColumn("Total (Rp)", format="Rp %d"),
            },
            height=400,
        )
    else:
        st.info("Belum ada data transaksi masuk.")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. MENU TERLARIS
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Menu Terlaris":
    section(piala_tag, "Performa Menu", "Peringkat penjualan berdasarkan jumlah pcs terjual")

    if not df_rank.empty:
        col_chart, col_tbl = st.columns([3, 2])

        with col_chart:
            st.bar_chart(
                df_rank.set_index("Menu"),
                color="#C9A06C",
                use_container_width=True,
                height=350,
            )

        with col_tbl:
            st.dataframe(
                df_rank,
                use_container_width=True, hide_index=True,
                column_config={
                    "Terjual": st.column_config.ProgressColumn(
                        "Pcs Terjual",
                        min_value=0,
                        max_value=int(df_rank["Terjual"].max()),
                        format="%d pcs",
                    ),
                },
                height=350,
            )
            
        c1, c2 = st.columns(2)
        c1.metric("Menu Paling Diminati (Juara 1)", df_rank.iloc[0]["Menu"])
        c2.metric("Total Variasi Menu Terjual", f"{len(df_rank)} jenis menu")
    else:
        st.info("Belum ada data performa menu.")


# ═══════════════════════════════════════════════════════════════════════════════
# 3. EXPORT LAPORAN
# ═══════════════════════════════════════════════════════════════════════════════
elif nav == "Export Laporan":
    section(unduh_tag, "Unduh Data Laporan", "Simpan data transaksi ke format Excel atau CSV")

    if not df_sales.empty:
        st.markdown("<div style='margin-bottom:1rem;'>Pilih format laporan yang ingin Anda unduh:</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container(border=True):
                st.markdown("*Laporan Lengkap (Excel .xlsx)*<br><span style='font-size:0.8rem;color:gray;'>Rekomendasi. Berisi sheet Riwayat Penjualan & Menu Terlaris.</span>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                excel_bytes = to_excel(df_sales, df_rank if not df_rank.empty else pd.DataFrame())
                st.download_button(
                    "Download Excel",
                    data=excel_bytes,
                    file_name=f"Laporan_Penjualan_Nusantara_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        with col2:
            with st.container(border=True):
                st.markdown("*Data Transaksi Mentah (CSV)*<br><span style='font-size:0.8rem;color:gray;'>Format ringan. Hanya berisi tabel Riwayat Penjualan.</span>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                csv_bytes = df_sales.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download CSV",
                    data=csv_bytes,
                    file_name=f"Laporan_Penjualan_Nusantara_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.markdown("<div style='margin:1.5rem 0'></div>", unsafe_allow_html=True)
        section(pencarian_tag, "Preview Singkat Laporan", "Menampilkan 5 transaksi terakhir")
        st.dataframe(
            df_sales.sort_values("Waktu", ascending=False).head(5), 
            use_container_width=True, hide_index=True,
            column_config={"Total Penjualan": st.column_config.NumberColumn("Total (Rp)", format="Rp %d")}
        )
    else:
        st.info("Belum ada data untuk diekspor.")


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;color:#9C8362;font-size:.72rem;
     border-top:1px solid #E3D6B8;padding:1.25rem 0 .5rem;margin-top:2.5rem;
     letter-spacing:.08em">
  CAFE NUSANTARA &nbsp;·&nbsp; Laporan Internal &nbsp;·&nbsp; Data Digenerate Otomatis
</div>
""", unsafe_allow_html=True)