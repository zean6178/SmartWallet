"""
Solana Smart Wallet Tracker
Monitors a wallet for buy/sell/swap transactions on Jupiter & Raydium DEXes.
Uses Helius API for parsed transaction data.
"""

import asyncio
import time
from typing import Optional
import aiohttp

# Known DEX Program IDs
JUPITER_V6_PROGRAM = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
JUPITER_V4_PROGRAM = "JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB"
JUPITER_AGGREGATOR_V6 = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4"
RAYDIUM_V4_PROGRAM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
RAYDIUM_CPMM_PROGRAM = "CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C"
RAYDIUM_AMM_PROGRAM = "routeUGWgWzqBWFcrCfv8tritsqukccJPu3q5GPP3xS"

# SOL mint address
SOL_MINT = "So11111111111111111111111111111111111111112"
WSOL_MINT = "So11111111111111111111111111111111111111112"

DEX_PROGRAMS = {
    JUPITER_V6_PROGRAM: "Jupiter V6",
    JUPITER_V4_PROGRAM: "Jupiter V4",
    JUPITER_AGGREGATOR_V6: "Jupiter",
    RAYDIUM_V4_PROGRAM: "Raydium V4",
    RAYDIUM_CPMM_PROGRAM: "Raydium CPMM",
    RAYDIUM_AMM_PROGRAM: "Raydium AMM",
}


class Transaction:
    """Represents a parsed swap/trade transaction."""

    def __init__(
        self,
        signature: str,
        timestamp: int,
        dex: str,
        action: str,  # "BUY" or "SELL"
        token_in: str,
        token_in_amount: float,
        token_in_symbol: str,
        token_out: str,
        token_out_amount: float,
        token_out_symbol: str,
        sol_amount: Optional[float] = None,
    ):
        self.signature = signature
        self.timestamp = timestamp
        self.dex = dex
        self.action = action
        self.token_in = token_in
        self.token_in_amount = token_in_amount
        self.token_in_symbol = token_in_symbol
        self.token_out = token_out
        self.token_out_amount = token_out_amount
        self.token_out_symbol = token_out_symbol
        self.sol_amount = sol_amount

    def __repr__(self):
        return (
            f"Transaction({self.action} on {self.dex}: "
            f"{self.token_in_amount} {self.token_in_symbol} -> "
            f"{self.token_out_amount} {self.token_out_symbol})"
        )


