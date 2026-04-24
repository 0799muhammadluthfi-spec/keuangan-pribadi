# ==========================================
# pages/2_⚙️_Pengaturan.py
# ==========================================
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css, render_top_nav
from utils.helpers import (
    WS_KAS,
    WS_PENGATURAN,
    KOLOM_KAS,
    KOLOM_PENGATURAN,
    load_data,
    safe_update,
    get_next_no,
    pastikan_kolom,
    tombol_refresh,
    to_float,
    fmt_nominal,
    rupiah,
    get_last_saldo,
    get_gaji,
    get_pengaturan,
    hitung_pengeluaran_tetap_bulanan,
    hitung_pengeluaran_harian,
    hitung_hasil_bersih_bulanan,
    get_jumlah_hari_bulan_ini,
    get_sisa_hari_bulan_ini,
    today_wita
)

# ==========================================
# KONFIGURASI
# ==========================================
st.set_page_config(
    page_title="Pengaturan | Keuangan Pribadi",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_css()

# ==========================================
# KONEKSI
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# NAVIGATION
# ==========================================
render_top_nav(active="setting")

# ==========================================
# LOAD DATA
# ==========================================
df_pg = load_data(conn, WS_PENGATURAN)
df_pg = pastikan_kolom(df_pg, KOLOM_PENGATURAN)

df_kas = load_data(conn, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)

# ==========================================
# HEADER
# ==========================================
st.markdown(
    """
    <div style="text-align:center; padding:5px 0;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:1.3rem; font-weight:700;
                  color:#f5f5f5; margin:0;">
            ⚙️ Pengaturan
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# TAB
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 Gaji",
    "💳 Pengeluaran Tetap",
    "🏦 Tabungan",
    "🔄 Transfer",
    "📊 Ringkasan Bulanan"
])

# ==========================================
# TAB 1 — GAJI
# ==========================================
with tab1:
    st.subheader("💼 Input Gaji")

    gaji_sekarang = get_gaji(df_pg)

    if gaji_sekarang > 0:
        st.metric("Gaji Saat Ini", rupiah(gaji_sekarang))
    else:
        st.info("Gaji belum diatur.")

    st.divider()

    with st.form("form_gaji", clear_on_submit=True):
        nominal_gaji = st.number_input(
            "Nominal Gaji Baru",
            min_value=0.0,
            value=float(gaji_sekarang) if gaji_sekarang > 0 else 0.0,
            step=100000.0,
            format="%.0f"
        )

        if nominal_gaji > 0:
            st.caption(f"💰 {rupiah(nominal_gaji)}")

        b1, b2 = st.columns(2)
        with b1:
            simpan_gaji = st.form_submit_button(
                "💾 Simpan Gaji",
                type="primary",
                use_container_width=True
            )
        with b2:
            reset_gaji = st.form_submit_button(
                "🔄 Reset",
                use_container_width=True
            )

        if reset_gaji:
            st.rerun()

        if simpan_gaji:
            if nominal_gaji <= 0:
                st.error("❌ Nominal gaji harus lebih dari 0.")
            else:
                # Hapus gaji lama kalau ada
                df_pg = df_pg[df_pg["Jenis"] != "GAJI"].copy()

                row_gaji = {
                    "Jenis": "GAJI",
                    "Nama": "GAJI BULANAN",
                    "Nominal": fmt_nominal(nominal_gaji),
                    "Periode": "BULANAN",
                    "Status": "AKTIF"
                }

                df_pg = pd.concat(
                    [df_pg, pd.DataFrame([row_gaji])],
                    ignore_index=True
                )

                if safe_update(conn, WS_PENGATURAN, df_pg):
                    st.success("✅ Gaji berhasil disimpan!")
                    st.rerun()

    st.divider()

    # Tombol masukkan gaji ke transaksi
    if gaji_sekarang > 0:
        st.subheader("🚀 Masukkan Gaji ke Kas")
        st.info(f"Klik tombol di bawah untuk memasukkan gaji **{rupiah(gaji_sekarang)}** ke transaksi kas.")

        tujuan_gaji = st.selectbox(
            "Tujuan Gaji Masuk Ke",
            ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"],
            key="tujuan_gaji"
        )

        if st.button(
            f"💰 Masukkan Gaji {rupiah(gaji_sekarang)}",
            type="primary",
            use_container_width=True,
            key="btn_masukkan_gaji"
        ):
            last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)

            if tujuan_gaji == "SALDO KAS (DI TANGAN)":
                new_kas = last_kas + gaji_sekarang
                new_atm = last_atm
                new_shopee = last_shopee
            elif tujuan_gaji == "UANG DI ATM":
                new_kas = last_kas
                new_atm = last_atm + gaji_sekarang
                new_shopee = last_shopee
            else:
                new_kas = last_kas
                new_atm = last_atm
                new_shopee = last_shopee + gaji_sekarang

            total_baru = new_kas + new_atm + new_shopee

            next_no = get_next_no(df_kas)
            row_gaji_kas = {
                "No": str(next_no),
                "Tanggal": today_wita().strftime("%d/%m/%Y"),
                "Keterangan": "GAJI BULANAN",
                "Jenis_Transaksi": "MASUK",
                "Nominal": fmt_nominal(gaji_sekarang),
                "Sumber_Anggaran": "-",
                "Tujuan_Anggaran": tujuan_gaji,
                "Sisa_Kas_Di_Tangan": fmt_nominal(new_kas),
                "Sisa_ATM": fmt_nominal(new_atm),
                "Sisa_Shopee": fmt_nominal(new_shopee),
                "Sisa_Kas_Seluruh": fmt_nominal(total_baru),
                "Catatan": "INPUT GAJI OTOMATIS"
            }

            df_kas_baru = pd.concat(
                [df_kas, pd.DataFrame([row_gaji_kas])],
                ignore_index=True
            )
            if safe_update(conn, WS_KAS, df_kas_baru):
                st.success(f"✅ Gaji {rupiah(gaji_sekarang)} berhasil dimasukkan ke kas!")
                st.rerun()

# ==========================================
# TAB 2 — PENGELUARAN TETAP
# ==========================================
with tab2:
    st.subheader("💳 Pengeluaran Tetap")

    aktif_pengeluaran = st.toggle(
        "Aktifkan Pengeluaran Tetap",
        value=True,
        key="toggle_pengeluaran"
    )

    df_pengeluaran = get_pengaturan(df_pg, "PENGELUARAN")

    if not df_pengeluaran.empty and aktif_pengeluaran:
        st.dataframe(
            df_pengeluaran[["Nama", "Nominal", "Periode"]],
            use_container_width=True,
            hide_index=True
        )

        total_bulanan = hitung_pengeluaran_tetap_bulanan(df_pg)
        total_harian = hitung_pengeluaran_harian(df_pg)

        m1, m2 = st.columns(2)
        m1.metric("💳 Total/Bulan", rupiah(total_bulanan))
        m2.metric("📅 Total/Hari", rupiah(total_harian))
    elif aktif_pengeluaran:
        st.info("Belum ada pengeluaran tetap.")

    st.divider()
    st.subheader("➕ Tambah Pengeluaran Tetap")

    with st.form("form_pengeluaran", clear_on_submit=True):
        nama_p = st.text_input("Nama Pengeluaran").strip().upper()
        nominal_p = st.number_input(
            "Nominal",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            format="%.0f"
        )
        if nominal_p > 0:
            st.caption(f"💰 {rupiah(nominal_p)}")

        periode_p = st.selectbox(
            "Periode",
            ["HARIAN", "MINGGUAN", "BULANAN"]
        )

        b1, b2 = st.columns(2)
        with b1:
            simpan_p = st.form_submit_button(
                "💾 Simpan",
                type="primary",
                use_container_width=True
            )
        with b2:
            reset_p = st.form_submit_button(
                "🔄 Reset",
                use_container_width=True
            )

        if reset_p:
            st.rerun()

        if simpan_p:
            if not nama_p:
                st.error("❌ Nama pengeluaran wajib diisi.")
            elif nominal_p <= 0:
                st.error("❌ Nominal harus lebih dari 0.")
            else:
                row_p = {
                    "Jenis": "PENGELUARAN",
                    "Nama": nama_p,
                    "Nominal": fmt_nominal(nominal_p),
                    "Periode": periode_p,
                    "Status": "AKTIF"
                }

                df_pg_baru = pd.concat(
                    [df_pg, pd.DataFrame([row_p])],
                    ignore_index=True
                )
                if safe_update(conn, WS_PENGATURAN, df_pg_baru):
                    st.success(f"✅ Pengeluaran '{nama_p}' berhasil ditambahkan!")
                    st.rerun()

    # Hapus pengeluaran
    if not df_pengeluaran.empty:
        st.divider()
        st.subheader("🗑️ Hapus Pengeluaran Tetap")

        nama_list = df_pengeluaran["Nama"].tolist()
        hapus_nama = st.selectbox(
            "Pilih yang mau dihapus",
            nama_list,
            key="hapus_pengeluaran"
        )

        if st.button("🗑️ Hapus", key="btn_hapus_p", use_container_width=True):
            df_pg = df_pg[~(
                (df_pg["Jenis"] == "PENGELUARAN") &
                (df_pg["Nama"] == hapus_nama)
            )].copy()

            if safe_update(conn, WS_PENGATURAN, df_pg):
                st.success(f"✅ '{hapus_nama}' berhasil dihapus!")
                st.rerun()

# ==========================================
# TAB 3 — TABUNGAN
# ==========================================
with tab3:
    st.subheader("🏦 Target Tabungan")

    aktif_tabungan = st.toggle(
        "Aktifkan Tabungan",
        value=True,
        key="toggle_tabungan"
    )

    d_tabungan = get_pengaturan(df_pg, "TABUNGAN")
    tabungan_sekarang = to_float(d_tabungan.iloc[0]["Nominal"]) if not d_tabungan.empty else 0

    if tabungan_sekarang > 0 and aktif_tabungan:
        st.metric("🏦 Tabungan/Bulan", rupiah(tabungan_sekarang))
    elif aktif_tabungan:
        st.info("Tabungan belum diatur.")

    if aktif_tabungan:
        st.divider()

        with st.form("form_tabungan", clear_on_submit=True):
            nominal_tab = st.number_input(
                "Nominal Tabungan/Bulan",
                min_value=0.0,
                value=float(tabungan_sekarang) if tabungan_sekarang > 0 else 0.0,
                step=50000.0,
                format="%.0f"
            )
            if nominal_tab > 0:
                st.caption(f"💰 {rupiah(nominal_tab)}")

            if st.form_submit_button(
                "💾 Simpan Tabungan",
                type="primary",
                use_container_width=True
            ):
                if nominal_tab <= 0:
                    st.error("❌ Nominal harus lebih dari 0.")
                else:
                    df_pg = df_pg[df_pg["Jenis"] != "TABUNGAN"].copy()

                    row_tab = {
                        "Jenis": "TABUNGAN",
                        "Nama": "TARGET TABUNGAN",
                        "Nominal": fmt_nominal(nominal_tab),
                        "Periode": "BULANAN",
                        "Status": "AKTIF"
                    }

                    df_pg = pd.concat(
                        [df_pg, pd.DataFrame([row_tab])],
                        ignore_index=True
                    )
                    if safe_update(conn, WS_PENGATURAN, df_pg):
                        st.success("✅ Tabungan berhasil disimpan!")
                        st.rerun()

# ==========================================
# TAB 4 — TRANSFER ANTAR ANGGARAN
# ==========================================
with tab4:
    st.subheader("🔄 Transfer Antar Anggaran")
    st.info("Pindahkan uang antar saldo tanpa transaksi masuk/keluar.")

    last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)

    # Tampilkan saldo
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("💵 Tangan", rupiah(last_kas))
    tc2.metric("🏧 ATM", rupiah(last_atm))
    tc3.metric("🛒 Shopee", rupiah(last_shopee))

    st.divider()

    pilihan_saldo = ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"]

    tf1, tf2 = st.columns(2)
    with tf1:
        dari = st.selectbox("Dari", pilihan_saldo, key="transfer_dari")
    with tf2:
        ke_options = [x for x in pilihan_saldo if x != dari]
        ke = st.selectbox("Ke", ke_options, key="transfer_ke")

    nominal_tf = st.number_input(
        "Nominal Transfer",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%.0f",
        key="transfer_nominal"
    )

    if nominal_tf > 0:
        st.caption(f"💰 {rupiah(nominal_tf)}")

        # Cek saldo cukup
        if dari == "UANG KAS (DI TANGAN)" and nominal_tf > last_kas:
            st.warning(f"⚠️ Saldo kas tangan ({rupiah(last_kas)}) tidak cukup!")
        elif dari == "UANG DI ATM" and nominal_tf > last_atm:
            st.warning(f"⚠️ Saldo ATM ({rupiah(last_atm)}) tidak cukup!")
        elif dari == "UANG DI SHOPEE" and nominal_tf > last_shopee:
            st.warning(f"⚠️ Saldo Shopee ({rupiah(last_shopee)}) tidak cukup!")

    if st.button(
        "🔄 Transfer Sekarang",
        type="primary",
        use_container_width=True,
        key="btn_transfer"
    ):
        if nominal_tf <= 0:
            st.error("❌ Nominal harus lebih dari 0.")
        else:
            new_kas = last_kas
            new_atm = last_atm
            new_shopee = last_shopee

            # Kurangi sumber
            if dari == "UANG KAS (DI TANGAN)":
                new_kas -= nominal_tf
            elif dari == "UANG DI ATM":
                new_atm -= nominal_tf
            elif dari == "UANG DI SHOPEE":
                new_shopee -= nominal_tf

            # Tambahkan tujuan
            if ke == "UANG KAS (DI TANGAN)":
                new_kas += nominal_tf
            elif ke == "UANG DI ATM":
                new_atm += nominal_tf
            elif ke == "UANG DI SHOPEE":
                new_shopee += nominal_tf

            total_baru = new_kas + new_atm + new_shopee

            next_no = get_next_no(df_kas)
            row_transfer = {
                "No": str(next_no),
                "Tanggal": today_wita().strftime("%d/%m/%Y"),
                "Keterangan": f"TRANSFER: {dari} → {ke}",
                "Jenis_Transaksi": "TRANSFER",
                "Nominal": fmt_nominal(nominal_tf),
                "Sumber_Anggaran": dari,
                "Tujuan_Anggaran": ke,
                "Sisa_Kas_Di_Tangan": fmt_nominal(new_kas),
                "Sisa_ATM": fmt_nominal(new_atm),
                "Sisa_Shopee": fmt_nominal(new_shopee),
                "Sisa_Kas_Seluruh": fmt_nominal(total_baru),
                "Catatan": "TRANSFER ANTAR ANGGARAN"
            }

            df_kas_baru = pd.concat(
                [df_kas, pd.DataFrame([row_transfer])],
                ignore_index=True
            )
            if safe_update(conn, WS_KAS, df_kas_baru):
                st.success(
                    f"✅ Transfer {rupiah(nominal_tf)} dari {dari} ke {ke} berhasil!"
                )
                st.rerun()

# ==========================================
# TAB 5 — RINGKASAN BULANAN
# ==========================================
with tab5:
    st.subheader("📊 Ringkasan Keuangan Bulan Ini")

    gaji = get_gaji(df_pg)
    pengeluaran_bulanan = hitung_pengeluaran_tetap_bulanan(df_pg)
    pengeluaran_harian = hitung_pengeluaran_harian(df_pg)
    hasil_bersih = hitung_hasil_bersih_bulanan(df_pg)

    d_tab = get_pengaturan(df_pg, "TABUNGAN")
    tabungan = to_float(d_tab.iloc[0]["Nominal"]) if not d_tab.empty else 0

    jumlah_hari = get_jumlah_hari_bulan_ini()
    sisa_hari = get_sisa_hari_bulan_ini()

    last_seluruh, last_kas, last_atm, last_shopee = get_last_saldo(df_kas)

    # Info bulan
    st.markdown(
        f"""
        <div style="text-align:center; padding:12px;
                    background: #13131a; border: 1px solid #2a2a3a;
                    border-radius:12px; margin-bottom:16px;">
            <p style="font-family:'Poppins',sans-serif;
                      font-size:0.75rem; color:#8a8a9a; margin:0;">
                Bulan ini: <b style="color:#c4a35a;">{jumlah_hari} hari</b>
                &nbsp;|&nbsp;
                Sisa: <b style="color:#c4a35a;">{sisa_hari} hari</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Metric
    m1, m2 = st.columns(2)
    m1.metric("💼 Gaji", rupiah(gaji))
    m2.metric("💳 Pengeluaran Tetap/Bulan", rupiah(pengeluaran_bulanan))

    m3, m4 = st.columns(2)
    m3.metric("🏦 Tabungan/Bulan", rupiah(tabungan))
    m4.metric("📅 Pengeluaran/Hari", rupiah(pengeluaran_harian))

    st.divider()

    # Hasil bersih
    if hasil_bersih >= 0:
        st.success(f"✨ **Hasil Bersih: {rupiah(hasil_bersih)}**")
    else:
        st.error(f"❌ **Hasil Bersih: {rupiah(hasil_bersih)}** (DEFISIT)")

    st.divider()

    # Budget harian tersedia
    if last_kas > 0 and sisa_hari > 0:
        budget_harian = last_kas / sisa_hari

        st.metric("🎯 Budget Harian Tersedia", rupiah(budget_harian))

        if budget_harian < pengeluaran_harian:
            st.warning(
                f"⚠️ Budget harian ({rupiah(budget_harian)}) "
                f"lebih kecil dari kebutuhan harian ({rupiah(pengeluaran_harian)}).\n\n"
                f"Pertimbangkan untuk mengurangi pengeluaran!"
            )
        else:
            sisa_budget = budget_harian - pengeluaran_harian
            st.success(
                f"✅ Aman! Sisa budget harian setelah pengeluaran tetap: "
                f"**{rupiah(sisa_budget)}**"
            )
    else:
        st.info("Belum ada saldo kas untuk menghitung budget harian.")

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
