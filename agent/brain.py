import os
import asyncio
import json
import sys
from groq import Groq
from dotenv import load_dotenv
from rich.console import Console

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.tools.price import get_all_prices

load_dotenv()
console = Console()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_prices",
            "description": "Get live prices of SOL, BTC, ETH, BONK, JUP",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_wallet_balance",
            "description": "Get current SOL balance of the agent wallet",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_market",
            "description": "Analyze market and suggest trading action",
            "parameters": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "price": {"type": "number"}
                },
                "required": ["token", "price"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are an autonomous Solana DeFi trading agent.
You monitor token prices, analyze market conditions, and suggest trading actions.
You are running on Solana devnet — all trades are simulated for safety.
Be concise, data-driven, and always explain your reasoning."""


async def process_tool(tool_name, tool_input):
    if tool_name == "get_prices":
        prices = await get_all_prices()
        lines = [f"{p['symbol']}: ${p['price']}" for p in prices]
        return "Current prices:\n" + "\n".join(lines)
    elif tool_name == "get_wallet_balance":
        from agent.wallet import SolanaWallet
        wallet = SolanaWallet()
        return f"Wallet balance: {wallet.get_balance():.4f} SOL"
    elif tool_name == "analyze_market":
        token = tool_input.get("token", "SOL")
        price = tool_input.get("price", 0)
        return f"Analyzing {token} at ${price} — devnet simulation mode active"
    return "Tool not found"


async def run_agent(user_message):
    console.print(f"\n[bold cyan]You:[/bold cyan] {user_message}\n")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            tool_calls_data = []
            for tc in msg.tool_calls:
                tool_calls_data.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
            messages.append({
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": tool_calls_data
            })
            for tc in msg.tool_calls:
                tool_name = tc.function.name
                tool_input = json.loads(tc.function.arguments)
                console.print(f"[yellow]🔧 Using tool: {tool_name}[/yellow]")
                result = await process_tool(tool_name, tool_input)
                console.print(f"[dim]{result}[/dim]\n")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            console.print(f"[bold green]🤖 Agent:[/bold green] {msg.content}\n")
            break


if __name__ == "__main__":
    async def main():
        console.print("[bold green]🤖 Solana AI Agent — Groq Brain[/bold green]")
        console.print("[dim]Type exit to quit[/dim]\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                break
            if user_input:
                await run_agent(user_input)
    asyncio.run(main())
