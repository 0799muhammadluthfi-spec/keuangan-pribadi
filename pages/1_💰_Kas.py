# ==========================================
# pages/1_💰_Kas.py
# ==========================================
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css, render_top_nav
from utils.helpers import (
    WS_KAS, WS_PENGATURAN, WS_PENGECEKAN,
    KOLOM_KAS, KOLOM_PENGATURAN, KOLOM_PENGECEKAN,
    load_data, safe_update,
    get_next_no, pastikan_kolom,
    tampilkan_n_terakhir, tombol_refresh,
    to_float, fmt_nominal, rupiah,
    get_last_saldo, hitung_ringkasan,
    get_selisih_aktif,
    get_status_batas_harian,
    get_sisa_hari_bulan_ini,
    today_wita
)

st.set_page_config(
    page_title="Keuangan | Keuangan Pribadi",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_css()
conn = st.connection("gsheets", type=GSheetsConnection)

if "kas_rc" not in st.session_state:
    st.session_state["kas_rc"] = 0

def reset_form():
    st.session_state["kas_rc"] += 1

render_top_nav(active="kas")

df_kas = load_data(conn, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)
df_pg = load_data(conn, WS_PENGATURAN)
df_pg = pastikan_kolom(df_pg, KOLOM_PENGATURAN)
df_cek = load_data(conn, WS_PENGECEKAN)
df_cek = pastikan_kolom(df_cek, KOLOM_PENGECEKAN)

# ── HEADER ──
st.markdown(
    '<div style="text-align:center; padding:5px 0;">'
    '<p style="font-family:\'Poppins\',sans-serif; font-size:1.3rem; font-weight:700;'
    'color:#f5f5f5; margin:0; text-align:center;">💰 Keuangan</p></div>',
    unsafe_allow_html=True
)

# ── RINGKASAN ──
last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)
total_masuk, total_keluar = hitung_ringkasan(df_kas)

r1c1, r1c2, r1c3 = st.columns(3)
r1c1.metric("📥 Masuk", rupiah(total_masuk))
r1c2.metric("📤 Keluar", rupiah(total_keluar))
r1c3.metric("🏦 Total", rupiah(last_seluruh))

r2c1, r2c2, r2c3 = st.columns(3)
r2c1.metric("💵 Tangan", rupiah(last_kas))
r2c2.metric("🏧 ATM", rupiah(last_atm))
r2c3.metric("🛒 Shopee", rupiah(last_shopee))

st.divider()

# ── WARNING BATAS HARIAN ──
# Cek apakah batas harian aktif di pengaturan
df_pg_batas = df_pg[
    (df_pg["Jenis"] == "SETTING") &
    (df_pg["Nama"] == "BATAS_HARIAN")
]
batas_aktif = False
if not df_pg_batas.empty:
    batas_aktif = str(df_pg_batas.iloc[0]["Status"]).strip().upper() == "AKTIF"

if batas_aktif:
    status, pesan, batas, sisa, keluar = get_status_batas_harian(df_kas, df_pg)

    if status == "bahaya":
        st.error(pesan)
    elif status == "merah":
        st.error(pesan)
    elif status == "kuning":
        st.warning(pesan)
    elif status == "hijau":
        st.success(pesan)

# ── ALERT SELISIH ──
ada_selisih, nilai_selisih, tgl_selisih = get_selisih_aktif(df_cek)
if ada_selisih:
    if nilai_selisih > 0:
        st.error(f"❌ **SELISIH: KURANG {rupiah(nilai_selisih)}** ({tgl_selisih})")
    else:
        st.success(f"✅ **SELISIH: LEBIH {rupiah(abs(nilai_selisih))}** ({tgl_selisih})")

# ── CEK SELISIH ──
cek = st.toggle("🔎 Cek Selisih", value=False, key="toggle_cek")

if cek:
    st.info("Hanya untuk pengecekan.")
    st.metric("💵 Di Tangan (Sistem)", rupiah(last_kas))

    kas_fisik = st.number_input(
        "Uang Fisik di Tangan",
        value=float(last_kas),
        step=1000.0, format="%.0f",
        key="input_cek_fisik"
    )
    if kas_fisik > 0:
        st.caption(f"💰 {rupiah(kas_fisik)}")

    selisih = last_kas - kas_fisik
    if selisih > 0.5:
        st.warning(f"⚠️ **KURANG: {rupiah(selisih)}**")
    elif selisih < -0.5:
        st.success(f"✅ **LEBIH: {rupiah(abs(selisih))}**")
    else:
        st.success("✅ **PAS**")

    if st.button("💾 Simpan Pengecekan", type="primary", use_container_width=True, key="btn_cek"):
        next_no_cek = get_next_no(df_cek)
        status_cek = "YA" if abs(selisih) > 0.5 else "TIDAK"
        row_cek = {
            "No": str(next_no_cek),
            "Tanggal": today_wita().strftime("%d/%m/%Y"),
            "Kas_Fisik": fmt_nominal(kas_fisik),
            "Kas_Sistem": fmt_nominal(last_kas),
            "Selisih": fmt_nominal(selisih),
            "Status_Aktif": status_cek
        }
        df_cek_baru = pd.concat([df_cek, pd.DataFrame([row_cek])], ignore_index=True)
        if safe_update(conn, WS_PENGECEKAN, df_cek_baru):
            st.success("✅ Disimpan!")
            st.rerun()

st.divider()

# ── TAB ──
tab1, tab2 = st.tabs(["📝 Input Keuangan", "📊 Data Keuangan"])

