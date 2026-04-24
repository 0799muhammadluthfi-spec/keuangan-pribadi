# ==========================================
# pages/2_⚙️_Pengaturan.py
# ==========================================
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

from utils.css_styles import inject_css, render_top_nav
from utils.helpers import (
    WS_KAS, WS_PENGATURAN,
    KOLOM_KAS, KOLOM_PENGATURAN,
    load_data, safe_update,
    get_next_no, pastikan_kolom,
    tombol_refresh,
    to_float, fmt_nominal, rupiah,
    get_last_saldo, get_gaji,
    get_pengaturan,
    hitung_pengeluaran_tetap_bulanan,
    hitung_pengeluaran_harian,
    hitung_hasil_bersih_bulanan,
    hitung_beban_belum_bayar,
    hitung_batas_harian,
    get_jumlah_hari_bulan_ini,
    get_sisa_hari_bulan_ini,
    get_bulan_ini_str,
    get_jumlah_minggu_bulan_ini,
    today_wita
)

st.set_page_config(
    page_title="Pengaturan | Keuangan Pribadi",
    page_icon="⚙️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

inject_css()

conn = st.connection("gsheets", type=GSheetsConnection)

render_top_nav(active="setting")

df_pg = load_data(conn, WS_PENGATURAN)
df_pg = pastikan_kolom(df_pg, KOLOM_PENGATURAN)

df_kas = load_data(conn, WS_KAS)
df_kas = pastikan_kolom(df_kas, KOLOM_KAS)

st.markdown(
    """
    <div style="text-align:center; padding:5px 0;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:1.3rem; font-weight:700;
                  color:#f5f5f5; margin:0; text-align:center;">
            ⚙️ Pengaturan
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💼 Gaji",
    "💳 Pengeluaran",
    "🏦 Tabungan",
    "🔄 Transfer",
    "📊 Ringkasan"
])

# ==========================================
# TAB 1 — GAJI
# ==========================================
with tab1:
    st.subheader("💼 Pengaturan Gaji")

    gaji_sekarang = get_gaji(df_pg)

    if gaji_sekarang > 0:
        st.metric("Gaji Saat Ini", rupiah(gaji_sekarang))
    else:
        st.info("Gaji belum diatur.")

    st.divider()

    with st.form("form_gaji", clear_on_submit=True):
        nominal_gaji = st.number_input(
            "Nominal Gaji",
            min_value=0.0,
            value=float(gaji_sekarang) if gaji_sekarang > 0 else 0.0,
            step=100000.0, format="%.0f"
        )
        if nominal_gaji > 0:
            st.caption(f"💰 {rupiah(nominal_gaji)}")

        b1, b2 = st.columns(2)
        with b1:
            simpan_gaji = st.form_submit_button("💾 Simpan", type="primary", use_container_width=True)
        with b2:
            st.form_submit_button("🔄 Reset", use_container_width=True)

        if simpan_gaji and nominal_gaji > 0:
            df_pg_baru = df_pg[df_pg["Jenis"] != "GAJI"].copy()
            row = {"Jenis": "GAJI", "Nama": "GAJI BULANAN", "Nominal": fmt_nominal(nominal_gaji),
                   "Periode": "SEBULAN", "Status": "AKTIF", "Bulan_Bayar": "-", "Counter_Bayar": "0"}
            df_pg_baru = pd.concat([df_pg_baru, pd.DataFrame([row])], ignore_index=True)
            if safe_update(conn, WS_PENGATURAN, df_pg_baru):
                st.success("✅ Gaji berhasil disimpan!")
                st.rerun()

    st.divider()

    if gaji_sekarang > 0:
        st.subheader("🚀 Masukkan Gaji ke Keuangan")
        tujuan_gaji = st.selectbox(
            "Tujuan Gaji",
            ["SALDO KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"],
            key="tujuan_gaji"
        )

        if st.button(f"💰 Masukkan Gaji {rupiah(gaji_sekarang)}", type="primary", use_container_width=True):
            ls, lk, la, lsh = get_last_saldo(df_kas)
            nk, na, nsh = lk, la, lsh

            if tujuan_gaji == "SALDO KAS (DI TANGAN)":
                nk += gaji_sekarang
            elif tujuan_gaji == "UANG DI ATM":
                na += gaji_sekarang
            else:
                nsh += gaji_sekarang

            total = nk + na + nsh
            next_no = get_next_no(df_kas)

            row = {
                "No": str(next_no), "Tanggal": today_wita().strftime("%d/%m/%Y"),
                "Keterangan": "GAJI BULANAN", "Jenis_Transaksi": "MASUK",
                "Nominal": fmt_nominal(gaji_sekarang), "Sumber_Anggaran": "-",
                "Tujuan_Anggaran": tujuan_gaji,
                "Sisa_Kas_Di_Tangan": fmt_nominal(nk), "Sisa_ATM": fmt_nominal(na),
                "Sisa_Shopee": fmt_nominal(nsh), "Sisa_Kas_Seluruh": fmt_nominal(total),
                "Catatan": "INPUT GAJI OTOMATIS"
            }

            df_kas_baru = pd.concat([df_kas, pd.DataFrame([row])], ignore_index=True)
            if safe_update(conn, WS_KAS, df_kas_baru):
                st.success(f"✅ Gaji {rupiah(gaji_sekarang)} berhasil dimasukkan!")
                st.rerun()

# ==========================================
# TAB 2 — PENGELUARAN TETAP
# ==========================================
with tab2:
    st.subheader("💳 Pengeluaran Tetap")

    aktif_p = st.toggle("Aktifkan Pengeluaran Tetap", value=True, key="toggle_p")

    df_pengeluaran = get_pengaturan(df_pg, "PENGELUARAN")
    bulan_ini = get_bulan_ini_str()
    jml_minggu = get_jumlah_minggu_bulan_ini()

    if not df_pengeluaran.empty and aktif_p:
        st.divider()
        st.subheader("📋 Status Pembayaran Bulan Ini")

        for idx, row in df_pengeluaran.iterrows():
            nama = row.get("Nama", "-")
            nominal = to_float(row.get("Nominal", 0))
            periode = str(row.get("Periode", "SEBULAN")).strip().upper()
            bulan_bayar = str(row.get("Bulan_Bayar", "-")).strip()
            counter = int(to_float(row.get("Counter_Bayar", 0)))

            if periode == "SEBULAN":
                sudah = bulan_bayar == bulan_ini
                status_text = "✅ SUDAH" if sudah else "❌ BELUM"
                bisa_bayar = not sudah
            else:
                if bulan_bayar != bulan_ini:
                    counter = 0
                status_text = f"📊 {counter}/{jml_minggu}"
                bisa_bayar = counter < jml_minggu

            with st.expander(f"{nama} — {rupiah(nominal)} ({periode}) — {status_text}", expanded=bisa_bayar):
                if bisa_bayar:
                    sumber = st.selectbox(
                        "Sumber Anggaran",
                        ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"],
                        key=f"sumber_{idx}"
                    )

                    if st.button(
                        f"✅ Bayar {nama} — {rupiah(nominal)}",
                        type="primary",
                        use_container_width=True,
                        key=f"bayar_{idx}"
                    ):
                        ls, lk, la, lsh = get_last_saldo(df_kas)
                        nk, na, nsh = lk, la, lsh

                        if sumber == "UANG KAS (DI TANGAN)":
                            nk -= nominal
                        elif sumber == "UANG DI ATM":
                            na -= nominal
                        else:
                            nsh -= nominal

                        total = nk + na + nsh
                        next_no = get_next_no(df_kas)

                        row_kas = {
                            "No": str(next_no),
                            "Tanggal": today_wita().strftime("%d/%m/%Y"),
                            "Keterangan": f"BAYAR: {nama}",
                            "Jenis_Transaksi": "KELUAR",
                            "Nominal": fmt_nominal(nominal),
                            "Sumber_Anggaran": sumber,
                            "Tujuan_Anggaran": "-",
                            "Sisa_Kas_Di_Tangan": fmt_nominal(nk),
                            "Sisa_ATM": fmt_nominal(na),
                            "Sisa_Shopee": fmt_nominal(nsh),
                            "Sisa_Kas_Seluruh": fmt_nominal(total),
                            "Catatan": f"PENGELUARAN TETAP: {nama}"
                        }

                        df_kas_baru = pd.concat([df_kas, pd.DataFrame([row_kas])], ignore_index=True)

                        # Update status bayar
                        df_pg_update = df_pg.copy()

                        real_idx = df_pg_update[
                            (df_pg_update["Jenis"] == "PENGELUARAN") &
                            (df_pg_update["Nama"] == nama)
                        ].index

                        if len(real_idx) > 0:
                            ri = real_idx[0]
                            df_pg_update.loc[ri, "Bulan_Bayar"] = bulan_ini

                            if periode == "SEBULAN":
                                df_pg_update.loc[ri, "Counter_Bayar"] = "1"
                            else:
                                new_counter = counter + 1
                                df_pg_update.loc[ri, "Counter_Bayar"] = str(new_counter)

                        save_kas = safe_update(conn, WS_KAS, df_kas_baru)
                        save_pg = safe_update(conn, WS_PENGATURAN, df_pg_update)

                        if save_kas and save_pg:
                            st.success(f"✅ {nama} berhasil dibayar!")
                            st.rerun()
                else:
                    st.success("✅ Sudah lunas untuk bulan ini!")

        st.divider()

        total_bulanan = hitung_pengeluaran_tetap_bulanan(df_pg)
        beban_sisa = hitung_beban_belum_bayar(df_pg)

        m1, m2 = st.columns(2)
        m1.metric("💳 Total Beban/Bulan", rupiah(total_bulanan))
        m2.metric("⏳ Sisa Belum Bayar", rupiah(beban_sisa))

    elif aktif_p:
        st.info("Belum ada pengeluaran tetap.")

    st.divider()
    st.subheader("➕ Tambah Pengeluaran Tetap")

    with st.form("form_pengeluaran", clear_on_submit=True):
        nama_p = st.text_input("Nama Pengeluaran").strip().upper()
        nominal_p = st.number_input("Nominal", min_value=0.0, value=0.0, step=1000.0, format="%.0f")
        if nominal_p > 0:
            st.caption(f"💰 {rupiah(nominal_p)}")

        periode_p = st.selectbox("Periode", ["SEBULAN", "SEMINGGU"])

        b1, b2 = st.columns(2)
        with b1:
            simpan_p = st.form_submit_button("💾 Simpan", type="primary", use_container_width=True)
        with b2:
            st.form_submit_button("🔄 Reset", use_container_width=True)

        if simpan_p:
            if not nama_p:
                st.error("❌ Nama wajib diisi.")
            elif nominal_p <= 0:
                st.error("❌ Nominal harus lebih dari 0.")
            else:
                row_p = {
                    "Jenis": "PENGELUARAN", "Nama": nama_p,
                    "Nominal": fmt_nominal(nominal_p), "Periode": periode_p,
                    "Status": "AKTIF", "Bulan_Bayar": "-", "Counter_Bayar": "0"
                }
                df_pg_baru = pd.concat([df_pg, pd.DataFrame([row_p])], ignore_index=True)
                if safe_update(conn, WS_PENGATURAN, df_pg_baru):
                    st.success(f"✅ '{nama_p}' berhasil ditambahkan!")
                    st.rerun()

    if not df_pengeluaran.empty:
        st.divider()
        st.subheader("🗑️ Hapus Pengeluaran")
        hapus_nama = st.selectbox("Pilih", df_pengeluaran["Nama"].tolist(), key="hapus_p")
        if st.button("🗑️ Hapus", key="btn_hapus_p", use_container_width=True):
            df_pg_baru = df_pg[~((df_pg["Jenis"] == "PENGELUARAN") & (df_pg["Nama"] == hapus_nama))].copy()
            if safe_update(conn, WS_PENGATURAN, df_pg_baru):
                st.success(f"✅ '{hapus_nama}' dihapus!")
                st.rerun()

# ==========================================
# TAB 3 — TABUNGAN
# ==========================================
with tab3:
    st.subheader("🏦 Target Tabungan")

    aktif_tab = st.toggle("Aktifkan Tabungan", value=True, key="toggle_tab")

    d_tabungan = get_pengaturan(df_pg, "TABUNGAN")
    tab_skg = to_float(d_tabungan.iloc[0]["Nominal"]) if not d_tabungan.empty else 0.0

    if tab_skg > 0 and aktif_tab:
        st.metric("🏦 Tabungan/Bulan", rupiah(tab_skg))
    elif aktif_tab:
        st.info("Tabungan belum diatur.")

    if aktif_tab:
        st.divider()
        with st.form("form_tabungan", clear_on_submit=True):
            nominal_tab = st.number_input(
                "Nominal Tabungan/Bulan",
                min_value=0.0,
                value=float(tab_skg) if tab_skg > 0 else 0.0,
                step=50000.0, format="%.0f"
            )
            if nominal_tab > 0:
                st.caption(f"💰 {rupiah(nominal_tab)}")

            if st.form_submit_button("💾 Simpan", type="primary", use_container_width=True):
                if nominal_tab <= 0:
                    st.error("❌ Nominal harus lebih dari 0.")
                else:
                    df_pg_baru = df_pg[df_pg["Jenis"] != "TABUNGAN"].copy()
                    row = {"Jenis": "TABUNGAN", "Nama": "TARGET TABUNGAN",
                           "Nominal": fmt_nominal(nominal_tab), "Periode": "SEBULAN",
                           "Status": "AKTIF", "Bulan_Bayar": "-", "Counter_Bayar": "0"}
                    df_pg_baru = pd.concat([df_pg_baru, pd.DataFrame([row])], ignore_index=True)
                    if safe_update(conn, WS_PENGATURAN, df_pg_baru):
                        st.success("✅ Tabungan disimpan!")
                        st.rerun()

# ==========================================
# TAB 4 — TRANSFER
# ==========================================
with tab4:
    st.subheader("🔄 Transfer Antar Anggaran")
    st.info("Pindahkan uang antar saldo tanpa mengubah total.")

    ls, lk, la, lsh = get_last_saldo(df_kas)

    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("💵 Tangan", rupiah(lk))
    tc2.metric("🏧 ATM", rupiah(la))
    tc3.metric("🛒 Shopee", rupiah(lsh))

    st.divider()

    pilihan = ["UANG KAS (DI TANGAN)", "UANG DI ATM", "UANG DI SHOPEE"]

    tf1, tf2 = st.columns(2)
    with tf1:
        dari = st.selectbox("Dari", pilihan, key="tf_dari")
    with tf2:
        ke = st.selectbox("Ke", [x for x in pilihan if x != dari], key="tf_ke")

    nominal_tf = st.number_input("Nominal", min_value=0.0, value=0.0, step=1000.0, format="%.0f", key="tf_nom")
    if nominal_tf > 0:
        st.caption(f"💰 {rupiah(nominal_tf)}")

    if st.button("🔄 Transfer", type="primary", use_container_width=True, key="btn_tf"):
        if nominal_tf <= 0:
            st.error("❌ Nominal harus lebih dari 0.")
        else:
            nk, na, nsh = lk, la, lsh

            if dari == "UANG KAS (DI TANGAN)": nk -= nominal_tf
            elif dari == "UANG DI ATM": na -= nominal_tf
            else: nsh -= nominal_tf

            if ke == "UANG KAS (DI TANGAN)": nk += nominal_tf
            elif ke == "UANG DI ATM": na += nominal_tf
            else: nsh += nominal_tf

            total = nk + na + nsh
            next_no = get_next_no(df_kas)

            row = {
                "No": str(next_no), "Tanggal": today_wita().strftime("%d/%m/%Y"),
                "Keterangan": f"TRANSFER: {dari} ke {ke}", "Jenis_Transaksi": "TRANSFER",
                "Nominal": fmt_nominal(nominal_tf), "Sumber_Anggaran": dari, "Tujuan_Anggaran": ke,
                "Sisa_Kas_Di_Tangan": fmt_nominal(nk), "Sisa_ATM": fmt_nominal(na),
                "Sisa_Shopee": fmt_nominal(nsh), "Sisa_Kas_Seluruh": fmt_nominal(total),
                "Catatan": "TRANSFER"
            }

            df_kas_baru = pd.concat([df_kas, pd.DataFrame([row])], ignore_index=True)
            if safe_update(conn, WS_KAS, df_kas_baru):
                st.success(f"✅ Transfer {rupiah(nominal_tf)} berhasil!")
                st.rerun()

# ==========================================
# TAB 5 — RINGKASAN BULANAN
# ==========================================
with tab5:
    st.subheader("📊 Ringkasan Bulan Ini")

    gaji = get_gaji(df_pg)
    total_beban = hitung_pengeluaran_tetap_bulanan(df_pg)
    beban_sisa = hitung_beban_belum_bayar(df_pg)
    hasil_bersih = hitung_saldo_siap_pakai(df_kas, df_pg)
    batas_harian = hitung_batas_harian(df_kas, df_pg)

    d_tab = get_pengaturan(df_pg, "TABUNGAN")
    tabungan = to_float(d_tab.iloc[0]["Nominal"]) if not d_tab.empty else 0.0

    jumlah_hari = get_jumlah_hari_bulan_ini()
    sisa_hari = get_sisa_hari_bulan_ini()
    jml_minggu = get_jumlah_minggu_bulan_ini()

    ls, lk, la, lsh = get_last_saldo(df_kas)
    saldo_siap = ls - beban_sisa

    st.markdown(
        f"""
        <div style="text-align:center; padding:12px;
                    background:#13131a; border:1px solid #2a2a3a;
                    border-radius:12px; margin-bottom:16px;">
            <p style="font-family:'Poppins',sans-serif;
                      font-size:0.75rem; color:#8a8a9a; margin:0; text-align:center;">
                Bulan ini: <b style="color:#c4a35a;">{jumlah_hari} hari / {jml_minggu} minggu</b>
                &nbsp;|&nbsp;
                Sisa: <b style="color:#c4a35a;">{sisa_hari} hari</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    m1, m2 = st.columns(2)
    m1.metric("💼 Gaji", rupiah(gaji))
    m2.metric("💳 Total Beban/Bulan", rupiah(total_beban))

    m3, m4 = st.columns(2)
    m3.metric("🏦 Tabungan/Bulan", rupiah(tabungan))
    m4.metric("⏳ Beban Belum Bayar", rupiah(beban_sisa))

    st.divider()

    m5, m6 = st.columns(2)
    m5.metric("💰 Saldo Siap Pakai", rupiah(saldo_siap))
    m6.metric("🎯 Batas Harian", rupiah(batas_harian))

    st.divider()

    if hasil_bersih >= 0:
        st.success(f"✨ **Hasil Bersih: {rupiah(hasil_bersih)}**")
    else:
        st.error(f"❌ **Hasil Bersih: {rupiah(hasil_bersih)}** (DEFISIT)")

    if batas_harian > 0 and batas_harian < 50000:
        st.warning(f"⚠️ Batas harian tinggal **{rupiah(batas_harian)}**!")
    elif batas_harian <= 0:
        st.error("❌ Tidak ada budget harian tersisa!")

st.markdown(
    """
    <div style="text-align:center; padding:30px 0 10px 0;
                border-top:1px solid #1e1e2a; margin-top:20px;">
        <p style="font-family:'Poppins',sans-serif;
                  font-size:0.55rem; font-weight:400;
                  color:#3a3a4a; margin:0; text-align:center;">
            Keuangan Pribadi - Financial Tracker
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
