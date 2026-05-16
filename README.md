# 🧠 Solana Smart Wallet Tracker

Bot Telegram untuk tracking transaksi buy/sell/swap dari sebuah wallet di Solana. Mendukung deteksi swap di **Jupiter** dan **Raydium** DEX.

## ✨ Features

- 🔍 Monitor real-time transaksi wallet Solana
- 🟢🔴 Deteksi otomatis BUY / SELL / SWAP
- 🏦 Support Jupiter V4/V6 & Raydium V4/CPMM/AMM
- 📲 Notifikasi instan via Telegram Bot
- 🔗 Link langsung ke Solscan untuk setiap transaksi

## 📋 Prerequisites

- Python 3.10+
- [Helius API Key](https://helius.dev) (gratis)
- [Telegram Bot Token](https://t.me/BotFather)
- Telegram Chat ID (dari [@userinfobot](https://t.me/userinfobot))

## 🚀 Setup

### 1. Clone Repository

```bash
git clone https://github.com/zean6178/SmartWallet.git
cd SmartWallet
```

### 2. Buat Virtual Environment (Recommended)

```bash
python -m venv venv
```

Aktifkan virtual environment:

- **Linux/macOS:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi

Copy file `.env.example` ke `.env`:

```bash
cp .env.example .env
```

Buka file `.env` lalu isi dengan data kamu:

```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
HELIUS_API_KEY=your_helius_api_key
WALLET_ADDRESS=wallet_yang_mau_di_track
WALLET_LABEL=Nama Wallet
TELEGRAM_BOT_TOKEN=bot_token_dari_botfather
TELEGRAM_CHAT_ID=chat_id_kamu
POLL_INTERVAL=10
```

> 💡 **Tips:** Lihat bagian [Cara Dapat API Keys](#-cara-dapat-api-keys) di bawah untuk panduan lengkap.

### 5. Jalankan Bot

```bash
python main.py
```

### 6. Jalankan di Background (Opsional)

Kalau mau bot jalan terus di server/VPS:

- **Menggunakan `nohup`:**
  ```bash
  nohup python main.py > bot.log 2>&1 &
  ```

- **Menggunakan `screen`:**
  ```bash
  screen -S smartwallet
  python main.py
  # Tekan Ctrl+A lalu D untuk detach
  # Untuk kembali: screen -r smartwallet
  ```

- **Menggunakan `systemd` (Linux):**

  Buat file `/etc/systemd/system/smartwallet.service`:
  ```ini
  [Unit]
  Description=Smart Wallet Tracker
  After=network.target

  [Service]
  Type=simple
  User=your_username
  WorkingDirectory=/path/to/SmartWallet
  ExecStart=/path/to/SmartWallet/venv/bin/python main.py
  Restart=always
  RestartSec=10

  [Install]
  WantedBy=multi-user.target
  ```

  Lalu jalankan:
  ```bash
  sudo systemctl enable smartwallet
  sudo systemctl start smartwallet
  ```

## 📱 Contoh Notifikasi Telegram

```
🟢 BUY detected!
👛 Wallet: Smart Wallet

🏦 DEX: Jupiter
📤 Spent: 2.5000 SOL
📥 Got: 1,000,000 BONK
💰 SOL Value: 2.5000 SOL

⏰ Time: 2025-01-15 10:30:45 UTC
🔗 View on Solscan
```

## 🔑 Cara Dapat API Keys

### Helius API Key
1. Buka [helius.dev](https://helius.dev)
2. Sign up (gratis)
3. Copy API key dari dashboard

### Telegram Bot Token
1. Chat ke [@BotFather](https://t.me/BotFather) di Telegram
2. Ketik `/newbot`
3. Ikuti instruksi, copy token yang diberikan

### Telegram Chat ID
1. Chat ke [@userinfobot](https://t.me/userinfobot) di Telegram
2. Bot akan reply dengan Chat ID kamu

## 📁 Project Structure

```
SmartWallet/
├── main.py              # Entry point
├── config.py            # Configuration loader
├── tracker/
│   ├── __init__.py
│   └── wallet_tracker.py  # Wallet monitoring & TX parsing
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py    # Telegram notifications
├── .env.example         # Template konfigurasi
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚠️ Notes

- Gunakan Helius RPC untuk rate limit yang lebih tinggi (free tier = 100 req/s)
- Default polling interval 10 detik, bisa disesuaikan di `.env`
- Bot hanya mendeteksi transaksi tipe SWAP (bukan transfer biasa)
