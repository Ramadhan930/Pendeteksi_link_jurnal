import re
import requests
from bs4 import BeautifulSoup
import urllib3

# Matikan warning SSL ceritificate error
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ekstrak_url_dari_baris(teks_baris):
    """Mencari semua tautan http/https dalam satu baris teks menggunakan Regex"""
    pattern_url = r'https?://[^\s,\"\'>]+'
    urls = re.findall(pattern_url, teks_baris)
    # Bersihkan jika ada karakter sisa di ujung URL (seperti garing atau titik dua)
    cleaned_urls = [url.rstrip('/') for url in urls]
    return list(set(cleaned_urls)) # Mengeliminasi duplikasi dalam satu baris

def cek_kondisi_web(url):
    """Memeriksa respon HTTP dan mendeteksi jika halaman web kosong"""
    if not url:
        return "TIDAK_AKTIF", "URL Kosong"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        response = requests.get(url, timeout=7, verify=False, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            konten_teks = soup.get_text().strip()
            
            # Jika teks yang terdeteksi di halaman web kurang dari 150 karakter
            if len(konten_teks) < 150:
                return "KOSONG", "Web Aktif tapi Konten Kosong/Blank"
            return "AMAN", "Tampilan Normal / OK"
        else:
            return "ERROR", f"HTTP Status {response.status_code}"
    except requests.exceptions.RequestException:
        return "ERROR", "Server Down / Tidak Dapat Diakses"

def main():
    file_input = "daftar_jurnal.txt"
    
    print("=" * 70)
    print("    MEMULAI PENGECEKAN MASAL OTOMATIS (SISTEM PARROT OS)    ")
    print("=" * 70)
    
    try:
        with open(file_input, "r", encoding="utf-8") as f:
            baris_data = f.readlines()
    except FileNotFoundError:
        print(f"[!] Error: File '{file_input}' tidak ditemukan di folder ini.")
        return

    total_diperiksa = 0
    
    for indeks, baris in enumerate(baris_data, 1):
        # Abaikan baris kosong atau baris komentar bawaan catatan Anda
        if not baris.strip() or baris.strip().startswith("=>") or baris.strip().startswith("="):
            continue
            
        urls = ekstrak_url_dari_baris(baris)
        
        # Jika dalam baris tersebut terdeteksi ada URL, lakukan pengecekan
        if urls:
            total_diperiksa += 1
            print(f"\n[Data #{total_diperiksa}] Memproses baris teks: {baris.strip()[:60]}...")
            
            # Jika baris memiliki 2 URL berbeda (Dual Link)
            if len(urls) >= 2:
                url_1, url_2 = urls[0], urls[1]
                status1, ket1 = cek_kondisi_web(url_1)
                status2, ket2 = cek_kondisi_web(url_2)
                
                print(f"  -> Link 1 [{url_1}]: {status1} ({ket1})")
                print(f"  -> Link 2 [{url_2}]: {status2} ({ket2})")
                
                # Kesimpulan Logika Kelompok
                if status1 == "AMAN" and status2 == "AMAN":
                    print("  [KESIMPULAN] => KATEGORI 1: AMAN (Tampilan Normal)")
                elif status1 == "AMAN" or status2 == "AMAN":
                    print("  [KESIMPULAN] => KATEGORI 2: BERMASALAH PARUH (Salah satu link bisa)")
                elif status1 == "KOSONG" or status2 == "KOSONG":
                    print("  [KESIMPULAN] => KATEGORI 3: KONTEN KOSONG / GAGAL MIGRASI")
                else:
                    print("  [KESIMPULAN] => KATEGORI 4: ERROR / DOWN TOTAL")
                    
            # Jika baris hanya memiliki 1 URL
            else:
                url_tunggal = urls[0]
                status, ket = cek_kondisi_web(url_tunggal)
                print(f"  -> Link Tunggal [{url_tunggal}]: {status} ({ket})")
                
                if status == "AMAN":
                    print("  [KESIMPULAN] => KATEGORI 1: AMAN (Tampilan Normal)")
                elif status == "KOSONG":
                    print("  [KESIMPULAN] => KATEGORI 3: KONTEN KOSONG")
                else:
                    print("  [KESIMPULAN] => KATEGORI 4: ERROR / DOWN")
                    
    print("\n" + "=" * 70)
    print(f" PENGECEKAN SELESAI. Total {total_diperiksa} entri jurnal telah diperiksa. ")
    print("=" * 70)

if __name__ == "__main__":
    main()