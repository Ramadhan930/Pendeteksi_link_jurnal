"""
╔══════════════════════════════════════════════╗
║   UNP JOURNAL DEFENSE SYSTEM v4              ║
║   Scanner 3-Layer + Hidden Link Detection    ║
║   + Telegram Notification + Bukti Otomatis   ║
║   L1:Custom (Judol/Deface/Redirect/Hidden)   ║
║   L2:WhatWeb (Versi & Teknologi)             ║
║   L3:VirusTotal (Reputasi Domain)            ║
╚══════════════════════════════════════════════╝
"""

import os
import csv
import time
import subprocess
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from colorama import init, Fore, Style

# ===================== INIT =====================
init(autoreset=True)
load_dotenv()

# Konfigurasi dari .env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

# File & Folder
FILE_INPUT = "daftar_jurnal.txt"
FOLDER_LOG = "logs"
FOLDER_BUKTI = "bukti"

# Kamus Judol (diperluas berdasarkan temuan)
KAMUS_JUDOL = [
    "slot", "judol", "gacor", "jp paus", "maxwin", "situs judi",
    "bandar togel", "taruhan bola", "rtp live", "deposit pulsa",
    "pragmatic", "zeus x500", "sensasional", "link alternatif slot",
    "agen toto", "casino online", "togel online", "situs slot",
    "judi online", "slot online", "slot gacor", "depo pulsa",
    "toto slot", "sabung ayam", "poker online", "slot demo",
    "slot88", "bola88", "togel", "4d", "toto", "maxwin",
    "situs toto", "situs togel", "bandar slot", "agen slot",
    "demo slot", "slot maxwin", "slot hoki", "gacor hari ini"
]

KAMUS_DEFACE = [
    "hacked by", "defaced by", "indonesian hacker", "pwned",
    "rootkit", "security team", "vuln terinfeksi", "your site has been hacked",
    "just hacked", "hacked by mr", "cyber team"
]

# ===================== TELEGRAM =====================

def kirim_telegram(pesan):
    """Kirim alert ke Telegram"""
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(Fore.YELLOW + "  [i] Telegram belum dikonfigurasi")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": pesan,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=payload, timeout=10)
        result = response.json()
        
        if response.status_code == 200 and result.get("ok"):
            print(Fore.GREEN + "  [✓] Telegram BERHASIL!")
            return True
        else:
            error_msg = result.get('description', 'Unknown error')
            print(Fore.RED + f"  [✗] Telegram GAGAL: {error_msg}")
            return False
            
    except Exception as e:
        print(Fore.RED + f"  [✗] Telegram Error: {e}")
        return False


def test_telegram():
    """Test koneksi Telegram"""
    print(Fore.CYAN + "\n[TEST] Mengirim test ke Telegram...")
    
    pesan = f"<b>UNP JOURNAL DEFENSE SYSTEM v4</b>\n━━━━━━━━━━━━━━━━━━━━\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nStatus: <b>ONLINE</b>\nNotifikasi: <b>AKTIF</b>\n\n<i>Sistem siap memantau jurnal UNP</i>"
    
    return kirim_telegram(pesan.strip())


# ===================== SCANNER v4 =====================

