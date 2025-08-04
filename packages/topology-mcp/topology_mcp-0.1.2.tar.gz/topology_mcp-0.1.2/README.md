# Topology CLI

A command-line interface for accessing topology data from a topology service.

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

### Basic Commands

```bash
# Get topology edges
topology-cli edges

# Get topology graph
topology-cli graph

# Get topology nodes
topology-cli nodes

# Get topology events
topology-cli events
```

### Advanced Usage

```bash
# Use a different topology service URL
topology-cli edges --url http://my-topology-service:8080

# Output as compact JSON
topology-cli nodes --format json

# Use environment variable for URL
export TOPOLOGY_URL=http://my-service:9000
topology-cli graph
```

### Environment Variables

- `TOPOLOGY_URL`: Base URL for the topology service (defaults to `http://localhost:8000`)

## Examples

```bash
# Get all topology nodes in pretty format
topology-cli nodes

# Get topology graph as compact JSON
topology-cli graph --format json

# Connect to a remote topology service
topology-cli edges --url https://topology.example.com
```

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
