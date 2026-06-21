#!/usr/bin/env python3
"""
SCRAPER PPJ UNP - Versi Selenium (untuk halaman JavaScript)
Output: daftar_jurnal.txt
"""

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

BASE_URL = "https://ppj.unp.ac.id/"
OUTPUT_FILE = "daftar_jurnal.txt"
TOTAL_HALAMAN = 14

semua_link = set()

print("=" * 50)
print("  SCRAPER PPJ UNP - SELENIUM")
print("=" * 50)

# Setup Firefox headless
print("\n[*] Menyalakan browser...")
options = Options()
options.add_argument("--headless")  # Jalan di background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options
)

try:
    driver.get(BASE_URL)
    time.sleep(3)  # Tunggu JavaScript render
    
    for halaman in range(1, TOTAL_HALAMAN + 1):
        print(f"\n[*] Halaman {halaman}/{TOTAL_HALAMAN}")
        
        # Ambil semua link
        links = driver.find_elements(By.TAG_NAME, "a")
        jumlah = 0
        
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and any(kata in href.lower() for kata in ["journal", "jurnal", "ojs", "index.php", "ejournal"]):
                    if href not in semua_link:
                        semua_link.add(href)
                        jumlah += 1
            except:
                pass
        
        print(f"    [✓] {jumlah} link baru. Total: {len(semua_link)}")
        
        # Cari tombol Next
        if halaman < TOTAL_HALAMAN:
            try:
                # Coba berbagai selector untuk tombol next
                next_btn = None
                
                # Cari link dengan teks "›" atau "»" atau "Next"
                for a in driver.find_elements(By.TAG_NAME, "a"):
                    teks = a.text.strip()
                    if teks in ["›", "»", "Next", "next", "Berikutnya"]:
                        next_btn = a
                        break
                
                # Kalau tidak ketemu, coba cari pagination
                if not next_btn:
                    pagination = driver.find_elements(By.CSS_SELECTOR, ".pagination a, .pager a, nav a")
                    for p in pagination:
                        teks = p.text.strip()
                        if teks.isdigit() and int(teks) == halaman + 1:
                            next_btn = p
                            break
                
                if next_btn:
                    print(f"    ➡️ Klik Next...")
                    next_btn.click()
                    time.sleep(3)  # Tunggu load
                else:
                    print(f"    [!] Tombol Next tidak ditemukan. Berhenti.")
                    break
                    
            except Exception as e:
                print(f"    [!] Gagal klik Next: {e}")
                break

finally:
    driver.quit()

# Simpan hasil
daftar_akhir = sorted(list(semua_link))
with open(OUTPUT_FILE, "w") as f:
    for url in daftar_akhir:
        f.write(url + "\n")

print(f"\n{'='*50}")
print(f"  SELESAI! Total: {len(daftar_akhir)} jurnal")
print(f"  Disimpan ke: {OUTPUT_FILE}")
print(f"{'='*50}")

# Tampilkan 5 sample
print("\n[*] 5 Sample:")
for url in daftar_akhir[:5]:
    print(f"    {url}")