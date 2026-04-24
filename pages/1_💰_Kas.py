# ==========================================
# pages/1_💰_Kas.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css, render_top_nav
from utils.helpers import (
    WS_KAS,
    WS_PENGATURAN,
    WS_PENGECEKAN,
    KOLOM_KAS,
    KOLOM_PENGATURAN,
    KOLOM_PENGECEKAN,
    load_data,
    safe_update,
    get_next_no,
    pastikan_kolom,
    tampilkan_n_terakhir,
    tombol_refresh,
    to_float,
    fmt_nominal,
    rupiah,
    get_last_saldo,
    hitung_ringkasan,
    get_selisih_aktif,
    cek_warning_harian,
    today_wita
)

# ==========================================
# KONFIGURASI
# ==========================================
st.set_page_config(
    page_title="Kas | Keuangan Pribadi",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_css()

# ==========================================
# KONEKSI
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# RESET COUNTER
# ==========================================
if "kas_rc" not in st.session_state:
    st.session_state["kas_rc"] = 0

def reset_form():
    st.session_state["kas_rc"] += 1

# ==========================================
# NAVIGATION
# ==========================================
render_top_nav(active="kas")

# ==========================================
# LOAD DATA
# ==========================================
df_kas = load_data(conn, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)

df_pg = load_data(conn, WS_PENGATURAN)
df_pg = pastikan_kolom(df_pg, KOLOM_PENGATURAN)

df_cek = load_data(conn, WS_PENGECEKAN)
df_cek = pastikan_kolom(df_cek, KOLOM_PENGECEKAN)

# ==========================================
# HEADER
# ==========================================
st.markdown(
    """
    <div style="text-align:center; padding:5px 0;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:1.3rem; font-weight:700;
                  color:#f5f5f5; margin:0;">
            💰 Kas
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# RINGKASAN
# ==========================================
last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)
total_masuk, total_keluar = hitung_ringkasan(df_kas)

# Baris 1
r1c1, r1c2, r1c3 = st.columns(3)
r1c1.metric("📥 Masuk", rupiah(total_masuk))
r1c2.metric("📤 Keluar", rupiah(total_keluar))
r1c3.metric("🏦 Total", rupiah(last_seluruh))

# Baris 2
r2c1, r2c2, r2c3 = st.columns(3)
r2c1.metric("💵 Tangan", rupiah(last_kas))
r2c2.metric("🏧 ATM", rupiah(last_atm))
r2c3.metric("🛒 Shopee", rupiah(last_shopee))

st.divider()

# ==========================================
# WARNING BATAS HARIAN
# ==========================================
level, pesan = cek_warning_harian(df_kas, df_pg)
if level == "bahaya":
    st.error(pesan)
elif level == "warning":
    st.warning(pesan)

# ==========================================
# ALERT SELISIH AKTIF
# ==========================================
ada_selisih, nilai_selisih, tgl_selisih = get_selisih_aktif(df_cek)
if ada_selisih:
    if nilai_selisih > 0:
        st.error(
            f"❌ **SELISIH AKTIF: KURANG {rupiah(nilai_selisih)}** "
            f"(Pengecekan: {tgl_selisih})"
        )
    else:
        st.success(
            f"✅ **SELISIH AKTIF: LEBIH {rupiah(abs(nilai_selisih))}** "
            f"(Pengecekan: {tgl_selisih})"
        )

# ==========================================
# PENGECEKAN SELISIH (ON/OFF)
# ==========================================
cek_selisih = st.toggle(
    "🔎 Cek Selisih Kas",
    value=False,
    key="toggle_cek_selisih"
)

if cek_selisih:
    st.info("Hanya untuk pengecekan. Tidak mengubah transaksi.")

    st.metric("💵 Kas di Tangan (Sistem)", rupiah(last_kas))

    kas_fisik = st.number_input(
        "Input Kas Fisik di Tangan",
        value=float(last_kas),
        step=1000.0,
        format="%.0f",
        key="input_cek_fisik"
    )

    selisih = last_kas - kas_fisik

    if selisih > 0.5:
        st.warning(f"⚠️ **KURANG: {rupiah(selisih)}**")
    elif selisih < -0.5:
        st.success(f"✅ **LEBIH: {rupiah(abs(selisih))}**")
    else:
        st.success("✅ **PAS / Rp 0**")

    if st.button("💾 Simpan Hasil Pengecekan", type="primary",
                 use_container_width=True, key="btn_simpan_cek"):
        next_no_cek = get_next_no(df_cek)
        status = "YA" if abs(selisih) > 0.5 else "TIDAK"

        row_cek = {
            "No": str(next_no_cek),
            "Tanggal": today_wita().strftime("%d/%m/%Y"),
            "Kas_Fisik": fmt_nominal(kas_fisik),
            "Kas_Sistem": fmt_nominal(last_kas),
            "Selisih": fmt_nominal(selisih),
            "Status_Aktif": status
        }

        df_cek_baru = pd.concat(
            [df_cek, pd.DataFrame([row_cek])],
            ignore_index=True
        )
        if safe_update(conn, WS_PENGECEKAN, df_cek_baru):
            st.success("✅ Hasil pengecekan disimpan!")
            st.rerun()

st.divider()

# ==========================================
# TAB
# ==========================================
tab1, tab2 = st.tabs(["📝 Input Kas", "📊 Data Kas"])

# ==========================================
# TAB 1 — INPUT KAS
# ==========================================
with tab1:
    rc = st.session_state["kas_rc"]

    c_head, c_btn = st.columns([0.88, 0.12])
    c_head.subheader("📝 Input Transaksi")
    with c_btn:
        tombol_refresh("ref_kas_input")

    # Field dasar
    c1, c2 = st.columns(2)
    with c1:
        tanggal = st.text_input(
            "Tanggal",
            value=today_wita().strftime("%d/%m/%Y"),
            key=f"k_{rc}_tgl"
        )
        keterangan_raw = st.text_input(
            "Keterangan",
            key=f"k_{rc}_ket"
        )
    with c2:
        jenis = st.selectbox(
            "Jenis Transaksi",
            ["MASUK", "KELUAR"],
            key=f"k_{rc}_jenis"
        )
        nominal = st.number_input(
            "Nominal",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.0f",
            key=f"k_{rc}_nom"
        )

    if nominal > 0:
        st.caption(f"💰 {rupiah(nominal)}")

    # Default
    tujuan = "-"
    sumber = "-"

    # ── MASUK ──
    if jenis == "MASUK":
        st.divider()
        tujuan = st.selectbox(
            "🎯 Tujuan Anggaran",
            ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"],
            key=f"k_{rc}_tujuan"
        )

    # ── KELUAR ──
    else:
        st.divider()
        sumber = st.selectbox(
            "💳 Sumber Anggaran",
            ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"],
            key=f"k_{rc}_sumber"
        )

        if sumber == "UANG KAS (DI TANGAN)" and nominal > last_kas and nominal > 0:
            st.warning(f"⚠️ Melebihi saldo kas ({rupiah(last_kas)})")
        elif sumber == "UANG DI ATM" and nominal > last_atm and nominal > 0:
            st.warning(f"⚠️ Melebihi saldo ATM ({rupiah(last_atm)})")
        elif sumber == "UANG DI SHOPEE" and nominal > last_shopee and nominal > 0:
            st.warning(f"⚠️ Melebihi saldo Shopee ({rupiah(last_shopee)})")

    # ── HITUNG SALDO BARU ──
    if jenis == "MASUK":
        if tujuan == "SALDO KAS (DI TANGAN)":
            new_kas = last_kas + nominal
            new_atm = last_atm
            new_shopee = last_shopee
        elif tujuan == "UANG DI ATM":
            new_kas = last_kas
            new_atm = last_atm + nominal
            new_shopee = last_shopee
        else:
            new_kas = last_kas
            new_atm = last_atm
            new_shopee = last_shopee + nominal
    else:
        if sumber == "UANG KAS (DI TANGAN)":
            new_kas = last_kas - nominal
            new_atm = last_atm
            new_shopee = last_shopee
        elif sumber == "UANG DI ATM":
            new_kas = last_kas
            new_atm = last_atm - nominal
            new_shopee = last_shopee
        else:
            new_kas = last_kas
            new_atm = last_atm
            new_shopee = last_shopee - nominal

    total_baru = new_kas + new_atm + new_shopee

    # ── PREVIEW SALDO BARU ──
    if nominal > 0:
        st.divider()
        st.subheader("🏦 Preview Saldo")
        h1, h2, h3, h4 = st.columns(4)
        h1.metric("💵 Tangan", rupiah(new_kas))
        h2.metric("🏧 ATM", rupiah(new_atm))
        h3.metric("🛒 Shopee", rupiah(new_shopee))
        h4.metric("🏦 Total", rupiah(total_baru))

    # ── TOMBOL ──
    st.divider()
    b1, b2 = st.columns(2)
    with b1:
        simpan = st.button(
            "💾 Simpan",
            type="primary",
            use_container_width=True,
            key="btn_simpan_kas"
        )
    with b2:
        st.button(
            "🔄 Reset",
            use_container_width=True,
            key="btn_reset_kas",
            on_click=reset_form
        )

    if simpan:
        keterangan = keterangan_raw.strip().upper()
        if not keterangan:
            st.error("❌ Keterangan wajib diisi.")
        elif nominal <= 0:
            st.error("❌ Nominal harus lebih dari 0.")
        else:
            next_no = get_next_no(df_kas)
            new_row = {
                "No": str(next_no),
                "Tanggal": tanggal,
                "Keterangan": keterangan,
                "Jenis_Transaksi": jenis,
                "Nominal": fmt_nominal(nominal),
                "Sumber_Anggaran": sumber if jenis == "KELUAR" else "-",
                "Tujuan_Anggaran": tujuan if jenis == "MASUK" else "-",
                "Sisa_Kas_Di_Tangan": fmt_nominal(new_kas),
                "Sisa_ATM": fmt_nominal(new_atm),
                "Sisa_Shopee": fmt_nominal(new_shopee),
                "Sisa_Kas_Seluruh": fmt_nominal(total_baru),
                "Catatan": "-"
            }

            df_baru = pd.concat(
                [df_kas, pd.DataFrame([new_row])],
                ignore_index=True
            )
            if safe_update(conn, WS_KAS, df_baru):
                st.success("✅ Transaksi berhasil disimpan!")
                reset_form()
                st.rerun()

# ==========================================
# TAB 2 — DATA KAS
# ==========================================
with tab2:
    c_head2, c_btn2 = st.columns([0.88, 0.12])
    c_head2.subheader("📊 Histori Transaksi")
    with c_btn2:
        tombol_refresh("ref_kas_data")

    df_valid = df_kas[df_kas["No"] != "-"].copy()

    if df_valid.empty:
        st.info("Belum ada data transaksi.")
    else:
        # Filter
        filter_jenis = st.selectbox(
            "Filter",
            ["Semua", "MASUK", "KELUAR", "TRANSFER"],
            key="filter_kas"
        )

        if filter_jenis != "Semua":
            df_valid = df_valid[df_valid["Jenis_Transaksi"] == filter_jenis]

        kolom = [
            "No", "Tanggal", "Keterangan",
            "Jenis_Transaksi", "Nominal",
            "Sumber_Anggaran", "Tujuan_Anggaran",
            "Sisa_Kas_Di_Tangan", "Sisa_ATM",
            "Sisa_Shopee", "Sisa_Kas_Seluruh"
        ]
        kolom_ada = [k for k in kolom if k in df_valid.columns]

        st.dataframe(
            tampilkan_n_terakhir(df_valid, 30)[kolom_ada],
            use_container_width=True,
            hide_index=True
        )

# ==========================================
# FOOTER
# ==========================================
st.markdown(
    """
    <div style="text-align:center; padding:30px 0 10px 0;
                border-top:1px solid #1e1e2a; margin-top:20px;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:0.55rem; font-weight:400;
                  color:#3a3a4a; margin:0;">
            Keuangan Pribadi • Financial Tracker
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
