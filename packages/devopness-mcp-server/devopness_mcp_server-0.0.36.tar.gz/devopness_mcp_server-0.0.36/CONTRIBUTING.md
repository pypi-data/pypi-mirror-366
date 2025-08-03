# Developer guide to contribute to Devopness MCP Server

## Local Development

To run from source on tools such as Claude, Cursor, Visual Studio Code, Windsurf, etc

1. Find and edit the `mcp.json` file on your favorite tool
1. Add `devopness` MCP Server as exemplified below

### Using STDIO

Connect using:

#### Cursor (~/.cursor/mcp.json)

```json
{
  "mcpServers": {
    "devopness": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/full/path/to/devopness-ai/mcp-server",
        "devopness-mcp-server",
        "--transport",
        "stdio"
      ],
      "env": {
        "DEVOPNESS_USER_EMAIL": "YOUR_DEVOPNESS_USER_EMAIL",
        "DEVOPNESS_USER_PASSWORD": "YOUR_DEVOPNESS_USER_PASSWORD"
      }
    }
  }
}
```

#### VSCode (~/.config/Code/User/settings.json)

```json
{
  "mcp": {
    "servers": {
      "devopness": {
        "command": "uv",
        "args": [
          "run",
          "--directory",
          "/full/path/to/devopness-ai/mcp-server",
          "devopness-mcp-server",
          "--transport",
          "stdio"
        ],
        "env": {
          "DEVOPNESS_USER_EMAIL": "YOUR_DEVOPNESS_USER_EMAIL",
          "DEVOPNESS_USER_PASSWORD": "YOUR_DEVOPNESS_USER_PASSWORD"
        }
      }
    }
  }
}
```

### Using HTTP server

**Run local HTTP server**:

```shell
cd "/full/path/to/devopness-ai/mcp-server"

# Copy the .env.example file to .env
cp .env.example .env

# Run the mcp server
uv run devopness-mcp-server --host localhost --port 8000
```

Then connect using:

#### Cursor

```json
{
  "mcpServers": {
    "devopness": {
      "url": "http://localhost:8000/mcp/",
    }
  }
}
```

#### VSCode

```json
{
  "mcp": {
    "servers": {
      "devopness": {
        "type": "http",
        "url": "http://localhost:8000/mcp/",
      }
    }
  }
}
```

## Testing and Debugging

### Run with MCP Inspector

```shell
# --- Setup the MCP Server configuration --- #

# Go to the MCP Server directory
cd "/full/path/to/devopness-ai/mcp-server"

# Copy the .env.example file to .env
cp .env.example .env

# --- Using Official MCP Inspector --- #

# In one terminal, run the mcp server
uv run devopness-mcp-server

# In another terminal, run the inspector
npx -y @modelcontextprotocol/inspector

# Configuration must be set in the inspector web interface:
#   Transport Type = Streamble HTTP
#   URL = http://localhost:8000/mcp/

# --- Using alpic.ai MCP Inspector --- #

# In one terminal, run the inspector and the mcp server in stdio
npx -y @alpic-ai/grizzly uv run devopness-mcp-server --transport stdio

# Environment variables must be set in the inspector web interface:
#   DEVOPNESS_USER_EMAIL=<YOUR_DEVOPNESS_USER_EMAIL>
#   DEVOPNESS_USER_PASSWORD=<YOUR_DEVOPNESS_USER_PASSWORD>
```

### Run on Postman

Follow Postman guide to [create an MCP Request](https://learning.postman.com/docs/postman-ai-agent-builder/mcp-requests/create/)

* Choose `STDIO`
* Use the server command:

```shell
uv run --directory "/full/path/to/devopness-ai/mcp-server" devopness-mcp-server --transport stdio
```
