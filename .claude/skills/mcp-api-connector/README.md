# MCP API Connector Skill

A comprehensive skill for Claude Code that enables interaction with the Model Context Protocol (MCP) servers and external API systems like GitHub, Figma, Slack, Linear, and more.

## Overview

This skill provides a unified interface to:
- **Connect to MCP servers** following the Model Context Protocol specification
- **Query REST APIs** from popular services (GitHub, Figma, Slack, etc.)
- **Execute GraphQL queries** for services like Linear
- **Authenticate securely** using various methods (Bearer tokens, API keys, OAuth)
- **Translate responses** into agent-friendly context

## Features

### ✨ Supported Connectors

- **GitHub** - Query repositories, issues, pull requests, users
- **Figma** - Access design files, projects, components
- **Slack** - Read messages, channels, users
- **Linear** - Query issues, projects, teams via GraphQL
- **MCP Servers** - Connect to any MCP-compliant server
- **Custom APIs** - Extensible framework for adding new connectors

### 🔐 Authentication Methods

- Bearer Token (GitHub, Figma, Slack, Linear)
- API Key
- OAuth 2.0
- Basic Authentication

### 🎯 Key Capabilities

1. **Resource Querying** - Fetch data from external systems
2. **Response Translation** - Automatic formatting for agent context
3. **Error Handling** - Robust error handling and reporting
4. **Extensibility** - Easy to add new connectors

## Installation

### 1. Install Dependencies

```bash
cd .claude/skills/mcp-api-connector
pip install -r requirements.txt
```

### 2. Configure Authentication

Copy the example environment file and add your API tokens:

```bash
cp ../../.env.example ../../.env
```

Edit `.claude/.env` and add your tokens:

```bash
GITHUB_TOKEN=ghp_your_github_token
FIGMA_TOKEN=figd_your_figma_token
SLACK_TOKEN=xoxb_your_slack_token
LINEAR_TOKEN=lin_api_your_linear_key
```

### 3. Enable Connectors

Edit `.claude/config.json` to enable the connectors you want:

```json
{
  "skills": [
    {
      "name": "mcp-api-connector",
      "enabled": true,
      "config": {
        "api_connectors": {
          "github": {"enabled": true},
          "figma": {"enabled": true},
          "slack": {"enabled": true},
          "linear": {"enabled": true}
        }
      }
    }
  ]
}
```

## Usage

### Quick Start

```python
from impl import MCPAPIConnector, QueryRequest

# Initialize the skill
skill = MCPAPIConnector()

# Query GitHub repository
query = QueryRequest(
    connector_name="github",
    resource_type="repository",
    endpoint="/repos/anthropics/anthropic-sdk-python"
)

response = skill.execute(query)
print(response.to_context())
```

### GitHub Examples

#### Get Repository Information

```python
query = QueryRequest(
    connector_name="github",
    resource_type="repository",
    endpoint="/repos/owner/repo"
)
response = skill.execute(query)
```

#### List Open Issues

```python
query = QueryRequest(
    connector_name="github",
    resource_type="issues",
    endpoint="/repos/owner/repo/issues",
    params={"state": "open", "labels": "bug"}
)
response = skill.execute(query)
```

#### Get Pull Request

```python
query = QueryRequest(
    connector_name="github",
    resource_type="pull_request",
    endpoint="/repos/owner/repo/pulls/123"
)
response = skill.execute(query)
```

#### Search Repositories

```python
query = QueryRequest(
    connector_name="github",
    resource_type="search",
    endpoint="/search/repositories",
    params={"q": "language:python stars:>1000"}
)
response = skill.execute(query)
```

### Figma Examples

#### Get Design File

```python
query = QueryRequest(
    connector_name="figma",
    resource_type="file",
    endpoint="/files/FILE_KEY"
)
response = skill.execute(query)
```

#### Get Project Files

```python
query = QueryRequest(
    connector_name="figma",
    resource_type="project_files",
    endpoint="/projects/PROJECT_ID/files"
)
response = skill.execute(query)
```

