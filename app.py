import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from utils.css_styles import inject_css, inject_opening_css, render_top_nav
from utils.helpers import (
    WS_KAS, WS_PENGATURAN, KOLOM_KAS, KOLOM_PENGATURAN,
    load_data, safe_update, pastikan_kolom, rupiah,
    get_last_saldo, hitung_ringkasan,
    get_sisa_hari_bulan_ini,
    get_gaji, get_tabungan,
    hitung_pengeluaran_tetap_bulanan,
    hitung_beban_belum_bayar,
    hitung_saldo_siap_pakai,
    hitung_pengeluaran_hari_ini,
    get_pengaturan, to_float
)

st.set_page_config(page_title="Keuangan Pribadi", page_icon="💰", layout="centered", initial_sidebar_state="collapsed")
inject_css()
conn = st.connection("gsheets", type=GSheetsConnection)

if "opening_done" not in st.session_state:
    st.session_state["opening_done"] = False

if not st.session_state["opening_done"]:
    inject_opening_css()
    st.markdown("""
    <div class="opening-wrapper">
        <div class="coin-container">
            <div class="coin-ring"></div><div class="coin"></div>
            <div class="sparkle"></div><div class="sparkle"></div>
            <div class="sparkle"></div><div class="sparkle"></div>
        </div>
        <p class="opening-name">M. Luthfi Renaldi</p>
        <p class="opening-tagline">Financial Tracker</p>
        <div class="opening-line"></div>
        <p class="opening-subtitle">Atur keuanganmu dengan cerdas</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    if st.button("🚀 MASUK", type="primary", use_container_width=True):
        st.session_state["opening_done"] = True
        st.rerun()
    st.stop()

render_top_nav(active="home")

df_kas = load_data(conn, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)
df_pg = load_data(conn, WS_PENGATURAN)
df_pg = pastikan_kolom(df_pg, KOLOM_PENGATURAN)

st.markdown("""
<div style="text-align:center; padding:10px 0 5px 0;">
    <p style="font-family:'Poppins',sans-serif; font-size:0.7rem; font-weight:500;
              color:#5a5a6a; text-transform:uppercase; letter-spacing:0.1em; margin:0; text-align:center;">
        KEUANGAN PRIBADI</p>
    <p style="font-family:'Poppins',sans-serif; font-size:1.4rem; font-weight:700;
              color:#f5f5f5; margin:4px 0 0 0; text-align:center;">
        Hai, Luthfi 👋</p>
</div>
""", unsafe_allow_html=True)

st.divider()

last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)
total_masuk, total_keluar = hitung_ringkasan(df_kas)

st.markdown(f"""
<div style="text-align:center; padding:20px 0; background:linear-gradient(135deg,#13131a,#1a1a25);
            border:1px solid #2a2a3a; border-radius:16px; margin-bottom:16px;">
    <p style="font-family:'Poppins',sans-serif; font-size:0.7rem; font-weight:500;
              color:#8a8a9a; text-transform:uppercase; letter-spacing:0.08em; margin:0 0 6px 0; text-align:center;">
        Total Saldo</p>
    <p style="font-family:'JetBrains Mono',monospace; font-size:2rem; font-weight:700;
              color:#c4a35a; margin:0; text-shadow:0 0 20px rgba(196,163,90,0.2); text-align:center;">
        {rupiah(last_seluruh)}</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
c1.metric("💵 Di Tangan", rupiah(last_kas))
c2.metric("🏧 ATM", rupiah(last_atm))
c3.metric("🛒 Shopee", rupiah(last_shopee))

st.divider()

mc1, mc2 = st.columns(2)
mc1.metric("📥 Total Masuk", rupiah(total_masuk))
mc2.metric("📤 Total Keluar", rupiah(total_keluar))

st.divider()

# ── BATAS HARIAN ──
df_pg_batas = df_pg[(df_pg["Jenis"] == "SETTING") & (df_pg["Nama"] == "BATAS_HARIAN")]
batas_aktif_default = False
if not df_pg_batas.empty:
    batas_aktif_default = str(df_pg_batas.iloc[0]["Status"]).strip().upper() == "AKTIF"

aktif_batas = st.toggle("📅 Aktifkan Batas Harian", value=batas_aktif_default, key="toggle_batas_home")

if aktif_batas != batas_aktif_default:
    df_u = df_pg.copy()
    df_u = df_u[~((df_u["Jenis"] == "SETTING") & (df_u["Nama"] == "BATAS_HARIAN"))].copy()
    row_s = {"Jenis": "SETTING", "Nama": "BATAS_HARIAN", "Nominal": "0", "Periode": "-",
             "Status": "AKTIF" if aktif_batas else "NONAKTIF", "Bulan_Bayar": "-", "Counter_Bayar": "0"}
    df_u = pd.concat([df_u, pd.DataFrame([row_s])], ignore_index=True)
    safe_update(conn, WS_PENGATURAN, df_u)

if aktif_batas:
    saldo_siap = hitung_saldo_siap_pakai(df_kas, df_pg)
    beban_sisa = hitung_beban_belum_bayar(df_pg)
    tabungan_val = get_tabungan(df_pg)
    sisa_hari = get_sisa_hari_bulan_ini()
    keluar = hitung_pengeluaran_hari_ini(df_kas)

    batas = saldo_siap / sisa_hari if sisa_hari > 0 and saldo_siap > 0 else 0
    sisa = batas - keluar

    b1, b2 = st.columns(2)
    b1.metric("💰 Saldo Siap Pakai", rupiah(saldo_siap))
    b2.metric("🎯 Batas Harian", rupiah(batas))

    b3, b4 = st.columns(2)
    b3.metric("📤 Keluar Hari Ini", rupiah(keluar))
    b4.metric("💵 Sisa Batas Hari Ini", rupiah(sisa))

    st.caption(
        f"Saldo ({rupiah(last_seluruh)}) - beban ({rupiah(beban_sisa)}) "
        f"- tabungan ({rupiah(tabungan_val)}) = {rupiah(saldo_siap)} / {sisa_hari} hari"
    )

    if batas <= 0:
        st.error("❌ Tidak ada budget harian tersisa!")
    elif keluar <= 0:
        st.success(f"✅ Belum ada pengeluaran hari ini. Batas penuh {rupiah(batas)}")
    elif sisa < 0:
        st.error(f"🚨 Melebihi batas harian sebesar {rupiah(abs(sisa))}")
    elif (sisa / batas * 100) < 20:
        st.error(f"❌ Sisa batas tinggal {rupiah(sisa)} ({sisa/batas*100:.0f}%)")
    elif (sisa / batas * 100) < 50:
        st.warning(f"⚠️ Sisa batas {rupiah(sisa)} ({sisa/batas*100:.0f}%)")
    else:
        st.success(f"✅ Masih aman. Sisa {rupiah(sisa)} ({sisa/batas*100:.0f}%)")

st.divider()

# ── INFO BULANAN ──
gaji = get_gaji(df_pg)
pengeluaran_tetap = hitung_pengeluaran_tetap_bulanan(df_pg)
hasil_bersih = hitung_saldo_siap_pakai(df_kas, df_pg)
sisa_hari = get_sisa_hari_bulan_ini()
tabungan = get_tabungan(df_pg)

with st.expander("📊 Info Keuangan Bulan Ini", expanded=False):
    i1, i2 = st.columns(2)
    i1.metric("💼 Gaji", rupiah(gaji))
    i2.metric("💳 Beban Tetap/Bulan", rupiah(pengeluaran_tetap))
    i3, i4 = st.columns(2)
    i3.metric("🏦 Tabungan/Bulan", rupiah(tabungan))
    i4.metric("✨ Hasil Bersih", rupiah(hasil_bersih))
    st.divider()
    i5, i6 = st.columns(2)
    i5.metric("📅 Sisa Hari", f"{sisa_hari} hari")
    i6.metric("⏳ Beban Belum Bayar", rupiah(hitung_beban_belum_bayar(df_pg)))

st.markdown("""
<div style="text-align:center; padding:30px 0 10px 0; border-top:1px solid #1e1e2a; margin-top:20px;">
    <p style="font-family:'Poppins',sans-serif; font-size:0.55rem; color:#3a3a4a; margin:0; text-align:center;">
        Keuangan Pribadi - Financial Tracker</p>
    <p style="font-family:'Poppins',sans-serif; font-size:0.65rem; font-weight:600;
              color:#5a5a6a; margin:2px 0 0 0; text-align:center;">
        M. Luthfi Renaldi</p>
</div>
""", unsafe_allow_html=True)
