# tool.py
import requests
from typing import Optional
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
from mcp import types as mcp_types
from mcp.server.lowlevel import Server

SELLER_WALLET = "3BMEwjrn9gBfSetARPrAK1nPTXMRsvQzZLN1n4CYjpcU"
FACILITATOR_URL = "https://facilitator.latinum.ai/api/facilitator"
MINT_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v" # USDC
NETWORK = "mainnet"
PRICE_ATOMIC_AMOUNT = 10000 # 0.01 USDC

async def generate_brand(query: str, signed_b64_payload: Optional[str] = None) -> dict:
    print(f"generate_brand called with: query={query}, signedTransactionB64={'yes' if signed_b64_payload else 'no'}")

    try:
        res = requests.post(FACILITATOR_URL, json={
            "chain": "solana",
            "signedTransactionB64": signed_b64_payload,
            "expectedRecipient": SELLER_WALLET,
            "expectedAmountAtomic": PRICE_ATOMIC_AMOUNT,
            "mint": MINT_ADDRESS,
            "network": NETWORK,
        })
        data = res.json() 
    except Exception as e:
        return {"success": False, "message": f"❌ Facilitator error: {str(e)}"}

    if res.status_code == 402:
        return {
            "success": False,
            "message": data.get("error", "❌ Payment required or validation failed.")
        }

    brandmint_res = requests.post("https://delicious-domains.onrender.com/mcp/brands", json={
        "query": query,
        "token": "LatinumIsTinWrappedInGoldWrappedInLomonosovium"
    })

    if brandmint_res.status_code != 200:
        return {
            "success": False,
            "message": f"❌ Brandmint API error: {brandmint_res.status_code}"
        }

    try:
        brandmint_data = brandmint_res.json()
        return {
            "success": True,
            "data": brandmint_data
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Failed to parse brandmint response: {str(e)}"
        }

def build_brandmint_mcp() -> Server:
    tool = FunctionTool(generate_brand)
    server = Server("brandmint-mcp")

    @server.list_tools()
    async def list_tools():
        return [adk_to_mcp_tool_type(tool)]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == tool.name:
            result = await tool.run_async(args=arguments, tool_context=None)
            if result.get("success"):
                return [mcp_types.TextContent(type="text", text=str(result.get("data", "✅ Success")))]
            else:
                return [mcp_types.TextContent(type="text", text=result.get("message", "❌ Something went wrong."))]

        return [mcp_types.TextContent(type="text", text="❌ Tool not found")]

    return server