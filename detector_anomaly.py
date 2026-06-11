import re
import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

# ==============================================================================
# KAMUS HITAM (KEYWORDS BLACKLIST) UNTUK HAL MENCURIGAKAN
# ==============================================================================
KAMUS_JUDOL_SLOT = [
    "slot", "judol", "gacor", "jp paus", "maxwin", "situs judi", "bandar togel", 
    "taruhan bola", "rtp live", "deposit pulsa", "pragmatic", "zeus x500", 
    "sensasional", "link alternatif slot", "agen toto", "casino online"
]

KAMUS_DEFACE_HACK = [
    "hacked by", "defaced by", "indonesian hacker", "pwned", "rootkit", 
    "security team", "vuln terinfeksi"
]

def ekstrak_url_dari_baris(teks_baris):
    """Mengekstraksi URL http/https dari teks mentah"""
    pattern_url = r'https?://[^\s,\"\'>]+'
    urls = re.findall(pattern_url, teks_baris)
    return list(set([url.rstrip('/') for url in urls]))

def inisialisasi_browser():
    """Mengatur Firefox Headless dengan Path Eksplisit untuk Parrot OS"""
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Berjalan senyap di latar belakang
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    
    # Path biner Firefox ESR bawaan sistem Parrot OS
    firefox_options.binary_location = "/usr/bin/firefox-esr"
    
    # Menyamar sebagai browser Windows biasa agar tidak dicurigai sebagai bot
    firefox_options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0")
    
    # Menunjuk langsung ke letak geckodriver yang sudah dipasang manual
    service_gecko = Service(executable_path="/usr/local/bin/geckodriver")
    
    driver = webdriver.Firefox(options=firefox_options, service=service_gecko)
    driver.set_page_load_timeout(15)  # Batas waktu tunggu memuat halaman (15 detik)
    return driver

def audit_akses_dan_konten(driver, url):
    if not url:
        return {"status": "TIDAK_AKTIF", "pesan": "URL Kosong/Tidak Tersedia", "temuan": []}
    
    temuan_mencurigakan = []
    
    # Jeda acak natural manusiawi (2-4 detik)
    time.sleep(random.uniform(2.0, 4.0))
    
    parsed_url = urlparse(url)
    waktu_mulai = time.time()
    
    try:
        # ----------------------------------------------------------------------
        # 1. PENGUJIAN AKSES (BISA DIBUKA ATAU TIDAK)
        # ----------------------------------------------------------------------
        driver.get(url)
        waktu_respon = time.time() - waktu_mulai
        
        # ----------------------------------------------------------------------
        # 2. ANALISIS HAL MENCURIGAKAN DI DALAM LINK
        # ----------------------------------------------------------------------
        
        # A. Pengalihan Rute Mencurigakan (Malicious Redirect)
        url_akhir = driver.current_url
        domain_asal = parsed_url.netloc
        domain_akhir = urlparse(url_akhir).netloc
        
        if domain_asal != domain_akhir and "unp.ac.id" not in domain_akhir:
            temuan_mencurigakan.append(f"🪝 HIJACK REDIRECT: Link dialihkan keluar dari jaringan UNP ke -> {domain_akhir}")
        
        # Ambil seluruh teks bersih yang terlihat di halaman web
        konten_teks = driver.find_element(By.TAG_NAME, "html").text.lower().strip()
        panjang_teks = len(konten_teks)
        
        # B. Deteksi Penyusupan Judi Online / Slot
        kata_judi_terdeteksi = [kata for kata in KAMUS_JUDOL_SLOT if kata in konten_teks]
        if kata_judi_terdeteksi:
            temuan_mencurigakan.append(f"🎰 INJEKSI JUDI ONLINE: Terdeteksi kata kunci judi/slot {list(set(kata_judi_terdeteksi))}")
            
        # C. Deteksi Tanda Deface / Peretasan Halaman
        kata_hack_terdeteksi = [kata for kata in KAMUS_DEFACE_HACK if kata in konten_teks]
        if kata_hack_terdeteksi:
            temuan_mencurigakan.append(f"🚨 INDIKASI DEFACE: Terdeteksi klaim peretasan {list(set(kata_hack_terdeteksi))}")
            
        # D. Deteksi Halaman Kosong (Database OJS Mati/Gagal Sinkronisasi)
        if panjang_teks < 150:
            # Jika web sukses dibuka tapi hampir tidak ada teks sama sekali
            if "forbidden" not in konten_teks and "not found" not in konten_teks:
                减temuan_mencurigakan.append("🕳️ HALAMAN KOSONG: Link bisa dibuka tetapi isi web blank/kosong")

        # Evaluasi Akhir Hasil Temuan
        if temuan_mencurigakan:
            return {"status": "MENCURIGAKAN", "pesan": "Link Bisa Dibuka (Ada Temuan)", "temuan": temuan_mencurigakan}
        return {"status": "AMAN", "pesan": "Link Bisa Dibuka & Konten Normal", "temuan": []}

    except Exception as e:
        # Menangkap kegagalan jika link tidak bisa dibuka sama sekali
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            return {"status": "GAGAL_BUKA", "pesan": "❌ LINK TIDAK BISA DIBUKA (Request Timeout / RTO 15 Detik)", "temuan": []}
        elif "403" in error_msg or "forbidden" in error_msg:
            return {"status": "GAGAL_BUKA", "pesan": "❌ LINK TIDAK BISA DIBUKA (403 Forbidden / Diblokir Server)", "temuan": []}
        else:
            return {"status": "GAGAL_BUKA", "pesan": "❌ LINK TIDAK BISA DIBUKA (Server Down / Kendala DNS)", "temuan": []}

