"""
Telegram Bot Module for Smart Wallet Tracker
Sends formatted notifications for wallet swap/trade transactions.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

import aiohttp

from tracker.wallet_tracker import Transaction


class TelegramNotifier:
    """Sends formatted trade notifications to a Telegram chat."""

    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send a message to the configured Telegram chat."""
        session = await self._get_session()
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    return True
                else:
                    error = await resp.text()
                    print(f"[ERROR] Telegram API error {resp.status}: {error}")
                    return False
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram message: {e}")
            return False

    async def send_transaction_alert(self, tx: Transaction, wallet_label: str = "") -> bool:
        """Format and send a transaction alert."""
        message = self._format_transaction(tx, wallet_label)
        return await self.send_message(message)

    def _format_transaction(self, tx: Transaction, wallet_label: str = "") -> str:
        """Format a transaction into a readable Telegram message."""

        # Action emoji
        if tx.action == "BUY":
            emoji = "🟢"
            action_text = "BUY"
        elif tx.action == "SELL":
            emoji = "🔴"
            action_text = "SELL"
        else:
            emoji = "🔄"
            action_text = "SWAP"

        # Format timestamp
        if tx.timestamp:
            dt = datetime.fromtimestamp(tx.timestamp, tz=timezone.utc)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        else:
            time_str = "Unknown"

        # Wallet label
        wallet_display = wallet_label if wallet_label else self._shorten_address(tx.signature[:44] if len(tx.signature) > 44 else "")

        # Format amounts
        amount_in = self._format_amount(tx.token_in_amount)
        amount_out = self._format_amount(tx.token_out_amount)

        # Solscan link
        solscan_link = f"https://solscan.io/tx/{tx.signature}"

        # Build message
        lines = [
            f"{emoji} <b>{action_text}</b> detected!",
            f"",
            f"🏦 <b>DEX:</b> {tx.dex}",
            f"",
            f"📤 <b>Spent:</b> {amount_in} {tx.token_in_symbol}",
            f"📥 <b>Got:</b> {amount_out} {tx.token_out_symbol}",
        ]

        if tx.sol_amount is not None:
            lines.append(f"💰 <b>SOL Value:</b> {self._format_amount(tx.sol_amount)} SOL")

        lines.extend([
            f"",
            f"⏰ <b>Time:</b> {time_str}",
            f"🔗 <a href=\"{solscan_link}\">View on Solscan</a>",
        ])

        if wallet_label:
            lines.insert(1, f"👛 <b>Wallet:</b> {wallet_label}")

        return "\n".join(lines)

    async def send_startup_message(self, wallet_address: str, wallet_label: str = "") -> bool:
        """Send a bot startup notification."""
        short_addr = self._shorten_address(wallet_address)
        label = f" ({wallet_label})" if wallet_label else ""

        message = (
            f"🚀 <b>Smart Wallet Tracker Started!</b>\n"
            f"\n"
            f"👛 Tracking: <code>{short_addr}</code>{label}\n"
            f"📡 Monitoring for swaps on Jupiter & Raydium\n"
            f"\n"
            f"✅ Bot is running..."
        )
        return await self.send_message(message)

    async def send_error_message(self, error: str) -> bool:
        """Send an error notification."""
        message = f"⚠️ <b>Tracker Error:</b>\n<code>{error}</code>"
        return await self.send_message(message)

    @staticmethod
    def _format_amount(amount: float) -> str:
        """Format token amount for display."""
        if amount == 0:
            return "0"
        elif amount >= 1_000_000:
            return f"{amount:,.0f}"
        elif amount >= 1:
            return f"{amount:,.4f}"
        elif amount >= 0.0001:
            return f"{amount:.6f}"
        else:
            return f"{amount:.10f}"

    @staticmethod
    def _shorten_address(address: str) -> str:
        """Shorten a Solana address for display."""
        if len(address) > 8:
            return f"{address[:4]}...{address[-4:]}"
        return address
