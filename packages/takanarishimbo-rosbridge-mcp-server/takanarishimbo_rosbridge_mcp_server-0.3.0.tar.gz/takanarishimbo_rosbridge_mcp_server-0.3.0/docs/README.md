[English](README.md) | [日本語](README_ja.md) | **README**

# Rosbridge MCP Server

A Model Context Protocol (MCP) server that provides comprehensive tools for interacting with ROS (Robot Operating System) via rosbridge WebSocket connection. This Python implementation enables AI assistants to monitor and control ROS systems through a standardized interface.

## Features

- **Topic Operations**: List topics, get topic info, and publish messages
- **Service Operations**: List services and call ROS services
- **Action Operations**: List action servers, send goals, and cancel actions

## Usage

Choose one of these examples based on your needs:

**Basic usage (localhost):**

```json
{
  "mcpServers": {
    "rosbridge": {
      "command": "uvx",
      "args": ["takanarishimbo-rosbridge-mcp-server"]
    }
  }
}
```

**Custom rosbridge host:**

```json
{
  "mcpServers": {
    "rosbridge": {
      "command": "uvx",
      "args": ["takanarishimbo-rosbridge-mcp-server"],
      "env": {
        "ROSBRIDGE_HOST": "192.168.1.100",
        "ROSBRIDGE_PORT": "9090"
      }
    }
  }
}
```

**Remote ROS system:**

```json
{
  "mcpServers": {
    "rosbridge": {
      "command": "uvx",
      "args": ["rosbridge-mcp-server"],
      "env": {
        "ROSBRIDGE_HOST": "ros-robot.local",
        "ROSBRIDGE_PORT": "9091"
      }
    }
  }
}
```

## Configuration

The server can be configured using environment variables:

### `ROSBRIDGE_HOST`

The rosbridge server host (default: "localhost")

Examples:

- `localhost`: Local rosbridge
- `192.168.1.100`: Remote IP address
- `ros-robot.local`: Hostname

### `ROSBRIDGE_PORT`

The rosbridge server port (default: "9090")

Standard rosbridge WebSocket port is 9090.

## Available Tools

### Topic Operations

#### `list_topics`

List all available ROS topics with their types.

No parameters required.

#### `get_topic_info`

Get detailed information about a specific topic including publishers and subscribers.

Parameters:

- `topic` (required): The ROS topic name (e.g., "/cmd_vel")

#### `publish_topic`

Publish a message to a ROS topic.

Parameters:

- `topic` (required): The ROS topic name (e.g., "/cmd_vel")
- `message_type` (required): The ROS message type (e.g., "geometry_msgs/Twist")
- `message` (required): The message data as a JSON object

Example:

```json
{
  "name": "publish_topic",
  "arguments": {
    "topic": "/cmd_vel",
    "message_type": "geometry_msgs/Twist",
    "message": {
      "linear": { "x": 0.5, "y": 0.0, "z": 0.0 },
      "angular": { "x": 0.0, "y": 0.0, "z": 0.1 }
    }
  }
}
```

### Service Operations

#### `list_services`

List all available ROS services.

No parameters required.

#### `publish_service`

Call a ROS service.

Parameters:

- `service` (required): The ROS service name (e.g., "/add_two_ints")
- `service_type` (required): The ROS service type (e.g., "rospy_tutorials/AddTwoInts")
- `request` (required): The service request data as a JSON object
- `timeout` (optional): Timeout in seconds (default: 10)

Example:

```json
{
  "name": "publish_service",
  "arguments": {
    "service": "/add_two_ints",
    "service_type": "rospy_tutorials/AddTwoInts",
    "request": {
      "a": 10,
      "b": 20
    }
  }
}
```

### Action Operations

#### `list_actions`

List all available ROS action servers.

No parameters required.

#### `publish_action`

Send a goal to a ROS action server.

Parameters:

- `action_name` (required): The ROS action server name (e.g., "/move_base")
- `action_type` (required): The ROS action type (e.g., "move_base_msgs/MoveBaseAction")
- `goal` (required): The goal data as a JSON object
- `timeout` (optional): Timeout in seconds to wait for result (default: 30)

Example:

```json
{
  "name": "publish_action",
  "arguments": {
    "action_name": "/move_base",
    "action_type": "move_base_msgs/MoveBaseAction",
    "goal": {
      "target_pose": {
        "header": {
          "frame_id": "map"
        },
        "pose": {
          "position": { "x": 1.0, "y": 2.0, "z": 0.0 },
          "orientation": { "x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0 }
        }
      }
    }
  }
}
```

#### `cancel_action`

Cancel a running ROS action goal.

Parameters:

- `action_name` (required): The ROS action server name (e.g., "/move_base")
- `goal_id` (optional): The specific goal ID to cancel (cancels all if not provided)

## Development

