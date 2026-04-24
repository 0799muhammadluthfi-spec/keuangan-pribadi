# ==========================================
# app.py
# ==========================================
import streamlit as st
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css, inject_opening_css, render_top_nav
from utils.helpers import (
    WS_KAS,
    WS_PENGATURAN,
    KOLOM_KAS,
    KOLOM_PENGATURAN,
    load_data,
    pastikan_kolom,
    rupiah,
    get_last_saldo,
    hitung_ringkasan,
    hitung_pengeluaran_harian,
    get_sisa_hari_bulan_ini,
    cek_warning_harian,
    hitung_hasil_bersih_bulanan,
    get_gaji,
    hitung_pengeluaran_tetap_bulanan,
    get_pengaturan,
    to_float
)

st.set_page_config(
    page_title="Keuangan Pribadi",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_css()

conn = st.connection("gsheets", type=GSheetsConnection)

# ── OPENING SCREEN ──
if "opening_done" not in st.session_state:
    st.session_state["opening_done"] = False

if not st.session_state["opening_done"]:
    inject_opening_css()

    st.markdown(
        """
        <div class="opening-wrapper">
            <div class="coin-container">
                <div class="coin-ring"></div>
                <div class="coin"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
                <div class="sparkle"></div>
            </div>
            <p class="opening-name">M. Luthfi Renaldi</p>
            <p class="opening-tagline">Financial Tracker</p>
            <div class="opening-line"></div>
            <p class="opening-subtitle">Atur keuanganmu dengan cerdas</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    if st.button("🚀 MASUK", type="primary", use_container_width=True):
        st.session_state["opening_done"] = True
        st.rerun()

    st.stop()

# ── NAVIGATION ──
render_top_nav(active="home")

# ── LOAD DATA ──
df_kas = load_data(conn, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)

df_pg = load_data(conn, WS_PENGATURAN)
df_pg = pastikan_kolom(df_pg, KOLOM_PENGATURAN)

# ── HEADER ──
st.markdown(
    """
    <div style="text-align:center; padding: 10px 0 5px 0;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:0.7rem; font-weight:500;
                  color:#5a5a6a; text-transform:uppercase;
                  letter-spacing:0.1em; margin:0;">
            KEUANGAN PRIBADI
        </p>
        <p style="font-family:'Poppins',sans-serif;
                  font-size:1.4rem; font-weight:700;
                  color:#f5f5f5; margin:4px 0 0 0;
                  text-align:center;">
            Hai, Luthfi 👋
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ── RINGKASAN SALDO ──
last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)
total_masuk, total_keluar = hitung_ringkasan(df_kas)

st.markdown(
    f"""
    <div style="text-align:center; padding: 20px 0;
                background: linear-gradient(135deg, #13131a, #1a1a25);
                border: 1px solid #2a2a3a;
                border-radius: 16px; margin-bottom: 16px;
                animation: metricIn 0.5s ease-out both;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:0.7rem; font-weight:500;
                  color:#8a8a9a; text-transform:uppercase;
                  letter-spacing:0.08em; margin:0 0 6px 0;
                  text-align:center;">
            Total Saldo
        </p>
        <p style="font-family:'JetBrains Mono',monospace;
                  font-size:2rem; font-weight:700;
                  color:#c4a35a; margin:0;
                  text-shadow: 0 0 20px rgba(196,163,90,0.2);
                  text-align:center;">
            {rupiah(last_seluruh)}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)
c1.metric("💵 Di Tangan", rupiah(last_kas))
c2.metric("🏧 ATM", rupiah(last_atm))
c3.metric("🛒 Shopee", rupiah(last_shopee))

st.divider()

mc1, mc2 = st.columns(2)
mc1.metric("📥 Total Masuk", rupiah(total_masuk))
mc2.metric("📤 Total Keluar", rupiah(total_keluar))

st.divider()

# ── WARNING HARIAN ──
level, pesan = cek_warning_harian(df_kas, df_pg)
if level == "bahaya":
    st.error(pesan)
elif level == "warning":
    st.warning(pesan)

# ── INFO BULANAN ──
gaji = get_gaji(df_pg)
pengeluaran_tetap = hitung_pengeluaran_tetap_bulanan(df_pg)
hasil_bersih = hitung_hasil_bersih_bulanan(df_pg)
pengeluaran_harian = hitung_pengeluaran_harian(df_pg)
sisa_hari = get_sisa_hari_bulan_ini()

d_tabungan = get_pengaturan(df_pg, "TABUNGAN")
tabungan = to_float(d_tabungan.iloc[0]["Nominal"]) if not d_tabungan.empty else 0

with st.expander("📊 Info Keuangan Bulan Ini", expanded=False):
    i1, i2 = st.columns(2)
    i1.metric("💼 Gaji", rupiah(gaji))
    i2.metric("💳 Pengeluaran Tetap/Bulan", rupiah(pengeluaran_tetap))

    i3, i4 = st.columns(2)
    i3.metric("🏦 Tabungan/Bulan", rupiah(tabungan))
    i4.metric("✨ Hasil Bersih", rupiah(hasil_bersih))

    st.divider()

    i5, i6 = st.columns(2)
    i5.metric("📅 Sisa Hari", f"{sisa_hari} hari")
    i6.metric("💰 Batas Harian", rupiah(pengeluaran_harian))

    if last_kas > 0 and sisa_hari > 0:
        batas_riil = last_kas / sisa_hari
        st.metric("🎯 Budget Harian Tersedia", rupiah(batas_riil))

        if batas_riil < pengeluaran_harian:
            st.warning(
                f"⚠️ Budget harian ({rupiah(batas_riil)}) "
                f"lebih kecil dari pengeluaran tetap harian ({rupiah(pengeluaran_harian)})"
            )

# ── FOOTER ──
st.markdown(
    """
    <div style="text-align:center; padding:30px 0 10px 0;
                border-top:1px solid #1e1e2a; margin-top:20px;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:0.55rem; font-weight:400;
                  color:#3a3a4a; margin:0; text-align:center;">
            Keuangan Pribadi - Financial Tracker
        </p>
        <p style="font-family:'Poppins',sans-serif;
                  font-size:0.65rem; font-weight:600;
                  color:#5a5a6a; margin:2px 0 0 0; text-align:center;">
            M. Luthfi Renaldi
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
