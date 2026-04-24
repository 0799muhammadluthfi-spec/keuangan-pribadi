# ==========================================
# utils/helpers.py
# ==========================================
import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from zoneinfo import ZoneInfo

# ==========================================
# TIMEZONE
# ==========================================
def now_wita():
    return datetime.now(ZoneInfo("Asia/Makassar"))

def today_wita():
    return now_wita().date()

# ==========================================
# NAMA WORKSHEET
# ==========================================
WS_KAS        = "DATA_KAS"
WS_PENGATURAN = "PENGATURAN"
WS_PENGECEKAN = "PENGECEKAN"

# ==========================================
# KOLOM STANDAR
# ==========================================
KOLOM_KAS = [
    "No",
    "Tanggal",
    "Keterangan",
    "Jenis_Transaksi",
    "Nominal",
    "Sumber_Anggaran",
    "Tujuan_Anggaran",
    "Sisa_Kas_Di_Tangan",
    "Sisa_ATM",
    "Sisa_Shopee",
    "Sisa_Kas_Seluruh",
    "Catatan"
]

KOLOM_PENGATURAN = [
    "Jenis",
    "Nama",
    "Nominal",
    "Periode",
    "Status"
]

KOLOM_PENGECEKAN = [
    "No",
    "Tanggal",
    "Kas_Fisik",
    "Kas_Sistem",
    "Selisih",
    "Status_Aktif"
]

# ==========================================
# FUNGSI FORMAT & KONVERSI
# ==========================================
def to_float(val) -> float:
    try:
        txt = str(val).strip().replace(",", "")
        if txt in ["", "-", "nan", "None", "null", "<NA>"]:
            return 0.0
        return float(txt)
    except:
        return 0.0

def fmt_nominal(val) -> str:
    try:
        num = float(val)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}".rstrip("0").rstrip(".")
    except:
        return "0"

def rupiah(val) -> str:
    try:
        num = int(round(float(val)))
        if num < 0:
            return f"-Rp {abs(num):,}".replace(",", ".")
        return f"Rp {num:,}".replace(",", ".")
    except:
        return "Rp 0"

def format_tgl_indo(tgl_str) -> str:
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

def get_jumlah_hari_bulan_ini() -> int:
    hari_ini = today_wita()
    return calendar.monthrange(hari_ini.year, hari_ini.month)[1]

def get_sisa_hari_bulan_ini() -> int:
    hari_ini = today_wita()
    total = calendar.monthrange(hari_ini.year, hari_ini.month)[1]
    return total - hari_ini.day + 1

# ==========================================
# FUNGSI DATAFRAME
# ==========================================
def get_empty_df(worksheet: str) -> pd.DataFrame:
    if worksheet == WS_KAS:
        return pd.DataFrame(columns=KOLOM_KAS)
    if worksheet == WS_PENGATURAN:
        return pd.DataFrame(columns=KOLOM_PENGATURAN)
    if worksheet == WS_PENGECEKAN:
        return pd.DataFrame(columns=KOLOM_PENGECEKAN)
    return pd.DataFrame()

def pastikan_kolom(df: pd.DataFrame, kolom_list: list) -> pd.DataFrame:
    for col in kolom_list:
        if col not in df.columns:
            df[col] = "-"
    return df

def get_next_no(df: pd.DataFrame, col: str = "No") -> int:
    try:
        if df.empty or col not in df.columns:
            return 1
        nums = pd.to_numeric(df[col], errors="coerce").dropna()
        return int(nums.max()) + 1 if not nums.empty else 1
    except:
        return 1