def scan_custom(url):
    """Layer 1: Scanner konten + hidden link detection"""
    print(Fore.CYAN + f"  [L1] Custom Scan...")
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/125.0"
        }
        response = requests.get(url, timeout=15, headers=headers, allow_redirects=True)
        
        if response.status_code != 200:
            return {"status": "GAGAL", "temuan": [f"HTTP {response.status_code}"]}
        
        soup = BeautifulSoup(response.text, "lxml")
        temuan = []
        
        # ========== METODE 1: Cek teks di header & footer ==========
        header = soup.find("header")
        footer = soup.find("footer")
        teks_header = header.get_text().lower() if header else ""
        teks_footer = footer.get_text().lower() if footer else ""
        teks_gabungan = teks_header + " " + teks_footer
        
        for kata in KAMUS_JUDOL:
            if kata in teks_gabungan:
                temuan.append(f"JUDOL:{kata}")
        
        for kata in KAMUS_DEFACE:
            if kata in teks_gabungan:
                temuan.append(f"DEFACE:{kata}")
        
        # ========== METODE 2: Deteksi HIDDEN LINK (BARU!) ==========
        hidden_links_ditemukan = 0
        hidden_links_sample = []
        
        for a in soup.find_all("a", href=True):
            style = a.get("style", "").replace(" ", "").lower()
            href = a["href"].strip()
            text = a.get_text(strip=True).lower()
            
            # Cek apakah link disembunyikan
            is_hidden = "display:none" in style or "visibility:hidden" in style
            
            if is_hidden and href:
                # Cek apakah link mengandung judol
                gabungan = href.lower() + " " + text
                for kata in KAMUS_JUDOL:
                    if kata in gabungan:
                        hidden_links_ditemukan += 1
                        if len(hidden_links_sample) < 5:
                            hidden_links_sample.append(f"{kata}:{href[:60]}")
                        break
        
        if hidden_links_ditemukan > 0:
            temuan.append(f"HIDDEN_LINK:{hidden_links_ditemukan} link judol tersembunyi")
            for sample in hidden_links_sample:
                temuan.append(f"   └ {sample}")
        
        # ========== METODE 3: Cek seluruh body text ==========
        body = soup.find("body")
        teks_body = body.get_text().lower() if body else ""
        
        for kata in KAMUS_JUDOL:
            if kata in teks_body and kata not in teks_gabungan:
                temuan.append(f"BODY_HIDDEN:{kata}")
                break  # Satu saja cukup
        
        # ========== METODE 4: Deteksi Redirect ==========
        if response.url != url:
            domain_asal = url.split("/")[2]
            domain_akhir = response.url.split("/")[2]
            if domain_asal != domain_akhir and "unp.ac.id" not in domain_akhir:
                temuan.append(f"REDIRECT:{domain_akhir}")
        
        if temuan:
            return {"status": "MENCURIGAKAN", "temuan": temuan}
        else:
            return {"status": "AMAN", "temuan": []}
    
    except requests.Timeout:
        return {"status": "GAGAL", "temuan": ["TIMEOUT"]}
    except requests.ConnectionError:
        return {"status": "GAGAL", "temuan": ["KONEKSI DITOLAK"]}
    except Exception as e:
        return {"status": "GAGAL", "temuan": [str(e)[:80]]}


def scan_whatweb(url):
    """Layer 2: Deteksi teknologi & versi"""
    print(Fore.BLUE + f"  [L2] WhatWeb Scan...")
    
    try:
        result = subprocess.run(
            ["whatweb", "--no-errors", "--colour=never", url],
            capture_output=True, text=True, timeout=30
        )
        
        output = result.stdout.strip()
        temuan = []
        
        if "Open Journal Systems" in output:
            if "2." in output:
                temuan.append("OJS VERSI LAMA (2.x) - RENTAN CVE!")
            elif "3.0" in output or "3.1" in output:
                temuan.append("OJS VERSI LAWAS (3.0-3.1)")
            else:
                temuan.append("OJS Terdeteksi")
        
        if any(php in output for php in ["PHP/5.", "PHP/7.0", "PHP/7.1"]):
            temuan.append("PHP EOL (End of Life)")
        
        if "Apache/2.2" in output:
            temuan.append("Apache Versi Lama")
        
        if not temuan:
            temuan.append("Teknologi OK")
        
        return temuan
    
    except subprocess.TimeoutExpired:
        return ["WhatWeb Timeout"]
    except FileNotFoundError:
        return ["WhatWeb tidak terinstall"]
    except Exception as e:
        return [f"WhatWeb Error: {e}"]