with tab1:
    rc = st.session_state["kas_rc"]

    c_h, c_b = st.columns([0.88, 0.12])
    c_h.subheader("📝 Input Transaksi")
    with c_b:
        tombol_refresh("ref_kas_input")

    c1, c2 = st.columns(2)
    with c1:
        tanggal = st.text_input("Tanggal", value=today_wita().strftime("%d/%m/%Y"), key=f"k_{rc}_tgl")
        ket_raw = st.text_input("Keterangan", key=f"k_{rc}_ket")
    with c2:
        jenis = st.selectbox("Jenis", ["MASUK", "KELUAR"], key=f"k_{rc}_jenis")
        nominal = st.number_input("Nominal", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key=f"k_{rc}_nom")

    if nominal > 0:
        st.caption(f"💰 {rupiah(nominal)}")

    tujuan = "-"
    sumber = "-"

    if jenis == "MASUK":
        st.divider()
        tujuan = st.selectbox("🎯 Tujuan", ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"], key=f"k_{rc}_tujuan")
    else:
        st.divider()
        sumber = st.selectbox("💳 Sumber", ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"], key=f"k_{rc}_sumber")
        if sumber == "UANG KAS (DI TANGAN)" and nominal > last_kas and nominal > 0:
            st.warning(f"⚠️ Melebihi saldo tangan ({rupiah(last_kas)})")
        elif sumber == "UANG DI ATM" and nominal > last_atm and nominal > 0:
            st.warning(f"⚠️ Melebihi saldo ATM ({rupiah(last_atm)})")
        elif sumber == "UANG DI SHOPEE" and nominal > last_shopee and nominal > 0:
            st.warning(f"⚠️ Melebihi saldo Shopee ({rupiah(last_shopee)})")

    if jenis == "MASUK":
        if tujuan == "SALDO KAS (DI TANGAN)":
            nk, na, ns = last_kas + nominal, last_atm, last_shopee
        elif tujuan == "UANG DI ATM":
            nk, na, ns = last_kas, last_atm + nominal, last_shopee
        else:
            nk, na, ns = last_kas, last_atm, last_shopee + nominal
    else:
        if sumber == "UANG KAS (DI TANGAN)":
            nk, na, ns = last_kas - nominal, last_atm, last_shopee
        elif sumber == "UANG DI ATM":
            nk, na, ns = last_kas, last_atm - nominal, last_shopee
        else:
            nk, na, ns = last_kas, last_atm, last_shopee - nominal

    total_baru = nk + na + ns

    if nominal > 0:
        st.divider()
        st.subheader("🏦 Preview")
        h1, h2 = st.columns(2)
        h1.metric("💵 Tangan", rupiah(nk))
        h2.metric("🏧 ATM", rupiah(na))
        h3, h4 = st.columns(2)
        h3.metric("🛒 Shopee", rupiah(ns))
        h4.metric("🏦 Total", rupiah(total_baru))

    st.divider()
    b1, b2 = st.columns(2)
    with b1:
        simpan = st.button("💾 Simpan", type="primary", use_container_width=True, key="btn_simpan")
    with b2:
        st.button("🔄 Reset", use_container_width=True, key="btn_reset", on_click=reset_form)

    if simpan:
        keterangan = ket_raw.strip().upper()
        if not keterangan:
            st.error("❌ Keterangan wajib diisi.")
        elif nominal <= 0:
            st.error("❌ Nominal harus lebih dari 0.")
        else:
            next_no = get_next_no(df_kas)
            new_row = {
                "No": str(next_no), "Tanggal": tanggal, "Keterangan": keterangan,
                "Jenis_Transaksi": jenis, "Nominal": fmt_nominal(nominal),
                "Sumber_Anggaran": sumber if jenis == "KELUAR" else "-",
                "Tujuan_Anggaran": tujuan if jenis == "MASUK" else "-",
                "Sisa_Kas_Di_Tangan": fmt_nominal(nk), "Sisa_ATM": fmt_nominal(na),
                "Sisa_Shopee": fmt_nominal(ns), "Sisa_Kas_Seluruh": fmt_nominal(total_baru),
                "Catatan": "-"
            }
            df_baru = pd.concat([df_kas, pd.DataFrame([new_row])], ignore_index=True)
            if safe_update(conn, WS_KAS, df_baru):
                st.success("✅ Berhasil!")
                reset_form()
                st.rerun()

with tab2:
    c_h2, c_b2 = st.columns([0.88, 0.12])
    c_h2.subheader("📊 Histori")
    with c_b2:
        tombol_refresh("ref_kas_data")

    df_valid = df_kas[df_kas["No"] != "-"].copy()
    if df_valid.empty:
        st.info("Belum ada data.")
    else:
        filt = st.selectbox("Filter", ["Semua", "MASUK", "KELUAR", "TRANSFER"], key="filter_kas")
        if filt != "Semua":
            df_valid = df_valid[df_valid["Jenis_Transaksi"] == filt]
        kolom = ["No","Tanggal","Keterangan","Jenis_Transaksi","Nominal",
                 "Sumber_Anggaran","Tujuan_Anggaran",
                 "Sisa_Kas_Di_Tangan","Sisa_ATM","Sisa_Shopee","Sisa_Kas_Seluruh"]
        kolom_ada = [k for k in kolom if k in df_valid.columns]
        st.dataframe(tampilkan_n_terakhir(df_valid, 30)[kolom_ada], use_container_width=True, hide_index=True)

st.markdown(
    '<div style="text-align:center; padding:30px 0 10px 0; border-top:1px solid #1e1e2a; margin-top:20px;">'
    '<p style="font-family:\'Poppins\',sans-serif; font-size:0.55rem; color:#3a3a4a; margin:0; text-align:center;">'
    'Keuangan Pribadi - Financial Tracker</p></div>',
    unsafe_allow_html=True
)