def tampilkan_n_terakhir(df: pd.DataFrame, n: int = 30) -> pd.DataFrame:
    try:
        if df.empty:
            return df
        d = df.copy()
        d["_sort"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_sort", ascending=False).drop(columns="_sort")
        return d.head(n)
    except:
        return df

# ==========================================
# FUNGSI LOAD & SAVE
# ==========================================
def load_data(conn_obj, worksheet: str) -> pd.DataFrame:
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
        st.error(f"Gagal membaca data ({worksheet}): {e}")
        return get_empty_df(worksheet)

def safe_update(conn_obj, worksheet: str, data: pd.DataFrame) -> bool:
    try:
        conn_obj.update(worksheet=worksheet, data=data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan ({worksheet}): {e}")
        return False

def tombol_refresh(key_btn: str):
    if st.button("🔄", key=key_btn, use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# FUNGSI SALDO KAS
# ==========================================
def get_last_saldo(df_kas: pd.DataFrame):
    try:
        if df_kas.empty:
            return 0.0, 0.0, 0.0, 0.0

        d = df_kas[df_kas["No"] != "-"].copy()

        # Abaikan record pengecekan
        if "Jenis_Transaksi" in d.columns:
            d = d[d["Jenis_Transaksi"] != "PENGECEKAN"]

        if d.empty:
            return 0.0, 0.0, 0.0, 0.0

        d["_sort"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_sort", ascending=True)
        last = d.iloc[-1]

        kas     = to_float(last.get("Sisa_Kas_Di_Tangan", 0))
        atm     = to_float(last.get("Sisa_ATM", 0))
        shopee  = to_float(last.get("Sisa_Shopee", 0))
        seluruh = kas + atm + shopee

        return seluruh, kas, atm, shopee
    except:
        return 0.0, 0.0, 0.0, 0.0

def hitung_ringkasan(df_kas: pd.DataFrame):
    try:
        if df_kas.empty:
            return 0.0, 0.0

        d = df_kas[df_kas["No"] != "-"].copy()

        if "Jenis_Transaksi" not in d.columns:
            return 0.0, 0.0

        d = d[d["Jenis_Transaksi"].isin(["MASUK", "KELUAR"])]

        total_masuk  = d[d["Jenis_Transaksi"] == "MASUK"]["Nominal"].apply(to_float).sum()
        total_keluar = d[d["Jenis_Transaksi"] == "KELUAR"]["Nominal"].apply(to_float).sum()

        return total_masuk, total_keluar
    except:
        return 0.0, 0.0

# ==========================================
# FUNGSI PENGATURAN
# ==========================================
def get_pengaturan(df_pg: pd.DataFrame, jenis: str):
    try:
        if df_pg.empty:
            return pd.DataFrame()

        result = df_pg[
            (df_pg["Jenis"] == jenis) &
            (df_pg["Status"] == "AKTIF")
        ].copy()

        return result
    except:
        return pd.DataFrame()

def get_gaji(df_pg: pd.DataFrame) -> float:
    try:
        d = df_pg[
            (df_pg["Jenis"] == "GAJI") &
            (df_pg["Status"] == "AKTIF")
        ]
        if d.empty:
            return 0.0
        return to_float(d.iloc[0]["Nominal"])
    except:
        return 0.0

def hitung_pengeluaran_tetap_bulanan(df_pg: pd.DataFrame) -> float:
    try:
        d = get_pengaturan(df_pg, "PENGELUARAN")
        if d.empty:
            return 0.0

        total = 0.0
        jumlah_hari = get_jumlah_hari_bulan_ini()

        for _, row in d.iterrows():
            nominal = to_float(row.get("Nominal", 0))
            periode = str(row.get("Periode", "BULANAN")).strip().upper()

            if periode == "HARIAN":
                total += nominal * jumlah_hari
            elif periode == "MINGGUAN":
                total += nominal * 4
            elif periode == "BULANAN":
                total += nominal

        return total
    except:
        return 0.0

def hitung_pengeluaran_harian(df_pg: pd.DataFrame) -> float:
    try:
        d = get_pengaturan(df_pg, "PENGELUARAN")
        if d.empty:
            return 0.0

        total = 0.0
        jumlah_hari = get_jumlah_hari_bulan_ini()

        for _, row in d.iterrows():
            nominal = to_float(row.get("Nominal", 0))
            periode = str(row.get("Periode", "BULANAN")).strip().upper()

            if periode == "HARIAN":
                total += nominal
            elif periode == "MINGGUAN":
                total += nominal / 7
            elif periode == "BULANAN":
                total += nominal / jumlah_hari

        return total
    except:
        return 0.0

def hitung_hasil_bersih_bulanan(df_pg: pd.DataFrame) -> float:
    try:
        gaji        = get_gaji(df_pg)
        pengeluaran = hitung_pengeluaran_tetap_bulanan(df_pg)

        d_tabungan = get_pengaturan(df_pg, "TABUNGAN")
        tabungan = 0.0
        if not d_tabungan.empty:
            tabungan = to_float(d_tabungan.iloc[0]["Nominal"])

        return gaji - pengeluaran - tabungan
    except:
        return 0.0

# ==========================================
# FUNGSI PENGECEKAN SELISIH
# ==========================================
def get_selisih_aktif(df_cek: pd.DataFrame):
    try:
        if df_cek.empty:
            return False, 0.0, "-"

        d = df_cek[df_cek["No"] != "-"].copy()
        if d.empty:
            return False, 0.0, "-"

        d["_sort"] = pd.to_numeric(d["No"], errors="coerce")
        d = d.sort_values("_sort", ascending=True)
        last = d.iloc[-1]

        status  = str(last.get("Status_Aktif", "TIDAK")).strip().upper()
        selisih = to_float(last.get("Selisih", 0))
        tgl     = str(last.get("Tanggal", "-")).strip()

        if status == "YA" and abs(selisih) > 0.5:
            return True, selisih, tgl
        return False, 0.0, "-"
    except:
        return False, 0.0, "-"

# ==========================================
# FUNGSI WARNING BATAS HARIAN
# ==========================================
def cek_warning_harian(df_kas: pd.DataFrame, df_pg: pd.DataFrame):
    try:
        _, kas, _, _ = get_last_saldo(df_kas)
        pengeluaran_harian = hitung_pengeluaran_harian(df_pg)
        sisa_hari = get_sisa_hari_bulan_ini()

        if pengeluaran_harian <= 0:
            return "aman", ""

        kebutuhan_sisa_bulan = pengeluaran_harian * sisa_hari
        batas_harian = kas / sisa_hari if sisa_hari > 0 else 0

        if kas <= 0:
            return "bahaya", f"❌ Kas di tangan MINUS! Saldo tidak mencukupi."
        elif kas < pengeluaran_harian:
            return "bahaya", (
                f"❌ Kas di tangan ({rupiah(kas)}) tidak cukup untuk "
                f"pengeluaran hari ini ({rupiah(pengeluaran_harian)})!"
            )
        elif kas < kebutuhan_sisa_bulan:
            return "warning", (
                f"⚠️ Kas di tangan ({rupiah(kas)}) mungkin tidak cukup "
                f"untuk sisa bulan ini ({sisa_hari} hari). "
                f"Batas harian saat ini: {rupiah(batas_harian)}"
            )
        else:
            return "aman", ""
    except:
        return "aman", ""