def main():
    file_input = "daftar_jurnal.txt"
    
    print("=" * 95)
    print("   AUDITOR WEB JURNAL: FOKUS AKSESIBILITAS & DETEKSI HAL MENCURIGAKAN (SELENIUM DRIVER)   ")
    print("=" * 95)
    
    try:
        with open(file_input, "r", encoding="utf-8") as f:
            baris_data = f.readlines()
    except FileNotFoundError:
        print(f"[!] Error: File '{file_input}' tidak ditemukan di folder ini.")
        return

    print("[*] Membuka Firefox Engine di latar belakang...")
    try:
        driver = inisialisasi_browser()
        print("[+] Engine aktif. Memulai pemindaian...\n")
    except Exception as e:
        print(f"[!] Gagal memuat driver browser: {e}")
        return

    total_entri = 0
    total_mencurigakan = 0
    total_gagal_buka = 0
    
    try:
        for baris in baris_data:
            if not baris.strip() or baris.strip().startswith("=>") or baris.strip().startswith("="):
                continue
                
            urls = ekstrak_url_dari_baris(baris)
            
            if urls:
                total_entri += 1
                print(f"\n[Analisis #{total_entri}] Memeriksa baris: \"{baris.strip()[:60]}...\"")
                
                for url in urls:
                    hasil = audit_akses_dan_konten(driver, url)
                    
                    if hasil["status"] == "AMAN":
                        print(f"   🟢 [{url}] -> {hasil['pesan']}")
                    elif hasil["status"] == "MENCURIGAKAN":
                        total_mencurigakan += 1
                        print(f"   🟡 [{url}] -> {hasil['pesan']}")
                        for temuan in hasil["temuan"]:
                            print(f"      └─ {temuan}")
                    else:
                        total_gagal_buka += 1
                        print(f"   🔴 [{url}] -> {hasil['pesan']}")
                            
    finally:
        print("\n[*] Mematikan engine browser...")
        driver.quit()
                        
    print("=" * 95)
    print(f" PEMINDAIAN SELESAI | Total Link Diperiksa: {total_entri}")
    print(f" -> Link Aman: {total_entri - total_mencurigakan - total_gagal_buka} | Mencurigakan: {total_mencurigakan} | Gagal Dibuka: {total_gagal_buka}")
    print("=" * 95)

if __name__ == "__main__":
    main()