import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from utils.css_styles import inject_css, render_top_nav
from utils.helpers import (
    WS_KAS, WS_PENGATURAN, WS_PENGECEKAN,
    KOLOM_KAS, KOLOM_PENGATURAN, KOLOM_PENGECEKAN,
    load_data, safe_update, get_next_no, pastikan_kolom,
    tampilkan_n_terakhir, tombol_refresh,
    to_float, fmt_nominal, rupiah,
    get_last_saldo, hitung_ringkasan,
    get_selisih_aktif,
    hitung_saldo_siap_pakai,
    hitung_pengeluaran_hari_ini,
    get_sisa_hari_bulan_ini,
    get_tabungan,
    hitung_beban_belum_bayar,
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

# ── INPUT TRANSAKSI DULU SESUAI PERMINTAAN ──
rc = st.session_state["kas_rc"]

ch, cb = st.columns([0.88, 0.12])
ch.subheader("📝 Input Transaksi")
with cb:
    tombol_refresh("ref_input")

last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)

c1, c2 = st.columns(2)
with c1:
    tgl = st.text_input("Tanggal", value=today_wita().strftime("%d/%m/%Y"), key=f"k_{rc}_tgl")
    ket = st.text_input("Keterangan", key=f"k_{rc}_ket")
with c2:
    jns = st.selectbox("Jenis", ["MASUK", "KELUAR"], key=f"k_{rc}_jns")
    nom = st.number_input("Nominal", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key=f"k_{rc}_nom")

if nom > 0:
    st.caption(f"💰 {rupiah(nom)}")

tujuan = "-"
sumber = "-"