def scan_virustotal(url):
    """Layer 3: Cek reputasi domain"""
    if not VIRUSTOTAL_API_KEY:
        return []
    
    print(Fore.MAGENTA + f"  [L3] VirusTotal Check...")
    
    try:
        domain = url.split("/")[2]
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        response = requests.get(
            f"https://www.virustotal.com/api/v3/domains/{domain}",
            headers=headers, timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            
            if malicious > 0:
                return [f"VT MALICIOUS: {malicious}/90 engine"]
            elif suspicious > 0:
                return [f"VT SUSPICIOUS: {suspicious}/90 engine"]
            else:
                return ["VT CLEAN"]
    
    except:
        pass
    
    return []


def simpan_log(url, hasil_l1, hasil_l2, hasil_l3, file_log):
    """Simpan hasil ke CSV"""
    semua_temuan = hasil_l1.get("temuan", []) + hasil_l2 + hasil_l3
    
    with open(file_log, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            url,
            hasil_l1.get("status", "UNKNOWN"),
            " | ".join(semua_temuan) if semua_temuan else "-"
        ])


# ===================== MAIN =====================

def scan_semua():
    """Fungsi utama scan semua jurnal"""
    print(Fore.YELLOW + "\n" + "=" * 60)
    print(Fore.YELLOW + f"  SCAN v4: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Fore.YELLOW + "=" * 60)
    
    if not os.path.exists(FILE_INPUT):
        print(Fore.RED + f"\n[!] File '{FILE_INPUT}' tidak ditemukan!")
        return
    
    with open(FILE_INPUT, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    if not urls:
        print(Fore.RED + "\n[!] File daftar_jurnal.txt kosong!\n")
        return
    
    print(Fore.WHITE + f"\n[*] Total URL: {len(urls)}")
    print(Fore.WHITE + f"[*] Layer 1: Custom (Judol/Deface/Hidden Link/Redirect)")
    print(Fore.WHITE + f"[*] Layer 2: WhatWeb (Versi & Teknologi)")
    print(Fore.WHITE + f"[*] Layer 3: VirusTotal ({'AKTIF' if VIRUSTOTAL_API_KEY else 'NONAKTIF'})")
    print(Fore.WHITE + f"[*] Telegram: {'AKTIF' if TELEGRAM_TOKEN else 'NONAKTIF'}\n")
    
    # Buat folder
    for folder in [FOLDER_LOG, FOLDER_BUKTI]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_log = f"{FOLDER_LOG}/scan_{timestamp}.csv"
    file_bukti = f"{FOLDER_BUKTI}/temuan_{timestamp}.txt"
    
    # Tulis header CSV
    with open(file_log, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Waktu", "URL", "Status", "Temuan"])
    
    total = 0
    mencurigakan = 0
    gagal = 0
    aman = 0
    list_mencurigakan = []
    list_gagal = []
    
    waktu_mulai = time.time()
    
    for url in urls:
        total += 1
        print(f"\n{'─'*55}")
        print(Fore.CYAN + f"[{total}/{len(urls)}] {url}")
        print(f"{'─'*55}")
        
        # Layer 1
        hasil_l1 = scan_custom(url)
        
        # Layer 2
        hasil_l2 = scan_whatweb(url)
        
        # Layer 3
        hasil_l3 = scan_virustotal(url)
        
        # Simpan log
        simpan_log(url, hasil_l1, hasil_l2, hasil_l3, file_log)
        
        # Hitung & tampilkan
        semua_temuan = hasil_l1.get("temuan", []) + hasil_l2 + hasil_l3
        
        if hasil_l1["status"] == "MENCURIGAKAN":
            mencurigakan += 1
            list_mencurigakan.append((url, semua_temuan))
            print(Fore.RED + f"  [!!!] MENCURIGAKAN!")
            for t in semua_temuan:
                print(Fore.RED + f"      └─ {t}")
        elif hasil_l1["status"] == "GAGAL":
            gagal += 1
            list_gagal.append((url, semua_temuan))
            print(Fore.MAGENTA + f"  [?] GAGAL: {semua_temuan[:2]}")
        else:
            aman += 1
            print(Fore.GREEN + f"  [✓] AMAN")
            if hasil_l2:
                for t in hasil_l2:
                    print(Fore.YELLOW + f"      └─ {t}")
        
        time.sleep(1)
    
    waktu_total = int(time.time() - waktu_mulai)
    
    # ===================== REKAP =====================
    rekap_console = f"""
{'='*60}
  SCAN SELESAI
{'='*60}
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Waktu: {waktu_total} detik
Log: {file_log}

Total: {total}
Aman: {aman}
Mencurigakan: {mencurigakan}
Gagal: {gagal}
{'='*60}
"""
    
    print(Fore.CYAN + rekap_console)
    
    # ===================== SIMPAN BUKTI =====================
    with open(file_bukti, "w", encoding="utf-8") as f:
        f.write(f"LAPORAN TEMUAN - UNP JOURNAL DEFENSE SYSTEM v4\n")
        f.write(f"{'='*50}\n")
        f.write(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Scan: {total}\n")
        f.write(f"Mencurigakan: {mencurigakan}\n")
        f.write(f"Gagal: {gagal}\n\n")
        
        if list_mencurigakan:
            f.write(f"JURNAL MENCURIGAKAN:\n")
            f.write(f"{'-'*30}\n")
            for url, temuan in list_mencurigakan:
                f.write(f"\n{url}\n")
                for t in temuan:
                    f.write(f"  - {t}\n")
        
        if list_gagal:
            f.write(f"\n\nJURNAL GAGAL AKSES:\n")
            f.write(f"{'-'*30}\n")
            for url, temuan in list_gagal[:20]:
                f.write(f"{url} → {temuan[0] if temuan else 'Unknown'}\n")
    
    print(Fore.GREEN + f"[✓] Bukti: {file_bukti}")
    
    # ===================== TELEGRAM =====================
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        if mencurigakan > 0:
            alert = f"<b>ALARM! {mencurigakan} ANOMALI!</b>\n━━━━━━━━━━━━━━━━━━━━━━\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nTotal: <b>{total}</b>\nAman: <b>{aman}</b>\nMencurigakan: <b>{mencurigakan}</b>\nGagal: <b>{gagal}</b>\n\n<b>Jurnal Mencurigakan:</b>"
            
            for url, temuan in list_mencurigakan[:3]:
                alert += f"\n{url.split('/')[2]}"
                for t in temuan[:2]:
                    alert += f"\n   └ {t[:80]}"
            
            alert += f"\n\n{file_bukti}"
            kirim_telegram(alert.strip())
        else:
            alert = f"<b>SCAN HARIAN AMAN</b>\n━━━━━━━━━━━━━━━━━━━━\n{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n Total: <b>{total}</b>\n Aman: <b>{aman}</b>\n Gagal: <b>{gagal}</b>\n\n<i>Tidak ada anomali terdeteksi</i>"
            kirim_telegram(alert.strip())
    
    print(Fore.GREEN + "\n[✓] Semua selesai.\n")


# ===================== RUN =====================

if __name__ == "__main__":
    print(Fore.CYAN + """
╔══════════════════════════════════════╗
║   UNP JOURNAL DEFENSE SYSTEM v4     ║
║   + Hidden Link Detection           ║
║   L1:Custom L2:WhatWeb L3:VT       ║
╚══════════════════════════════════════╝
""")
    
    print("[1] Scan semua jurnal")
    print("[2] Test Telegram")
    print("[3] Scan + Test Telegram")
    pilihan = input("\nPilih (1/2/3): ").strip()
    
    if pilihan == "2":
        test_telegram()
    elif pilihan == "3":
        test_telegram()
        print("\n" + "="*60)
        input("Tekan ENTER untuk lanjut scan...")
        scan_semua()
    else:
        scan_semua()