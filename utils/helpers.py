# ==========================================
# utils/helpers.py
# ==========================================
import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
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
WS_KAS = "DATA_KAS"
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
# FORMAT & KONVERSI
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
# DATAFRAME
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
# LOAD & SAVE
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
        conn_obj.update(worksheet=worksheet, 