if jns == "MASUK":
    st.divider()
    tujuan = st.selectbox("🎯 Tujuan", ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"], key=f"k_{rc}_tuj")
else:
    st.divider()
    sumber = st.selectbox("💳 Sumber", ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"], key=f"k_{rc}_smb")

    if sumber == "UANG KAS (DI TANGAN)" and nom > last_kas and nom > 0:
        st.warning(f"⚠️ Melebihi tangan ({rupiah(last_kas)})")
    elif sumber == "UANG DI ATM" and nom > last_atm and nom > 0:
        st.warning(f"⚠️ Melebihi ATM ({rupiah(last_atm)})")
    elif sumber == "UANG DI SHOPEE" and nom > last_shopee and nom > 0:
        st.warning(f"⚠️ Melebihi Shopee ({rupiah(last_shopee)})")

if jns == "MASUK":
    if tujuan == "SALDO KAS (DI TANGAN)":
        nk, na, ns = last_kas + nom, last_atm, last_shopee
    elif tujuan == "UANG DI ATM":
        nk, na, ns = last_kas, last_atm + nom, last_shopee
    else:
        nk, na, ns = last_kas, last_atm, last_shopee + nom
else:
    if sumber == "UANG KAS (DI TANGAN)":
        nk, na, ns = last_kas - nom, last_atm, last_shopee
    elif sumber == "UANG DI ATM":
        nk, na, ns = last_kas, last_atm - nom, last_shopee
    else:
        nk, na, ns = last_kas, last_atm, last_shopee - nom

tt = nk + na + ns

if nom > 0:
    st.divider()
    st.subheader("🏦 Preview")
    h1, h2 = st.columns(2)
    h1.metric("💵 Tangan", rupiah(nk))
    h2.metric("🏧 ATM", rupiah(na))
    h3, h4 = st.columns(2)
    h3.metric("🛒 Shopee", rupiah(ns))
    h4.metric("🏦 Total", rupiah(tt))

st.divider()
b1, b2 = st.columns(2)
with b1:
    simpan = st.button("💾 Simpan", type="primary", use_container_width=True, key="btn_s")
with b2:
    st.button("🔄 Reset", use_container_width=True, key="btn_r", on_click=reset_form)

if simpan:
    keterangan = ket.strip().upper()
    if not keterangan:
        st.error("❌ Keterangan wajib.")
    elif nom <= 0:
        st.error("❌ Nominal > 0.")
    else:
        nno = get_next_no(df_kas)
        row = {
            "No": str(nno), "Tanggal": tgl, "Keterangan": keterangan,
            "Jenis_Transaksi": jns, "Nominal": fmt_nominal(nom),
            "Sumber_Anggaran": sumber if jns == "KELUAR" else "-",
            "Tujuan_Anggaran": tujuan if jns == "MASUK" else "-",
            "Sisa_Kas_Di_Tangan": fmt_nominal(nk), "Sisa_ATM": fmt_nominal(na),
            "Sisa_Shopee": fmt_nominal(ns), "Sisa_Kas_Seluruh": fmt_nominal(tt),
            "Catatan": "-"
        }
        df_b = pd.concat([df_kas, pd.DataFrame([row])], ignore_index=True)
        if safe_update(conn, WS_KAS, df_b):
            st.success("✅ Berhasil!")
            reset_form()
            st.rerun()

st.divider()

# ── BATAS HARIAN SETELAH INPUT SESUAI PERMINTAAN ──
df_pg_batas = df_pg[(df_pg["Jenis"] == "SETTING") & (df_pg["Nama"] == "BATAS_HARIAN")]
batas_aktif = False
if not df_pg_batas.empty:
    batas_aktif = str(df_pg_batas.iloc[0]["Status"]).strip().upper() == "AKTIF"

if batas_aktif:
    saldo_siap = float(hitung_saldo_siap_pakai(df_kas, df_pg) or 0)
    sisa_hari = int(get_sisa_hari_bulan_ini() or 1)
    keluar_val = float(hitung_pengeluaran_hari_ini(df_kas) or 0)

    batas_val = float(saldo_siap / sisa_hari) if sisa_hari > 0 and saldo_siap > 0 else 0.0
    sisa_val = float(batas_val) - float(keluar_val)

    st.subheader("📅 Batas Harian")

    x1, x2, x3 = st.columns(3)
    x1.metric("🎯 Batas", rupiah(batas_val))
    x2.metric("📤 Keluar", rupiah(keluar_val))
    x3.metric("💵 Sisa", rupiah(sisa_val))

    if batas_val <= 0:
        st.error("❌ Tidak ada budget harian tersisa!")
    elif keluar_val <= 0:
        st.success(f"✅ Belum ada pengeluaran hari ini. Batas penuh {rupiah(batas_val)}")
    elif sisa_val < 0:
        st.error(f"🚨 Melebihi batas harian sebesar {rupiah(abs(sisa_val))}")
    elif (sisa_val / batas_val * 100) < 20:
        st.error(f"❌ Sisa batas tinggal {rupiah(sisa_val)} ({sisa_val/batas_val*100:.0f}%)")
    elif (sisa_val / batas_val * 100) < 50:
        st.warning(f"⚠️ Sisa batas {rupiah(sisa_val)} ({sisa_val/batas_val*100:.0f}%)")
    else:
        st.success(f"✅ Masih aman. Sisa {rupiah(sisa_val)} ({sisa_val/batas_val*100:.0f}%)")

    st.divider()

# ── CEK SELISIH ──
ada, nilai, tgl_sel = get_selisih_aktif(df_cek)
if ada:
    if nilai > 0:
        st.error(f"❌ SELISIH: KURANG {rupiah(nilai)} ({tgl_sel})")
    else:
        st.success(f"✅ SELISIH: LEBIH {rupiah(abs(nilai))} ({tgl_sel})")

cek = st.toggle("🔎 Cek Selisih", value=False, key="toggle_cek")
if cek:
    st.info("Hanya pengecekan.")
    st.metric("💵 Sistem", rupiah(last_kas))
    kas_fisik = st.number_input("Uang Fisik", value=float(last_kas), step=1000.0, format="%.0f", key="input_cek")
    if kas_fisik > 0:
        st.caption(f"💰 {rupiah(kas_fisik)}")
    selisih = last_kas - kas_fisik
    if selisih > 0.5:
        st.warning(f"⚠️ KURANG: {rupiah(selisih)}")
    elif selisih < -0.5:
        st.success(f"✅ LEBIH: {rupiah(abs(selisih))}")
    else:
        st.success("✅ PAS")
    if st.button("💾 Simpan", type="primary", use_container_width=True, key="btn_cek"):
        nno = get_next_no(df_cek)
        row = {
            "No": str(nno), "Tanggal": today_wita().strftime("%d/%m/%Y"),
            "Kas_Fisik": fmt_nominal(kas_fisik), "Kas_Sistem": fmt_nominal(last_kas),
            "Selisih": fmt_nominal(selisih), "Status_Aktif": "YA" if abs(selisih) > 0.5 else "TIDAK"
        }
        df_cb = pd.concat([df_cek, pd.DataFrame([row])], ignore_index=True)
        if safe_update(conn, WS_PENGECEKAN, df_cb):
            st.success("✅ Disimpan!")
            st.rerun()

st.divider()

# ── DATA HISTORI ──
st.subheader("📊 Data Keuangan")
dv = df_kas[df_kas["No"] != "-"].copy()
if dv.empty:
    st.info("Belum ada data.")
else:
    f = st.selectbox("Filter", ["Semua", "MASUK", "KELUAR", "TRANSFER"], key="flt")
    if f != "Semua":
        dv = dv[dv["Jenis_Transaksi"] == f]
    kol = ["No","Tanggal","Keterangan","Jenis_Transaksi","Nominal",
           "Sumber_Anggaran","Tujuan_Anggaran","Sisa_Kas_Di_Tangan","Sisa_ATM","Sisa_Shopee","Sisa_Kas_Seluruh"]
    ka = [k for k in kol if k in dv.columns]
    st.dataframe(tampilkan_n_terakhir(dv, 30)[ka], use_container_width=True, hide_index=True)

st.markdown('<div style="text-align:center;padding:30px 0 10px 0;border-top:1px solid #1e1e2a;margin-top:20px;"><p style="font-family:\'Poppins\',sans-serif;font-size:0.55rem;color:#3a3a4a;margin:0;text-align:center;">Keuangan Pribadi - Financial Tracker</p></div>', unsafe_allow_html=True)
