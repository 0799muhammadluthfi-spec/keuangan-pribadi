# ==========================================
# utils/helpers.py
# ==========================================
import streamlit as st
import pandas as pd
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
        txt = str(val).strip().replace(",", "").replace(".", "")
        if txt in ["", "-", "nan", "None", "null", "<NA>"]:
            return 0.0
        return float(txt)
    except:
        return 0.0

def to_float_rupiah(val) -> float:
    """Konversi string Rp ke float"""
    try:
        txt = str(val).strip()
        txt = txt.replace("Rp", "").replace(".", "").replace(",", "").strip()
        if txt in ["", "-", "nan", "None", "null"]:
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
    """Ambil jumlah hari di bulan ini"""
    import calendar
    hari_ini = today_wita()
    return calendar.monthrange(hari_ini.year, hari_ini.month)[1]

def get_sisa_hari_bulan_ini() -> int:
    """Ambil sisa hari 
