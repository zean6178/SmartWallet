"""
Configuration module for Smart Wallet Tracker.
Loads settings from .env file.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Solana
    SOLANA_RPC_URL: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "")

    # Target wallet
    WALLET_ADDRESS: str = os.getenv("WALLET_ADDRESS", "")
    WALLET_LABEL: str = os.getenv("WALLET_LABEL", "Smart Wallet")

    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Polling
    POLL_INTERVAL: int = int(os.getenv("POLL_INTERVAL", "10"))

    @classmethod
    def validate(cls) -> list[str]:
        """Validate that all required config values are set. Returns list of errors."""
        errors = []

        if not cls.HELIUS_API_KEY or cls.HELIUS_API_KEY == "your_helius_api_key_here":
            errors.append("HELIUS_API_KEY is not set")

        if not cls.WALLET_ADDRESS or cls.WALLET_ADDRESS == "your_target_wallet_address_here":
            errors.append("WALLET_ADDRESS is not set")

        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
            errors.append("TELEGRAM_BOT_TOKEN is not set")

        if not cls.TELEGRAM_CHAT_ID or cls.TELEGRAM_CHAT_ID == "your_chat_id_here":
            errors.append("TELEGRAM_CHAT_ID is not set")

        return errors

    @classmethod
    def display(cls):
        """Print current config (masking sensitive values)."""
        print("=" * 50)
        print("Smart Wallet Tracker - Configuration")
        print("=" * 50)
        print(f"  RPC URL:        {cls.SOLANA_RPC_URL}")
        print(f"  Helius API Key: {'***' + cls.HELIUS_API_KEY[-4:] if len(cls.HELIUS_API_KEY) > 4 else '(not set)'}")
        print(f"  Wallet:         {cls.WALLET_ADDRESS[:6]}...{cls.WALLET_ADDRESS[-4:] if len(cls.WALLET_ADDRESS) > 10 else '(not set)'}")
        print(f"  Wallet Label:   {cls.WALLET_LABEL}")
        print(f"  TG Bot Token:   {'***' + cls.TELEGRAM_BOT_TOKEN[-4:] if len(cls.TELEGRAM_BOT_TOKEN) > 4 else '(not set)'}")
        print(f"  TG Chat ID:     {cls.TELEGRAM_CHAT_ID}")
        print(f"  Poll Interval:  {cls.POLL_INTERVAL}s")
        print("=" * 50)
