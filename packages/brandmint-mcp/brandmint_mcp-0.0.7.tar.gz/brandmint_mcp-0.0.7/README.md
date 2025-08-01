# 🌤️ Brandmint MCP Tool (Latinum Paywalled Agent Tool)

A Model Context Protocol (MCP) tool for brandmint.ai
This service allows to generate doamin and brand for your projects.

# 🧠 Claude Integration

Install brandmint-mcp:
```bash
pip install brandmint-mcp
```

NOTE: Use pipx on mac!

Edit your Claude Desktop config:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

```json
{
  "mcpServers": {
      "brandmint_mcp": {
          "command": "/Users/{YOUR_USER}/.local/bin/brandmint-mcp",
      }
  }
}
```

Then restart Claude.

# 🔧 Developper testing
To install your local build as a CLI for testing with Claude:

```bash
git clone https://github.com/dennj/brandmint_mcp.git
cd brandmint_mcp
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --upgrade --upgrade-strategy eager -r requirements.txt
pip install --editable .
```

Then configure Clouse to use it.

```json
{
  "mcpServers": {
      "brandmint_mcp": {
          "command": "/Users/{YOUR_USER}/workspace/brandmint_mcp/.venv/bin/python",
          "args": [
              "/Users/{YOUR_USER}/workspace/brandmint_mcp/brandmint_mcp/server_stdio.py"
          ]
      }
  }
}
```

# 📑 PyPI Publishing

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
rm -rf dist/ build/ *.egg-info
python3 -m build
python3 -m twine upload dist/*
```

See the output here: https://pypi.org/project/brandmint-mcp/


## ⚙️ Configuration

Create a `.env` file in the project root:

```ini
# .env
SELLER_WALLET=3BMEwjrn9gBfSetARPrAK1nPTXMRsvQzZLN1n4CYjpcU
```

* `SELLER_WALLET`: The Solana devnet public address that will receive payments.

## 🚀 Run Locally

```bash
python server_stdio.py
```

Claude will detect the tool when properly configured.



## 💳 How It Works

* ❓ Ask: `Generate branding for a website about fast cars!` → Claude gets a `402` and triggers the wallet.
* ✅ Claude pays using Latinum Wallet and retries.
