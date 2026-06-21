# UNP Journal Defense System v4

Sistem Pemantauan Keamanan Jurnal Otomatis untuk Universitas Negeri Padang.

Zero Budget | Open Source | Production Ready

---

## Latar Belakang

Berdasarkan investigasi mandiri selama magang, ditemukan bahwa:

- 194 link dikelola secara desentralisasi
- 2 link terkonfirmasi mengandung ratusan link judi online tersembunyi
- 111 link tidak dapat diakses (rentan subdomain takeover)
- Link judol disembunyikan dengan teknik display:none dan visibility:hidden
- Tim Cyber hanya 1 orang tanpa tools pemantauan otomatis
- Tidak ada budget untuk server atau software keamanan

Sistem ini dibangun sebagai solusi 100% gratis untuk menjawab masalah tersebut.

---

## Fitur

### Layer 1: Custom Scanner
- Deteksi kata kunci judol (slot, togel, casino, dll)
- Deteksi tanda deface/peretasan
- Deteksi hidden link (display:none, visibility:hidden)
- Deteksi redirect mencurigakan
- Analisis header, footer, dan body

### Layer 2: WhatWeb
- Deteksi versi OJS (2.x, 3.0, 3.1 = rentan CVE)
- Deteksi PHP versi EOL (End of Life)
- Deteksi Apache versi lawas
- Inventarisasi teknologi web

### Layer 3: VirusTotal (Opsional)
- Cek reputasi domain via 90+ engine keamanan
- Deteksi malware known
- Deteksi domain blacklist

### Notifikasi & Logging
- Notifikasi real-time via Telegram Bot
- Log CSV harian (riwayat tidak hilang)
- Bukti temuan otomatis (format .txt)
- Output terminal berwarna (colorama)

---

## Instalasi

### Prasyarat
- Python 3.8+
- pip3
- Git
- WhatWeb

### Cara Cepat (Setup Script)
```bash
git clone https://github.com/Ramadhan930/Pendeteksi_link_jurnal.git
cd Pendeteksi_link_jurnal
chmod +x setup.sh
./setup.sh