#### Get File Comments

```python
query = QueryRequest(
    connector_name="figma",
    resource_type="comments",
    endpoint="/files/FILE_KEY/comments"
)
response = skill.execute(query)
```

### Slack Examples

#### Get Channel History

```python
query = QueryRequest(
    connector_name="slack",
    resource_type="messages",
    endpoint="/conversations.history",
    params={"channel": "C1234567890", "limit": 10}
)
response = skill.execute(query)
```

#### List Channels

```python
query = QueryRequest(
    connector_name="slack",
    resource_type="channels",
    endpoint="/conversations.list",
    params={"types": "public_channel"}
)
response = skill.execute(query)
```

#### Get User Info

```python
query = QueryRequest(
    connector_name="slack",
    resource_type="user",
    endpoint="/users.info",
    params={"user": "U1234567890"}
)
response = skill.execute(query)
```

### Linear Examples (GraphQL)

#### Query Issues

```python
query = QueryRequest(
    connector_name="linear",
    resource_type="issues",
    endpoint="""
        query {
            issues(first: 10, filter: {state: {name: {eq: "In Progress"}}}) {
                nodes {
                    id
                    title
                    description
                    state { name }
                    assignee { name }
                    createdAt
                }
            }
        }
    """,
    method="POST"
)
response = skill.execute(query)
```

#### Query Projects

```python
query = QueryRequest(
    connector_name="linear",
    resource_type="projects",
    endpoint="""
        query {
            projects {
                nodes {
                    id
                    name
                    description
                    state
                }
            }
        }
    """,
    method="POST"
)
response = skill.execute(query)
```

### MCP Server Examples

#### Configure MCP Server

First, add to `.claude/config.json`:

```json
{
  "mcp_servers": [
    {
      "name": "custom-mcp",
      "command": "node",
      "args": ["/path/to/mcp-server.js"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  ]
}
```

#### Query MCP Server

```python
query = QueryRequest(
    connector_name="custom-mcp",
    resource_type="custom_resource",
    endpoint="resource://custom/data",
    params={"filter": "value"}
)
response = skill.execute(query)
```

## Response Format

Responses are returned as `QueryResponse` objects with:

- **success**: Boolean indicating if the query succeeded
- **connector_name**: Name of the connector used
- **resource_type**: Type of resource queried
- **data**: The actual response data
- **metadata**: Additional information (status codes, headers, etc.)
- **error**: Error message if the query failed

### Convert to Context

Use `to_context()` to format the response for the agent:

```python
response = skill.execute(query)
context = response.to_context()
print(context)
```

Example output:

```markdown
# GITHUB - repository

**name**: anthropic-sdk-python
**description**: Python SDK for Anthropic's Claude API
**stars**: 1234
**language**: Python
**url**: https://github.com/anthropics/anthropic-sdk-python

## Metadata
{
  "status_code": 200
}
```

## Adding Custom Connectors

### 1. Define Connector Configuration

Edit `.claude/config.json`:

```json
{
  "api_connectors": {
    "myapi": {
      "enabled": true,
      "base_url": "https://api.example.com"
    }
  }
}
```

### 2. Update Initialization

Edit `impl.py` to add your connector:

```python
def _initialize_connectors(self):
    # ... existing code ...

    if api_configs.get('myapi', {}).get('enabled', False):
        self.connectors['myapi'] = APIConnector(
            name='myapi',
            connector_type=ConnectorType.REST_API,
            base_url='https://api.example.com',
            auth_type=AuthType.BEARER_TOKEN,
            auth_token_env='MYAPI_TOKEN'
        )
```

### 3. Add Environment Variable

Add to `.claude/.env`:

```bash
MYAPI_TOKEN=your_token_here
```

### 4. Use the Connector

```python
query = QueryRequest(
    connector_name="myapi",
    resource_type="data",
    endpoint="/v1/data"
)
response = skill.execute(query)
```

