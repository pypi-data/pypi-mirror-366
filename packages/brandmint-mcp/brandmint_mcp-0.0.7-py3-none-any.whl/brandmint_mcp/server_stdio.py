# server_stdio.py

import asyncio
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from brandmint_mcp.brandmint import build_brandmint_mcp
from mcp.server.lowlevel import NotificationOptions

async def run():
    server = build_brandmint_mcp()
    async with mcp.server.stdio.stdio_server() as (r, w):
        await server.run(
            r, w,
            InitializationOptions(
                server_name=server.name,
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                ),
            )
        )

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()