# server_sse.py

from fastapi import FastAPI
from brandmint_mcp.brandmint import build_brandmint_mcp
from mcp.server.sse import sse_app
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import NotificationOptions

server = build_brandmint_mcp()
app = FastAPI()
app.mount("/sse", sse_app(server))

@app.on_event("startup")
async def initialize_server():
    await server.initialize(
        InitializationOptions(
            server_name=server.name,
            server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            ),
        )
    )