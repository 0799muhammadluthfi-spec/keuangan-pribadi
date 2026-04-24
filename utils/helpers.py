import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
from zoneinfo import ZoneInfo

def now_wita():
    return datetime.now(ZoneInfo("Asia/Makassar"))

def today_wita():
    return now_wita().date()

WS_KAS = "DATA_KAS"
WS_PENGATURAN = "PENGATURAN"
WS_PENGECEKAN = "PENGECEKAN"

KOLOM_KAS = [
    "No", "Tanggal", "Keterangan",
    "Jenis_Transaksi", "Nominal",
    "Sumber_Anggaran", "Tujuan_Anggaran",
    "Sisa_Kas_Di_Tangan", "Sisa_ATM",
    "Sisa_Shopee", "Sisa_Kas_Seluruh",
    "Catatan"
]

KOLOM_PENGATURAN = [
    "Jenis", "Nama", "Nominal",
    "Periode", "Status",
    "Bulan_Bayar", "Counter_Bayar"
]

KOLOM_PENGECEKAN = [
    "No", "Tanggal",
    "Kas_Fisik", "Kas_Sistem",
    "Selisih", "Status_Aktif"
]

def to_float(val):
    try:
        txt = str(val).strip().replace(",", "")
        if txt in ["", "-", "nan", "None", "null", "<NA>"]:
            return 0.0
        return float(txt)
    except:
        return 0.0

def fmt_nominal(val):
    try:
        num = float(val)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}".rstrip("0").rstrip(".")
    except:
        return "0"

def rupiah(val):
    try:
        num = int(round(float(val)))
        if num < 0:
            return f"-Rp {abs(num):,}".replace(",", ".")
        return f"Rp {num:,}".replace(",", ".")
    except:
        return "Rp 0"

def format_tgl_indo(tgl_str):
    if not tgl_str or str(tgl_str).strip() in ["-", "nan", "", "None"]:
        return ""
    try:
        tgl_bersih = str(tgl_str).strip().replace("/", "-")
        if len(tgl_bersih.split("-")[-1]) == 2:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%y")
        else:
            dt = datetime.strptime(tgl_bersih, "%d-%m-%Y")
        hari = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"][dt.weekday()]
        bulan = ["Januari","Februari","Maret","April","Mei","Juni",
                 "Juli","Agustus","September","Oktober","November","Desember"][dt.month-1]
        return f"{hari}, {dt.day} {bulan} {dt.year}"
    except:
        return str(tgl_str)

def get_jumlah_hari_bulan_ini():
    h = today_wita()
    return calendar.monthrange(h.year, h.month)[1]

def get_sisa_hari_bulan_ini():
    h = today_wita()
    total = calendar.monthrange(h.year, h.month)[1]
    return total - h.day + 1

def get_bulan_ini_str():
    h = today_wita()
    return f"{h.year}-{h.month:02d}"

def get_jumlah_minggu_bulan_ini():
    if get_jumlah_hari_bulan_ini() <= 28:
        return 4
    return 5

def get_empty_df(worksheet):
    if worksheet == WS_KAS:
        return pd.DataFrame(columns=KOLOM_KAS)
    if worksheet == WS_PENGATURAN:
        return pd.DataFrame(columns=KOLOM_PENGATURAN)
    if worksheet == WS_PENGECEKAN:
        return pd.DataFrame(columns=KOLOM_PENGECEKAN)
    return pd.DataFrame()

def pastikan_kolom(df, kolom_list):
    for col in kolom_list:
        if col not in df.columns:
            df[col] = "-"
    return df

def get_next_no(df, col="No"):
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except:
        return 1

