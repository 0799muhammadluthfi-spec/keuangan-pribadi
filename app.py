# ── BATAS HARIAN ──
aktif_batas = st.toggle("📅 Aktifkan Batas Harian", value=False, key="toggle_batas_home")

if aktif_batas:
    from utils.helpers import hitung_batas_harian, hitung_beban_belum_bayar

    batas = hitung_batas_harian(df_kas, df_pg)
    beban_sisa = hitung_beban_belum_bayar(df_pg)
    sisa_hari = get_sisa_hari_bulan_ini()
    saldo_siap = last_seluruh - beban_sisa

    m1, m2 = st.columns(2)
    m1.metric("💰 Saldo Siap Pakai", rupiah(saldo_siap))
    m2.metric("🎯 Batas Harian", rupiah(batas))

    st.caption(
        f"Total saldo ({rupiah(last_seluruh)}) - beban belum bayar ({rupiah(beban_sisa)}) "
        f"= {rupiah(saldo_siap)} dibagi sisa {sisa_hari} hari"
    )

    if batas <= 0:
        st.error("❌ Tidak ada budget harian tersisa!")
    elif batas < 50000:
        st.warning(f"⚠️ Batas harian tinggal **{rupiah(batas)}**")
