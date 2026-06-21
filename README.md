cd ~/Development/cybersecurity/unp-jurnal-scanner

cat > setup.sh << 'SETUPEOF'
#!/bin/bash
# ============================================================
# UNP JOURNAL DEFENSE SYSTEM - SETUP SCRIPT
# ============================================================

echo "============================================="
echo " UNP JOURNAL DEFENSE SYSTEM - SETUP"
echo "============================================="

# Warna
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# -------------------------------
# 1. Update Sistem
# -------------------------------
echo -e "\n${CYAN}[1/6] Update sistem...${NC}"
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}[OK] Sistem terupdate${NC}"

# -------------------------------
# 2. Install Dependencies Sistem
# -------------------------------
echo -e "\n${CYAN}[2/6] Install dependencies sistem...${NC}"
sudo apt install -y python3 python3-pip python3-full python3-venv git curl wget whatweb firefox
echo -e "${GREEN}[OK] Dependencies sistem terinstall${NC}"

# -------------------------------
# 3. Buat Virtual Environment
# -------------------------------
echo -e "\n${CYAN}[3/6] Buat virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}[OK] Virtual environment dibuat${NC}"

# -------------------------------
# 4. Install Dependencies Python
# -------------------------------
echo -e "\n${CYAN}[4/6] Install dependencies Python...${NC}"
pip install --upgrade pip
pip install requests beautifulsoup4 python-telegram-bot schedule colorama python-dotenv lxml selenium webdriver-manager
echo -e "${GREEN}[OK] Dependencies Python terinstall${NC}"

# -------------------------------
# 5. Buat File Konfigurasi
# -------------------------------
echo -e "\n${CYAN}[5/6] Setup file konfigurasi...${NC}"

# .env
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
VIRUSTOTAL_API_KEY=
ENVEOF
    echo -e "${GREEN}[OK] .env dibuat${NC}"
    echo -e "${YELLOW}[!] Jangan lupa isi TELEGRAM_TOKEN dan TELEGRAM_CHAT_ID di file .env${NC}"
else
    echo -e "${YELLOW}[SKIP] .env sudah ada${NC}"
fi

# .env.example
cat > .env.example << 'ENVEOF'
# ==========================================
# UNP JOURNAL DEFENSE SYSTEM - CONFIGURATION
# ==========================================

# Telegram Bot Token (dari @BotFather)
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Telegram Chat ID (dari @userinfobot)
TELEGRAM_CHAT_ID=1234567890

# VirusTotal API Key (opsional, dari virustotal.com)
VIRUSTOTAL_API_KEY=
ENVEOF
echo -e "${GREEN}[OK] .env.example dibuat${NC}"

# .gitignore
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'GITEOF'
# Sensitif
.env
logs/
bukti/
daftar_jurnal.txt

# Python
venv/
env/
__pycache__/
*.py[cod]
*.so

# IDE
.vscode/
.idea/

# OS
.DS_Store
.directory
Thumbs.db
GITEOF
    echo -e "${GREEN}[OK] .gitignore dibuat${NC}"
else
    echo -e "${YELLOW}[SKIP] .gitignore sudah ada${NC}"
fi

# daftar_jurnal.txt (template)
if [ ! -f daftar_jurnal.txt ]; then
    cat > daftar_jurnal.txt << 'JURNALEOF'
# Format: Satu URL per baris

JURNALEOF
    echo -e "${GREEN}[OK] daftar_jurnal.txt dibuat${NC}"
    echo -e "${YELLOW}[!] Jangan lupa isi daftar_jurnal.txt dengan URL jurnal UNP${NC}"
else
    echo -e "${YELLOW}[SKIP] daftar_jurnal.txt sudah ada${NC}"
fi

# Buat folder
mkdir -p logs bukti
echo -e "${GREEN}[OK] Folder logs/ dan bukti/ dibuat${NC}"

# -------------------------------
# 6. Verifikasi
# -------------------------------
echo -e "\n${CYAN}[6/6] Verifikasi instalasi...${NC}"

echo -e "\n${YELLOW}Python:${NC}"
python3 --version

echo -e "\n${YELLOW}Pip:${NC}"
pip --version

echo -e "\n${YELLOW}WhatWeb:${NC}"
whatweb --version 2>/dev/null || echo "WhatWeb tidak terdeteksi"

echo -e "\n${YELLOW}Library Python:${NC}"
pip list | grep -E "requests|beautifulsoup4|python-telegram-bot|colorama|python-dotenv|lxml|selenium"

echo -e "\n${YELLOW}File:${NC}"
ls -la | grep -E "^-|^d" | awk '{print $9}'

# -------------------------------
# SELESAI
# -------------------------------
echo -e "\n${GREEN}=============================================${NC}"
echo -e "${GREEN}  SETUP SELESAI!${NC}"
echo -e "${GREEN}=============================================${NC}"
echo -e ""
echo -e "${YELLOW}Langkah selanjutnya:${NC}"
echo -e "  1. Edit .env:          ${CYAN}nano .env${NC}"
echo -e "  2. Isi daftar jurnal:  ${CYAN}nano daftar_jurnal.txt${NC}"
echo -e "  3. Aktifkan venv:      ${CYAN}source venv/bin/activate${NC}"
echo -e "  4. Jalankan scanner:   ${CYAN}python3 scanner_v4.py${NC}"
echo -e ""
echo -e "${YELLOW}Butuh bantuan? Baca README.md${NC}"
echo -e ""
SETUPEOF

chmod +x setup.sh

echo "============================================="
echo "  SETUP SCRIPT BERHASIL DIBUAT!"
echo "============================================="
echo ""
echo "Cara pakai:"
echo "  chmod +x setup.sh"
echo "  ./setup.sh"
echo ""