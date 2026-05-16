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

### 1. Clone & Install

```bash
git clone https://github.com/zean6178/SmartWallet.git
cd SmartWallet
pip install -r requirements.txt
```

### 2. Konfigurasi

Copy file `.env.example` ke `.env` dan isi dengan data kamu:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
HELIUS_API_KEY=your_helius_api_key
WALLET_ADDRESS=wallet_yang_mau_di_track
WALLET_LABEL=Nama Wallet
TELEGRAM_BOT_TOKEN=bot_token_dari_botfather
TELEGRAM_CHAT_ID=chat_id_kamu
POLL_INTERVAL=10
```

### 3. Jalankan Bot

```bash
python main.py
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