## Authentication Setup

### GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:user`
4. Copy token to `.claude/.env` as `GITHUB_TOKEN`

### Figma Token

1. Go to https://www.figma.com/developers/api#access-tokens
2. Click "Get personal access token"
3. Copy token to `.claude/.env` as `FIGMA_TOKEN`

### Slack Token

1. Go to https://api.slack.com/apps
2. Create new app or select existing
3. Go to "OAuth & Permissions"
4. Add scopes: `channels:history`, `channels:read`, `users:read`
5. Install app to workspace
6. Copy "Bot User OAuth Token" to `.claude/.env` as `SLACK_TOKEN`

### Linear API Key

1. Go to https://linear.app/settings/api
2. Create new API key
3. Copy key to `.claude/.env` as `LINEAR_TOKEN`

## Troubleshooting

### "Connector not found or not enabled"

- Check that the connector is enabled in `.claude/config.json`
- Verify the connector name matches exactly

### "Authentication token not found"

- Ensure the token is set in `.claude/.env`
- Check the environment variable name matches the connector configuration
- Verify `.env` file is in `.claude/` directory

### "Request failed with status code 401"

- Token may be invalid or expired
- Check token has required permissions/scopes
- Regenerate token if needed

### "Missing required dependency"

- Install dependencies: `pip install -r requirements.txt`
- Activate virtual environment if using one

## API Reference

### QueryRequest

```python
@dataclass
class QueryRequest:
    connector_name: str           # Name of connector (github, figma, etc.)
    resource_type: str            # Type of resource (issues, files, etc.)
    endpoint: Optional[str]       # API endpoint or GraphQL query
    params: Optional[Dict]        # Query parameters
    method: str = "GET"          # HTTP method
    data: Optional[Dict]          # Request body data
```

### QueryResponse

```python
@dataclass
class QueryResponse:
    success: bool                 # Query success status
    connector_name: str           # Connector used
    resource_type: str            # Resource type queried
    data: Any                     # Response data
    metadata: Optional[Dict]      # Additional metadata
    error: Optional[str]          # Error message if failed

    def to_context(self) -> str:  # Format as agent context
        ...
```

### MCPAPIConnector

```python
class MCPAPIConnector:
    def __init__(self, config: Optional[Dict] = None)
    def execute(self, query: QueryRequest) -> QueryResponse
    def list_connectors(self) -> List[str]
    def validate(self) -> bool
    def get_prompt(self) -> str
```

## Architecture

```
┌─────────────────────────────────────────────┐
│         Claude Code Agent                    │
└───────────────┬─────────────────────────────┘
                │
                │ QueryRequest
                ▼
┌─────────────────────────────────────────────┐
│      MCP API Connector Skill                 │
│  ┌─────────────────────────────────────┐    │
│  │  Connection Manager                  │    │
│  ├─────────────────────────────────────┤    │
│  │  - GitHub Connector                  │    │
│  │  - Figma Connector                   │    │
│  │  - Slack Connector                   │    │
│  │  - Linear Connector (GraphQL)        │    │
│  │  - MCP Server Connector              │    │
│  └─────────────────────────────────────┘    │
└───────────────┬─────────────────────────────┘
                │
                │ HTTP/GraphQL/MCP
                ▼
┌─────────────────────────────────────────────┐
│         External Systems                     │
│  ┌────────┐ ┌────────┐ ┌────────┐          │
│  │ GitHub │ │ Figma  │ │ Slack  │ ...      │
│  └────────┘ └────────┘ └────────┘          │
└─────────────────────────────────────────────┘
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new connectors
4. Submit a pull request

## Support

For issues or questions:
- Open an issue on GitHub
- Check the Claude Code documentation
- Review the MCP specification at https://modelcontextprotocol.io

## Changelog

### v1.0.0 (2025-11-18)
- Initial release
- GitHub, Figma, Slack, Linear connectors
- MCP server support
- REST and GraphQL APIs
- Multiple authentication methods
- Response translation
