# Containerized Code Executer MCP

A Model Context Protocol (MCP) server that provides secure Python code execution capabilities using Docker containers. This server allows clients to execute Python code in isolated Docker environments with customizable dependencies.

## Features

- **Secure Execution**: Code runs in isolated Docker containers, preventing system interference
- **Dynamic Dependencies**: Install Python packages on-demand when starting the execution service
- **Persistent State**: Maintains execution state within the container session
- **Socket Communication**: Fast TCP socket communication between client and container
- **MCP Integration**: Built with FastMCP for seamless integration with MCP clients

## Architecture

The project consists of two main components:

1. **MCP Server** (`main.py`): Exposes MCP tools for managing and communicating with code execution containers
2. **Code Executor** (`code_executer/executer.py`): Python REPL server that runs inside Docker containers

## Installation

### Prerequisites

- Python 3.11 or higher
- Docker Desktop or Docker Engine
- UV package manager (recommended) or pip

### Setup

1. Clone or download this project
2. Install dependencies:

```bash
# Using UV (recommended)
uv install

# Or using pip
pip install -r requirements.txt
```

## Usage

### Starting the MCP Server

Run the MCP server:

```bash
python main.py
```

The server will start and expose the following MCP tools:

### Available Tools

#### `start_code_executer`

Starts a new code execution service in a Docker container.

**Parameters:**
- `dependencies` (optional): List of Python packages to install in the container

**Example:**
```python
# Start with no additional dependencies
start_code_executer()

# Start with specific packages
start_code_executer(dependencies=["numpy", "pandas", "matplotlib"])
```

#### `execute_code`

Executes Python code in the running container.

**Parameters:**
- `code`: Python code string to execute

**Example:**
```python
execute_code("print('Hello, World!')")
execute_code("import numpy as np; print(np.array([1, 2, 3]))")
```

#### `stop_code_executer`

Stops and removes the code execution container.

**Example:**
```python
stop_code_executer()
```

## How It Works

1. **Container Creation**: When `start_code_executer` is called, the server:
   - Generates a Dockerfile with specified dependencies
   - Builds a Docker image with Python 3.11 and the executor script
   - Runs a container exposing port 8888

2. **Code Execution**: When `execute_code` is called:
   - The MCP server connects to the container via TCP socket (port 8888)
   - Sends the Python code to the container
   - The container executes the code and returns results as JSON
   - Results include output, errors, and execution status

3. **State Persistence**: Each container maintains its own execution context, so variables and imports persist between code executions within the same session.

## Security Features

- **Isolation**: Code runs in completely isolated Docker containers
- **Network Isolation**: Containers only expose the necessary port for communication
- **Resource Limits**: Docker provides built-in resource management and limits
- **Temporary Containers**: Containers are created with unique names and can be easily cleaned up

## Configuration

### Custom Dependencies

You can specify Python packages to be installed when starting the execution service:

```python
start_code_executer(dependencies=["requests", "beautifulsoup4", "scikit-learn"])
```

### Docker Configuration

The Docker container uses:
- Base image: `python:3.11-slim`
- Working directory: `/app`
- Exposed port: - Package manager: `uv` for fast dependency resolution

## Development

### Project Structure

```
├── main.py                 # MCP server with tool definitions
├── pyproject.toml         # Project configuration and dependencies
├── README.md              #
├── uv.lock               # Locked dependencies
└── code_executer/
    ├── Dockerfile        # Generated dynamically
    └── executer.py      # Python REPL server for containers
```

### Adding New Features

1. **New MCP Tools**: Add new functions decorated with `@mcp.tool()` in `main.py`
2. **Executor Enhancements**: Modify `code_executer/executer.py` for new execution capabilities
3. **Container Customization**: Update the Dockerfile template in `main.py`

## Troubleshooting

### Common Issues

1. **Docker Connection Errors**: Ensure Docker is running and accessible
2. **Port Conflicts**: Make sure port 8888 is available
3. **Container Build Failures**: Check Docker logs for dependency installation issues
