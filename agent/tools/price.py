import httpx
import asyncio
from rich.console import Console
from rich.table import Table

console = Console()

COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

TOKENS = {
    "SOL":  "solana",
    "BTC":  "bitcoin",
    "ETH":  "ethereum",
    "BONK": "bonk",
    "JUP":  "jupiter-exchange-solana",
}

async def get_all_prices() -> list:
    ids = ",".join(TOKENS.values())
    async with httpx.AsyncClient() as client:
        response = await client.get(
            COINGECKO_API,
            params={"ids": ids, "vs_currencies": "usd"}
        )
        data = response.json()
        prices = []
        for symbol, cg_id in TOKENS.items():
            price = data.get(cg_id, {}).get("usd", 0)
            prices.append({
                "symbol": symbol,
                "price": price
            })
        return prices

def display_prices(prices: list):
    table = Table(title="📈 Live Crypto Prices (CoinGecko)")
    table.add_column("Token", style="cyan", width=8)
    table.add_column("Price (USD)", style="green", justify="right")
    for p in prices:
        table.add_row(
            p["symbol"],
            f"${p['price']:.6f}" if p['price'] < 1 else f"${p['price']:.2f}",
        )
    console.print(table)

if __name__ == "__main__":
    async def main():
        console.print("[bold]Fetching live prices...[/bold]\n")
        prices = await get_all_prices()
        display_prices(prices)
    asyncio.run(main())
