"""
Smart Wallet Tracker - Main Entry Point
Monitors a Solana wallet and sends Telegram alerts for DEX trades.
"""

import asyncio
import signal
import sys

from config import Config
from tracker.wallet_tracker import WalletTracker
from bot.telegram_bot import TelegramNotifier


class SmartWalletBot:
    """Main application that connects the wallet tracker with Telegram notifications."""

    def __init__(self):
        self.tracker: WalletTracker = None
        self.notifier: TelegramNotifier = None
        self.running = False

    async def start(self):
        """Initialize and start the bot."""
        # Validate config
        errors = Config.validate()
        if errors:
            print("[ERROR] Configuration errors:")
            for err in errors:
                print(f"  - {err}")
            print("\nPlease check your .env file. See .env.example for reference.")
            sys.exit(1)

        Config.display()

        # Initialize components
        self.tracker = WalletTracker(
            wallet_address=Config.WALLET_ADDRESS,
            helius_api_key=Config.HELIUS_API_KEY,
            rpc_url=Config.SOLANA_RPC_URL,
        )

        self.notifier = TelegramNotifier(
            bot_token=Config.TELEGRAM_BOT_TOKEN,
            chat_id=Config.TELEGRAM_CHAT_ID,
        )

        # Send startup message
        await self.notifier.send_startup_message(
            wallet_address=Config.WALLET_ADDRESS,
            wallet_label=Config.WALLET_LABEL,
        )

        print(f"\n[INFO] Tracking wallet: {Config.WALLET_ADDRESS}")
        print(f"[INFO] Polling every {Config.POLL_INTERVAL} seconds...")
        print("[INFO] Press Ctrl+C to stop\n")

        # Start monitoring loop
        self.running = True
        await self._monitor_loop()

    async def _monitor_loop(self):
        """Main monitoring loop - polls for new transactions."""
        while self.running:
            try:
                new_txs = await self.tracker.get_new_transactions()

                for tx_data in new_txs:
                    parsed = self.tracker.parse_swap_transaction(tx_data)

                    if parsed:
                        print(
                            f"[TRADE] {parsed.action} on {parsed.dex}: "
                            f"{parsed.token_in_amount} {parsed.token_in_symbol} -> "
                            f"{parsed.token_out_amount} {parsed.token_out_symbol}"
                        )

                        # Send Telegram alert
                        success = await self.notifier.send_transaction_alert(
                            tx=parsed,
                            wallet_label=Config.WALLET_LABEL,
                        )

                        if success:
                            print(f"[INFO] Telegram alert sent for {parsed.signature[:16]}...")
                        else:
                            print(f"[WARN] Failed to send Telegram alert")

            except Exception as e:
                print(f"[ERROR] Monitor loop error: {e}")
                try:
                    await self.notifier.send_error_message(str(e))
                except Exception:
                    pass

            # Wait before next poll
            await asyncio.sleep(Config.POLL_INTERVAL)

    async def stop(self):
        """Gracefully stop the bot."""
        print("\n[INFO] Shutting down...")
        self.running = False

        if self.tracker:
            await self.tracker.close()
        if self.notifier:
            await self.notifier.send_message("🛑 Smart Wallet Tracker stopped.")
            await self.notifier.close()

        print("[INFO] Bot stopped.")


async def main():
    bot = SmartWalletBot()

    # Handle graceful shutdown
    loop = asyncio.get_event_loop()

    def shutdown_handler():
        asyncio.ensure_future(bot.stop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass

    try:
        await bot.start()
    except KeyboardInterrupt:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
