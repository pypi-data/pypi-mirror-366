# Topology MCP Server

A Model Context Protocol (MCP) server for accessing topology data from a topology service.

## Installation

### Via uvx (recommended)

```bash
uvx install topology-mcp
```

### Via pip

```bash
pip install topology-mcp
```

## Usage

### Running the MCP Server

```bash
# Start the MCP server with stdio transport (for MCP clients)
topology-mcp --transport stdio

# Start the MCP server with HTTP transport
topology-mcp --transport streamable-http --port 8001

# Start the MCP server with SSE transport
topology-mcp --transport sse --port 8002
```

### Advanced Usage

```bash
# Use a different topology service URL
export TOPOLOGY_URL=http://my-topology-service:8080
topology-mcp --transport stdio

# Use a different port
topology-mcp --transport streamable-http --port 9000

# Use environment variable for topology service
export TOPOLOGY_URL=http://my-service:9000
topology-mcp --transport sse
```

### Environment Variables

- `TOPOLOGY_URL`: Base URL for the topology service (defaults to `http://localhost:8000`)
- `PORT`: Server port (defaults to 8000)
- `HOST`: Server host (defaults to 0.0.0.0)
- `TRANSPORT`: Transport method (sse, stdio, streamable-http)

## Examples

```bash
# Start MCP server for use with Claude Desktop
topology-mcp --transport stdio

# Start MCP server on custom port
topology-mcp --transport streamable-http --port 9000

# Connect to a remote topology service
export TOPOLOGY_URL=https://topology.example.com
topology-mcp --transport sse
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/topology-mcp.git
cd topology-mcp

# Install in development mode with uv
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

## License

MIT License - see LICENSE file for details.
