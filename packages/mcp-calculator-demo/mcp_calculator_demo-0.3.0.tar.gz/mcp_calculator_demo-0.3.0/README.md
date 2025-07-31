# MCP Calculator Demo

A Model Context Protocol (MCP) server providing calculator functionality. Available in both Python and TypeScript implementations.

## 🚀 Quick Start

### Using uvx (Python) - Recommended
```bash
# Install and run directly from PyPI
uvx mcp-calculator-demo

# Or use with MCP clients
uvx mcp-calculator-demo --transport stdio
```

### Using npx (Node.js)
```bash
# Install and run directly from npm
npx -y @your-org/mcp-calculator

# Or use with MCP clients  
npx -y @your-org/mcp-calculator
```

## 📦 Package Installation

### Python Package (uvx/pip)
```bash
# Install via pip
pip install mcp-calculator-demo

# Install globally with uvx (recommended)
uvx install mcp-calculator-demo

# Run the server
mcp-calculator --transport stdio
```

### Node.js Package (npx/npm)
```bash
# Install via npm
npm install -g @your-org/mcp-calculator

# Install and run with npx (recommended)
npx -y @your-org/mcp-calculator

# Run the server locally
mcp-calculator-js
```

## 🔧 Configuration for MCP Clients

### Claude Desktop Configuration
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uvx",
      "args": ["mcp-calculator-demo"]
    }
  }
}
```

### VS Code MCP Extension Configuration
Add to your VS Code settings or `.vscode/mcp.json`:

```json
{
  "mcp": {
    "servers": {
      "calculator-python": {
        "command": "uvx",
        "args": ["mcp-calculator-demo"]
      },
      "calculator-typescript": {
        "command": "npx",
        "args": ["-y", "@your-org/mcp-calculator"]
      }
    }
  }
}
```

### General MCP Configuration (mcp.json)
```json
{
  "mcpServers": {
    "calculator-python-uvx": {
      "command": "uvx",
      "args": ["mcp-calculator-demo"],
      "env": {
        "DEBUG": "false"
      }
    },
    "calculator-python-local": {
      "command": "mcp-calculator",
      "args": ["--transport", "stdio"],
      "env": {
        "DEBUG": "true"
      }
    },
    "calculator-typescript-npx": {
      "command": "npx",
      "args": ["-y", "@your-org/mcp-calculator"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "calculator-typescript-local": {
      "command": "mcp-calculator-js",
      "args": [],
      "env": {
        "NODE_ENV": "development"
      }
    }
  }
}
```

## 🛠️ Available Tools

- **add**: Add two numbers together
- **subtract**: Subtract two numbers  
- **multiply**: Multiply two numbers
- **divide**: Divide two numbers (with zero-division protection)

## 🧪 Testing

### Python Version
```bash
# Test the client
python client-stdio.py

# Test with MCP Inspector
mcp dev src/mcp_calculator_demo/server.py
```

### TypeScript Version  
```bash
# Build and test
npm run build
npm run test

# Test with MCP Inspector
mcp dev dist/cli.js
```

## 🏗️ Development

### Python Development
```bash
# Install in development mode
pip install -e .

# Run directly
python -m mcp_calculator_demo.server

# Build for distribution
pip install build
python -m build
```

### TypeScript Development
```bash
# Install dependencies
npm install

# Build
npm run build

# Watch mode
npm run dev

# Publish to npm
npm publish
```

## 📋 Transport Options

Both implementations support multiple transport methods:

- **stdio**: For use with MCP clients (default)
- **sse**: For HTTP Server-Sent Events (Python only)

### Usage Examples
```bash
# Python
mcp-calculator --transport stdio
mcp-calculator --transport sse

# TypeScript (stdio only)
mcp-calculator-js
```

## 🌟 Key Benefits of uvx/npx Packaging

### uvx (Python)
- ✅ **Isolated environments**: Each tool runs in its own virtual environment
- ✅ **No global installs**: Avoid dependency conflicts
- ✅ **Automatic updates**: Always runs the latest version
- ✅ **Easy distribution**: Users don't need to manage Python environments

### npx (Node.js)  
- ✅ **No installation required**: Run packages without installing
- ✅ **Version flexibility**: Specify exact versions with `@version`
- ✅ **Global availability**: Access tools from anywhere
- ✅ **Easy distribution**: Users don't need to manage Node.js packages

## 📖 Usage in MCP Clients

### With Claude Desktop
1. Add server configuration to `claude_desktop_config.json`
2. Restart Claude Desktop
3. Calculator tools will be available in conversations

### With MCP Inspector
```bash
# Test Python version
mcp dev server.py

# Test TypeScript version  
mcp dev dist/cli.js

# Test published packages
uvx mcp-calculator-demo  # Python
npx -y @your-org/mcp-calculator  # TypeScript
```

### With VS Code MCP Extension
1. Configure in VS Code settings or `.vscode/mcp.json`
2. Reload VS Code
3. Calculator tools will be available in the MCP panel

## 🔗 Related Examples

- **Everything Server**: `npx -y @modelcontextprotocol/server-everything`
- **Python Interpreter**: `uvx python-interpreter-mcp`
- **MCP CLI Tool**: `uvx mcp2cli`

## 📄 License

MIT License - see LICENSE file for details.