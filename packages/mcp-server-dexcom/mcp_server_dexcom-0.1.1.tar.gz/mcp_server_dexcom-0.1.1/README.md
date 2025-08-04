# Dexcom MCP Server

A Model Context Protocol server that provides tools to fetch and chart Dexcom CGM data.

> [!CAUTION]
> This server can access the Dexcom Share website and may represent a security risk. Exercise caution when using this MCP server to ensure this does not expose any sensitive health data.

## Available Tools

- `get_latest_glucose_reading` - Fetches the most recent glucose reading from the Dexcom Share website.
- `get_glucose_readings` - Fetches prior 24 hours of glucose readings from the Dexcom Share website.

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-dexcom*.

### Using PIP

Alternatively you can install `mcp-server-dexcom` via pip:

```
pip install mcp-server-dexcom
```

After installation, you can run it as a script using:

```
python -m mcp_server_dexcom
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "dexcom": {
      "command": "uvx",
      "args": ["mcp-server-dexcom"],
      "env": {
        "DEXCOM_USERNAME": "your_dexcom_username",
        "DEXCOM_PASSWORD": "your_dexcom_password"
      }
    }
  }
}
```
</details>

<details>
<summary>Using docker</summary>

```json
{
  "mcpServers": {
    "dexcom": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "mcp/dexcom"],
      "env": {
        "DEXCOM_USERNAME": "your_dexcom_username",
        "DEXCOM_PASSWORD": "your_dexcom_password"
      }
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcpServers": {
    "dexcom": {
      "command": "python",
      "args": ["-m", "mcp_server_dexcom"],
      "env": {
        "DEXCOM_USERNAME": "your_dexcom_username",
        "DEXCOM_PASSWORD": "your_dexcom_password"
      }
    }
  }
}
```
</details>

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```
npx @modelcontextprotocol/inspector uvx mcp-server-dexcom
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/dexcom
npx @modelcontextprotocol/inspector uv run mcp-server-dexcom
```

## Contributing

We encourage contributions to help expand and improve mcp-server-dexcom. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make mcp-server-dexcom even more powerful and useful.

## License

mcp-server-dexcom is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