1. **Clone this repository**

   ```bash
   git clone https://github.com/TakanariShimbo/rosbridge-mcp-server.git
   cd rosbridge-mcp-server
   ```

2. **Install dependencies using uv**

   ```bash
   uv sync
   ```

3. **Start rosbridge on your ROS system**

   ```bash
   roslaunch rosbridge_server rosbridge_websocket.launch
   ```

4. **Run the server**

   ```bash
   uv run takanarishimbo-rosbridge-mcp-server
   ```

5. **Test with MCP Inspector (optional)**

   ```bash
   npx @modelcontextprotocol/inspector uv run takanarishimbo-rosbridge-mcp-server
   ```

## Publishing to PyPI

This project uses PyPI's Trusted Publishers feature for secure, token-less publishing via GitHub Actions.

### 1. Configure PyPI Trusted Publisher

1. **Log in to PyPI** (create account if needed)

   - Go to https://pypi.org/

2. **Navigate to Publishing Settings**

   - Go to your account settings
   - Click on "Publishing" or go to https://pypi.org/manage/account/publishing/

3. **Add GitHub Publisher**
   - Click "Add a new publisher"
   - Select "GitHub" as the publisher
   - Fill in:
     - **Owner**: `TakanariShimbo` (your GitHub username/org)
     - **Repository**: `rosbridge-mcp-server`
     - **Workflow name**: `pypi-publish.yml`
     - **Environment**: `pypi` (optional but recommended)
   - Click "Add"

### 2. Configure GitHub Environment (Recommended)

1. **Navigate to Repository Settings**

   - Go to your GitHub repository
   - Click "Settings" → "Environments"

2. **Create PyPI Environment**
   - Click "New environment"
   - Name: `pypi`
   - Configure protection rules (optional):
     - Add required reviewers
     - Restrict to specific branches/tags

### 3. Setup GitHub Personal Access Token (for release script)

The release script needs to push to GitHub, so you'll need a GitHub token:

1. **Create GitHub Personal Access Token**

   - Go to https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Set expiration (recommended: 90 days or custom)
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
   - Click "Generate token"
   - Copy the generated token (starts with `ghp_`)

2. **Configure Git with Token**

   ```bash
   # Option 1: Use GitHub CLI (recommended)
   gh auth login

   # Option 2: Configure git to use token
   git config --global credential.helper store
   # Then when prompted for password, use your token instead
   ```

### 4. Release New Version

Use the release script to automatically version, tag, and trigger publishing:

```bash
# First time setup
chmod +x scripts/release.sh

# Increment patch version (0.1.0 → 0.1.1)
./scripts/release.sh patch

# Increment minor version (0.1.0 → 0.2.0)
./scripts/release.sh minor

# Increment major version (0.1.0 → 1.0.0)
./scripts/release.sh major

# Set specific version
./scripts/release.sh 1.2.3
```

### 5. Verify Publication

1. **Check GitHub Actions**

   - Go to "Actions" tab in your repository
   - Verify the "Publish to PyPI" workflow completed successfully

2. **Verify PyPI Package**
   - Visit: https://pypi.org/project/rosbridge-mcp-server/
   - Or run: `pip show rosbridge-mcp-server`

### Release Process Flow

1. `release.sh` script updates version in all files
2. Creates git commit and tag
3. Pushes to GitHub
4. GitHub Actions workflow triggers on new tag
5. Workflow uses OIDC to authenticate with PyPI (no tokens needed!)
6. Workflow builds project and publishes to PyPI
7. Package becomes available globally via `pip install` or `uvx`

## Code Quality

This project uses `ruff` for linting and formatting:

```bash
# Run linter
uv run ruff check

# Fix linting issues
uv run ruff check --fix

# Format code
uv run ruff format
```

## Project Structure

```
rosbridge-mcp-server/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── __main__.py              # Main entry point
│   ├── server.py                # Server implementation
│   └── tools/                   # Tool implementations
│       ├── __init__.py          # Tools module initialization
│       ├── list_topics.py       # List topics tool
│       ├── list_actions.py      # List actions tool
│       ├── list_services.py     # List services tool
│       ├── get_topic_info.py    # Get topic info tool
│       ├── publish_topic.py     # Publish topic tool
│       ├── publish_action.py    # Publish action tool
│       ├── publish_service.py   # Publish service tool
│       └── cancel_action.py     # Cancel action tool
├── pyproject.toml               # Project configuration
├── uv.lock                      # Dependency lock file
├── .github/
│   └── workflows/
│       └── pypi-publish.yml     # PyPI publish workflow with Trusted Publishers
├── scripts/
│   └── release.sh               # Release automation script
├── docs/
│   ├── README.md                # English documentation
│   └── README_ja.md             # Japanese documentation
└── .gitignore                   # Git ignore file
```

## License

MIT
