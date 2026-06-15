import os
import json
from pathlib import Path
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

class SolanaWallet:
    def __init__(self):
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.client = Client(self.rpc_url)
        self.keypair = self._load_keypair()

    def _load_keypair(self) -> Keypair:
        wallet_path = Path(os.getenv("WALLET_PATH", "~/.config/solana/id.json")).expanduser()
        with open(wallet_path) as f:
            secret = json.load(f)
        return Keypair.from_bytes(bytes(secret))

    @property
    def pubkey(self) -> Pubkey:
        return self.keypair.pubkey()

    def get_balance(self) -> float:
        response = self.client.get_balance(self.pubkey)
        lamports = response.value
        return lamports / 1_000_000_000  # convert to SOL

    def is_connected(self) -> bool:
        try:
            self.client.get_version()
            return True
        except:
            return False

    def display_info(self):
        console.print("\n[bold green]🔗 Wallet Connected[/bold green]")
        console.print(f"[cyan]Address:[/cyan] {self.pubkey}")
        console.print(f"[cyan]Balance:[/cyan] {self.get_balance():.4f} SOL")
        console.print(f"[cyan]Network:[/cyan] {self.rpc_url}")
        console.print(f"[cyan]Status:[/cyan] {'✅ Online' if self.is_connected() else '❌ Offline'}\n")

if __name__ == "__main__":
    wallet = SolanaWallet()
    wallet.display_info()