def tampilkan_n_terakhir(df, n=30):
    try:
        if df.empty:
            return df
        d = df.copy()
        d["_s"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_s", ascending=False).drop(columns="_s")
        return d.head(n)
    except:
        return df

def load_data(conn_obj, worksheet):
    try:
        df = conn_obj.read(worksheet=worksheet, ttl=60)
        if df is None or df.empty:
            return get_empty_df(worksheet)
        df = df.astype(str).replace(r"\.0$", "", regex=True)
        for col in df.columns:
            df[col] = df[col].str.strip()
        df = df.replace(["nan", "None", "", "null", "NaN", "<NA>"], "-")
        if worksheet == WS_KAS:
            df = pastikan_kolom(df, KOLOM_KAS)
        elif worksheet == WS_PENGATURAN:
            df = pastikan_kolom(df, KOLOM_PENGATURAN)
        elif worksheet == WS_PENGECEKAN:
            df = pastikan_kolom(df, KOLOM_PENGECEKAN)
        return df
    except Exception as e:
        st.error(f"Gagal membaca ({worksheet}): {e}")
        return get_empty_df(worksheet)

def safe_update(conn_obj, worksheet, data):
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ({worksheet}): {e}")
        return False

def tombol_refresh(key_btn):
    if st.button("🔄", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()

def get_last_saldo(df_kas):
    try:
        if df_kas.empty:
            return 0.0, 0.0, 0.0, 0.0
        d = df_kas[df_kas["No"] != "-"].copy()
        if "Jenis_Transaksi" in d.columns:
            d = d[d["Jenis_Transaksi"] != "PENGECEKAN"]
        if d.empty:
            return 0.0, 0.0, 0.0, 0.0
        d["_s"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_s", ascending=True)
        last = d.iloc[-1]
        kas = to_float(last.get("Sisa_Kas_Di_Tangan", 0))
        atm = to_float(last.get("Sisa_ATM", 0))
        shopee = to_float(last.get("Sisa_Shopee", 0))
        return kas + atm + shopee, kas, atm, shopee
    except:
        return 0.0, 0.0, 0.0, 0.0

def hitung_ringkasan(df_kas):
    try:
        if df_kas.empty:
            return 0.0, 0.0
        d = df_kas[df_kas["No"] != "-"].copy()
        if "Jenis_Transaksi" not in d.columns:
            return 0.0, 0.0
        d = d[d["Jenis_Transaksi"].isin(["MASUK", "KELUAR"])]
        masuk = d[d["Jenis_Transaksi"] == "MASUK"]["Nominal"].apply(to_float).sum()
        keluar = d[d["Jenis_Transaksi"] == "KELUAR"]["Nominal"].apply(to_float).sum()
        return masuk, keluar
    except:
        return 0.0, 0.0

def hitung_pengeluaran_hari_ini(df_kas):
    try:
        if df_kas.empty:
            return 0.0
        d = df_kas[df_kas["No"] != "-"].copy()
        if "Jenis_Transaksi" not in d.columns:
            return 0.0
        hari_ini = today_wita().strftime("%d/%m/%Y")
        d["_tgl"] = d["Tanggal"].astype(str).str.strip().str.replace("-", "/", regex=False)
        d_h = d[(d["_tgl"] == hari_ini) & (d["Jenis_Transaksi"] == "KELUAR")]
        return d_h["Nominal"].apply(to_float).sum()
    except:
        return 0.0

def get_pengaturan(df_pg, jenis):
    try:
        if df_pg.empty:
            return pd.DataFrame()
        return df_pg[(df_pg["Jenis"] == jenis) & (df_pg["Status"] == "AKTIF")].copy()
    except:
        return pd.DataFrame()

def get_gaji(df_pg):
    try:
        d = df_pg[(df_pg["Jenis"] == "GAJI") & (df_pg["Status"] == "AKTIF")]
        if d.empty:
            return 0.0
        return to_float(d.iloc[0]["Nominal"])
    except:
        return 0.0

def get_tabungan(df_pg):
    try:
        d = get_pengaturan(df_pg, "TABUNGAN")
        if d.empty:
            return 0.0
        return to_float(d.iloc[0]["Nominal"])
    except:
        return 0.0

def hitung_pengeluaran_tetap_bulanan(df_pg):
    try:
        d = get_pengaturan(df_pg, "PENGELUARAN")
        if d.empty:
            return 0.0
        total = 0.0
        jm = get_jumlah_minggu_bulan_ini()
        for _, row in d.iterrows():
            nom = to_float(row.get("Nominal", 0))
            per = str(row.get("Periode", "SEBULAN")).strip().upper()
            if per == "SEMINGGU":
                total += nom * jm
            elif per == "SEBULAN":
                total += nom
        return total
    except:
        return 0.0

def hitung_beban_belum_bayar(df_pg):
    try:
        d = get_pengaturan(df_pg, "PENGELUARAN")
        if d.empty:
            return 0.0
        total = 0.0
        jm = get_jumlah_minggu_bulan_ini()
        bi = get_bulan_ini_str()
        for _, row in d.iterrows():
            nom = to_float(row.get("Nominal", 0))
            per = str(row.get("Periode", "SEBULAN")).strip().upper()
            bb = str(row.get("Bulan_Bayar", "-")).strip()
            cnt = int(to_float(row.get("Counter_Bayar", 0)))
            if per == "SEBULAN":
                if bb != bi:
                    total += nom
            elif per == "SEMINGGU":
                if bb != bi:
                    cnt = 0
                sisa = jm - cnt
                if sisa > 0:
                    total += nom * sisa
        return total
    except:
        return 0.0

def hitung_pengeluaran_harian(df_pg):
    try:
        tb = hitung_pengeluaran_tetap_bulanan(df_pg)
        jh = get_jumlah_hari_bulan_ini()
        return tb / jh if jh > 0 else 0.0
    except:
        return 0.0

def hitung_hasil_bersih_bulanan(df_pg):
    try:
        return get_gaji(df_pg) - hitung_pengeluaran_tetap_bulanan(df_pg) - get_tabungan(df_pg)
    except:
        return 0.0

def hitung_saldo_siap_pakai(df_kas, df_pg):
    try:
        ls, _, _, _ = get_last_saldo(df_kas)
        return ls - hitung_beban_belum_bayar(df_pg) - get_tabungan(df_pg)
    except:
        return 0.0

def hitung_batas_harian(df_kas, df_pg):
    try:
        ss = hitung_saldo_siap_pakai(df_kas, df_pg)
        sh = get_sisa_hari_bulan_ini()
        if sh > 0 and ss > 0:
            return ss / sh
        return 0.0
    except:
        return 0.0

def get_selisih_aktif(df_cek):
    try:
        if df_cek.empty:
            return False, 0.0, "-"
        d = df_cek[df_cek["No"] != "-"].copy()
        if d.empty:
            return False, 0.0, "-"
        d["_s"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_s", ascending=True)
        last = d.iloc[-1]
        status = str(last.get("Status_Aktif", "TIDAK")).strip().upper()
        selisih = to_float(last.get("Selisih", 0))
        tgl = str(last.get("Tanggal", "-")).strip()
        if status == "YA" and abs(selisih) > 0.5:
            return True, selisih, tgl
        return False, 0.0, "-"
    except:
        return False, 0.0, "-"