class WalletTracker:
    """Tracks a Solana wallet for DEX swap transactions using Helius API."""

    def __init__(self, wallet_address: str, helius_api_key: str, rpc_url: str):
        self.wallet_address = wallet_address
        self.helius_api_key = helius_api_key
        self.rpc_url = rpc_url
        self.helius_url = f"https://api.helius.xyz/v0"
        self.last_signature: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_recent_transactions(self, limit: int = 10) -> list[dict]:
        """Fetch recent parsed transactions from Helius API."""
        session = await self._get_session()
        url = (
            f"{self.helius_url}/addresses/{self.wallet_address}/transactions"
            f"?api-key={self.helius_api_key}&limit={limit}"
        )

        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_text = await resp.text()
                    print(f"[ERROR] Helius API error {resp.status}: {error_text}")
                    return []
        except Exception as e:
            print(f"[ERROR] Failed to fetch transactions: {e}")
            return []

    async def get_new_transactions(self) -> list[dict]:
        """Fetch only new transactions since last check."""
        transactions = await self.get_recent_transactions(limit=20)

        if not transactions:
            return []

        if self.last_signature is None:
            # First run, just record the latest and return it
            self.last_signature = transactions[0].get("signature")
            return transactions[:1]  # Return only the most recent one

        # Find new transactions (before the last known signature)
        new_txs = []
        for tx in transactions:
            if tx.get("signature") == self.last_signature:
                break
            new_txs.append(tx)

        if new_txs:
            self.last_signature = new_txs[0].get("signature")

        return new_txs

    def parse_swap_transaction(self, tx: dict) -> Optional[Transaction]:
        """Parse a Helius parsed transaction into a Transaction object."""
        signature = tx.get("signature", "")
        timestamp = tx.get("timestamp", 0)
        tx_type = tx.get("type", "")
        source = tx.get("source", "")

        # Check if it's a swap transaction
        if tx_type != "SWAP":
            return None

        # Determine which DEX
        dex = self._identify_dex(tx)
        if not dex:
            dex = source if source else "Unknown DEX"

        # Parse token transfers
        token_transfers = tx.get("tokenTransfers", [])
        native_transfers = tx.get("nativeTransfers", [])

        if not token_transfers and not native_transfers:
            return None

        # Identify tokens in and out for the tracked wallet
        tokens_sent = []  # Tokens the wallet sent (sold)
        tokens_received = []  # Tokens the wallet received (bought)

        for transfer in token_transfers:
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")
            mint = transfer.get("mint", "")
            amount = transfer.get("tokenAmount", 0)
            symbol = transfer.get("symbol", self._shorten_mint(mint))

            if from_addr == self.wallet_address:
                tokens_sent.append({
                    "mint": mint,
                    "amount": amount,
                    "symbol": symbol,
                })
            elif to_addr == self.wallet_address:
                tokens_received.append({
                    "mint": mint,
                    "amount": amount,
                    "symbol": symbol,
                })

        # Also check native SOL transfers
        for transfer in native_transfers:
            from_addr = transfer.get("fromUserAccount", "")
            to_addr = transfer.get("toUserAccount", "")
            amount_lamports = transfer.get("amount", 0)
            amount_sol = amount_lamports / 1e9

            # Filter out tiny amounts (fees)
            if amount_sol < 0.001:
                continue

            if from_addr == self.wallet_address:
                tokens_sent.append({
                    "mint": SOL_MINT,
                    "amount": amount_sol,
                    "symbol": "SOL",
                })
            elif to_addr == self.wallet_address:
                tokens_received.append({
                    "mint": SOL_MINT,
                    "amount": amount_sol,
                    "symbol": "SOL",
                })

        if not tokens_sent or not tokens_received:
            return None

        # Determine action: BUY = spending SOL/USDC for token, SELL = spending token for SOL/USDC
        token_in = tokens_sent[0]
        token_out = tokens_received[0]

        # Determine if it's a BUY or SELL
        stable_mints = [SOL_MINT, WSOL_MINT]
        stable_symbols = ["SOL", "USDC", "USDT"]

        if token_in["symbol"] in stable_symbols or token_in["mint"] in stable_mints:
            action = "BUY"
        elif token_out["symbol"] in stable_symbols or token_out["mint"] in stable_mints:
            action = "SELL"
        else:
            action = "SWAP"

        sol_amount = None
        if token_in["symbol"] == "SOL":
            sol_amount = token_in["amount"]
        elif token_out["symbol"] == "SOL":
            sol_amount = token_out["amount"]

        return Transaction(
            signature=signature,
            timestamp=timestamp,
            dex=dex,
            action=action,
            token_in=token_in["mint"],
            token_in_amount=token_in["amount"],
            token_in_symbol=token_in["symbol"],
            token_out=token_out["mint"],
            token_out_amount=token_out["amount"],
            token_out_symbol=token_out["symbol"],
            sol_amount=sol_amount,
        )

    def _identify_dex(self, tx: dict) -> Optional[str]:
        """Identify which DEX was used from the transaction."""
        source = tx.get("source", "").upper()

        if "JUPITER" in source:
            return "Jupiter"
        elif "RAYDIUM" in source:
            return "Raydium"

        # Check account data / instructions
        instructions = tx.get("instructions", [])
        for ix in instructions:
            program_id = ix.get("programId", "")
            if program_id in DEX_PROGRAMS:
                return DEX_PROGRAMS[program_id]

        return None

    @staticmethod
    def _shorten_mint(mint: str) -> str:
        """Shorten a mint address for display."""
        if len(mint) > 8:
            return f"{mint[:4]}...{mint[-4:]}"
        return mint

    async def get_token_info(self, mint_address: str) -> dict:
        """Get token metadata from Helius DAS API."""
        session = await self._get_session()
        url = f"https://mainnet.helius-rpc.com/?api-key={self.helius_api_key}"

        payload = {
            "jsonrpc": "2.0",
            "id": "token-info",
            "method": "getAsset",
            "params": {"id": mint_address},
        }

        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    result = data.get("result", {})
                    content = result.get("content", {})
                    metadata = content.get("metadata", {})
                    return {
                        "name": metadata.get("name", "Unknown"),
                        "symbol": metadata.get("symbol", "???"),
                    }
        except Exception as e:
            print(f"[ERROR] Failed to get token info: {e}")

        return {"name": "Unknown", "symbol": "???"}
