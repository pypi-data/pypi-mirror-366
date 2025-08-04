# Topology MCP Server

A Model Context Protocol (MCP) server for accessing topology data from a topology service.

## Installation

### Via pipx (recommended)

```bash
pipx install topology-mcp
```

### Via pip

```bash
pip install topology-mcp
```

## Usage

### Running the MCP Server

```bash
# Run with default settings (port 8000, SSE transport)
topology-mcp

# Run on a specific port
topology-mcp --port 9000

# Run with different transport
topology-mcp --transport stdio

# Run with custom host
topology-mcp --host 127.0.0.1 --port 8000
```

### Environment Variables

- `TOPOLOGY_URL`: Base URL for the topology service (defaults to `http://localhost:{port}`)
- `PORT`: Server port (defaults to 8000)
- `HOST`: Server host (defaults to 0.0.0.0)
- `TRANSPORT`: Transport method - sse, stdio, or streamable-http (defaults to sse)

### Available Tools

The MCP server provides the following tools:

- `get_topology_edges`: Get topology edges from the topology service
- `get_topology_graph`: Get topology graph from the topology service  
- `get_topology_nodes`: Get topology nodes from the topology service
- `get_topology_events`: Get topology events from the topology service

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/topology-mcp.git
cd topology-mcp

# Install in development mode
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
