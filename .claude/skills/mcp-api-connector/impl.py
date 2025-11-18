"""
MCP API Connector Skill

Connects to Model Context Protocol (MCP) servers and external APIs
to fetch data from systems like GitHub, Figma, Slack, and more.

Author: Claude Code Framework
Version: 1.0.0
"""

import os
import json
import subprocess
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Third-party imports
try:
    import requests
except ImportError:
    requests = None

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from dotenv import load_dotenv
except ImportError:
    # Fallback: no-op function if dotenv not available
    def load_dotenv(*args, **kwargs):
        pass


class AuthType(Enum):
    """Supported authentication types"""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer"
    OAUTH = "oauth"
    BASIC = "basic"
    NONE = "none"


class ConnectorType(Enum):
    """Types of API connectors"""
    MCP_SERVER = "mcp_server"
    REST_API = "rest_api"
    GRAPHQL = "graphql"


@dataclass
class APIConnector:
    """Configuration for an API connector"""
    name: str
    connector_type: ConnectorType
    base_url: Optional[str] = None
    auth_type: AuthType = AuthType.BEARER_TOKEN
    auth_token_env: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

    # MCP server specific
    mcp_command: Optional[str] = None
    mcp_args: Optional[List[str]] = None
    mcp_env: Optional[Dict[str, str]] = None


@dataclass
class QueryRequest:
    """Request to query an external system"""
    connector_name: str
    resource_type: str  # e.g., "issues", "files", "users"
    endpoint: Optional[str] = None  # REST endpoint or GraphQL query
    params: Optional[Dict[str, Any]] = None
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None


@dataclass
class QueryResponse:
    """Response from external system query"""
    success: bool
    connector_name: str
    resource_type: str
    data: Any
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_context(self) -> str:
        """Translate response into agent context"""
        if not self.success:
            return f"Error querying {self.connector_name}: {self.error}"

        # Format the response for the agent
        context = f"# {self.connector_name.upper()} - {self.resource_type}\n\n"

        if isinstance(self.data, dict):
            context += self._format_dict(self.data)
        elif isinstance(self.data, list):
            context += self._format_list(self.data)
        else:
            context += str(self.data)

        if self.metadata:
            context += f"\n\n## Metadata\n{json.dumps(self.metadata, indent=2)}"

        return context

    def _format_dict(self, data: Dict, indent: int = 0) -> str:
        """Format dictionary data"""
        result = ""
        for key, value in data.items():
            prefix = "  " * indent
            if isinstance(value, (dict, list)):
                result += f"{prefix}**{key}**:\n"
                if isinstance(value, dict):
                    result += self._format_dict(value, indent + 1)
                else:
                    result += self._format_list(value, indent + 1)
            else:
                result += f"{prefix}**{key}**: {value}\n"
        return result

    def _format_list(self, data: List, indent: int = 0) -> str:
        """Format list data"""
        result = ""
        prefix = "  " * indent
        for i, item in enumerate(data[:10]):  # Limit to first 10 items
            if isinstance(item, dict):
                result += f"{prefix}{i + 1}. "
                # Show key fields for common objects
                if "name" in item:
                    result += f"{item.get('name')}"
                if "title" in item:
                    result += f"{item.get('title')}"
                if "id" in item:
                    result += f" (ID: {item.get('id')})"
                result += "\n"
                # Show a few key fields
                for key in ["description", "status", "state", "url", "created_at"][:3]:
                    if key in item:
                        result += f"{prefix}   {key}: {item[key]}\n"
            else:
                result += f"{prefix}- {item}\n"

        if len(data) > 10:
            result += f"{prefix}... and {len(data) - 10} more items\n"

        return result


class MCPAPIConnector:
    """
    Main skill class for MCP and API connector functionality
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MCP API Connector skill

        Args:
            config: Configuration dictionary from .claude/config.json
        """
        self.config = config or {}
        self.connectors: Dict[str, APIConnector] = {}
        self.logger = logging.getLogger(__name__)

        # Load environment variables from .claude/.env
        load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

        # Initialize connectors from config
        self._initialize_connectors()

    def _initialize_connectors(self):
        """Initialize API connectors from configuration"""

        # Common API connectors
        api_configs = self.config.get('api_connectors', {})

        # GitHub
        if api_configs.get('github', {}).get('enabled', False):
            self.connectors['github'] = APIConnector(
                name='github',
                connector_type=ConnectorType.REST_API,
                base_url='https://api.github.com',
                auth_type=AuthType.BEARER_TOKEN,
                auth_token_env='GITHUB_TOKEN',
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'X-GitHub-Api-Version': '2022-11-28'
                }
            )

        # Figma
        if api_configs.get('figma', {}).get('enabled', False):
            self.connectors['figma'] = APIConnector(
                name='figma',
                connector_type=ConnectorType.REST_API,
                base_url='https://api.figma.com/v1',
                auth_type=AuthType.BEARER_TOKEN,
                auth_token_env='FIGMA_TOKEN'
            )

        # Slack
        if api_configs.get('slack', {}).get('enabled', False):
            self.connectors['slack'] = APIConnector(
                name='slack',
                connector_type=ConnectorType.REST_API,
                base_url='https://slack.com/api',
                auth_type=AuthType.BEARER_TOKEN,
                auth_token_env='SLACK_TOKEN'
            )

        # Linear
        if api_configs.get('linear', {}).get('enabled', False):
            self.connectors['linear'] = APIConnector(
                name='linear',
                connector_type=ConnectorType.GRAPHQL,
                base_url='https://api.linear.app/graphql',
                auth_type=AuthType.BEARER_TOKEN,
                auth_token_env='LINEAR_TOKEN'
            )

        # MCP Servers
        mcp_servers = self.config.get('mcp_servers', [])
        for server_config in mcp_servers:
            name = server_config.get('name')
            if name:
                self.connectors[name] = APIConnector(
                    name=name,
                    connector_type=ConnectorType.MCP_SERVER,
                    mcp_command=server_config.get('command'),
                    mcp_args=server_config.get('args', []),
                    mcp_env=server_config.get('env', {})
                )

    def get_prompt(self) -> str:
        """
        Return the skill prompt that explains capabilities to the agent
        """
        enabled_connectors = list(self.connectors.keys())

        prompt = f"""# MCP API Connector Skill

This skill enables you to fetch data from external systems using the Model Context Protocol (MCP) and direct API integrations.

## Available Connectors

{'- ' + chr(10).join(enabled_connectors) if enabled_connectors else 'No connectors configured'}

## Capabilities

1. **Query External Resources**: Fetch data from GitHub, Figma, Slack, Linear, and other systems
2. **MCP Server Integration**: Connect to MCP servers for standardized data access
3. **Authentication**: Securely authenticate with API tokens and OAuth
4. **Response Translation**: Automatically format responses into readable context

## Usage Examples

### Query GitHub Issues
```python
query = QueryRequest(
    connector_name="github",
    resource_type="issues",
    endpoint="/repos/owner/repo/issues",
    params={{"state": "open", "labels": "bug"}}
)
response = execute(query)
print(response.to_context())
```

### Query Figma Files
```python
query = QueryRequest(
    connector_name="figma",
    resource_type="files",
    endpoint="/files/FILE_KEY"
)
response = execute(query)
print(response.to_context())
```

### Query Slack Messages
```python
query = QueryRequest(
    connector_name="slack",
    resource_type="messages",
    endpoint="/conversations.history",
    params={{"channel": "C1234567890"}}
)
response = execute(query)
print(response.to_context())
```

### GraphQL Query (Linear)
```python
query = QueryRequest(
    connector_name="linear",
    resource_type="issues",
    endpoint="query {{ issues {{ nodes {{ title state }} }} }}",
    method="POST"
)
response = execute(query)
print(response.to_context())
```

## Authentication Setup

Set the following environment variables in `.claude/.env`:
- GITHUB_TOKEN - GitHub personal access token
- FIGMA_TOKEN - Figma API token
- SLACK_TOKEN - Slack bot token
- LINEAR_TOKEN - Linear API key

## Configuration

Enable connectors in `.claude/config.json`:
```json
{{
  "skills": [
    {{
      "name": "mcp-api-connector",
      "enabled": true,
      "config": {{
        "api_connectors": {{
          "github": {{"enabled": true}},
          "figma": {{"enabled": true}},
          "slack": {{"enabled": true}},
          "linear": {{"enabled": true}}
        }}
      }}
    }}
  ]
}}
```

Use this skill to fetch external data and integrate it into your agent's context.
"""
        return prompt

    def execute(self, query: Union[QueryRequest, Dict[str, Any]]) -> QueryResponse:
        """
        Execute a query against an external system

        Args:
            query: QueryRequest object or dictionary with query parameters

        Returns:
            QueryResponse with the fetched data
        """
        # Convert dict to QueryRequest if needed
        if isinstance(query, dict):
            query = QueryRequest(**query)

        # Get connector
        connector = self.connectors.get(query.connector_name)
        if not connector:
            return QueryResponse(
                success=False,
                connector_name=query.connector_name,
                resource_type=query.resource_type,
                data=None,
                error=f"Connector '{query.connector_name}' not found or not enabled"
            )

        # Execute based on connector type
        try:
            if connector.connector_type == ConnectorType.MCP_SERVER:
                return self._query_mcp_server(connector, query)
            elif connector.connector_type == ConnectorType.GRAPHQL:
                return self._query_graphql(connector, query)
            else:  # REST_API
                return self._query_rest_api(connector, query)
        except Exception as e:
            self.logger.error(f"Error executing query: {e}", exc_info=True)
            return QueryResponse(
                success=False,
                connector_name=query.connector_name,
                resource_type=query.resource_type,
                data=None,
                error=str(e)
            )

    def _query_rest_api(self, connector: APIConnector, query: QueryRequest) -> QueryResponse:
        """Query a REST API"""
        # Build URL
        url = f"{connector.base_url}{query.endpoint}"

        # Prepare headers
        headers = connector.headers.copy() if connector.headers else {}

        # Add authentication
        if connector.auth_type != AuthType.NONE:
            token = os.getenv(connector.auth_token_env)
            if not token:
                return QueryResponse(
                    success=False,
                    connector_name=connector.name,
                    resource_type=query.resource_type,
                    data=None,
                    error=f"Authentication token not found: {connector.auth_token_env}"
                )

            if connector.auth_type == AuthType.BEARER_TOKEN:
                headers['Authorization'] = f'Bearer {token}'
            elif connector.auth_type == AuthType.API_KEY:
                headers['X-API-Key'] = token

        # Make request
        response = requests.request(
            method=query.method,
            url=url,
            params=query.params,
            json=query.data,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return QueryResponse(
            success=True,
            connector_name=connector.name,
            resource_type=query.resource_type,
            data=response.json(),
            metadata={
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }
        )

    def _query_graphql(self, connector: APIConnector, query: QueryRequest) -> QueryResponse:
        """Query a GraphQL API"""
        # Prepare headers
        headers = connector.headers.copy() if connector.headers else {}
        headers['Content-Type'] = 'application/json'

        # Add authentication
        token = os.getenv(connector.auth_token_env)
        if token:
            headers['Authorization'] = f'Bearer {token}'

        # Prepare GraphQL query
        graphql_query = {
            'query': query.endpoint,
            'variables': query.params or {}
        }

        # Make request
        response = requests.post(
            connector.base_url,
            json=graphql_query,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        # Check for GraphQL errors
        if 'errors' in result:
            return QueryResponse(
                success=False,
                connector_name=connector.name,
                resource_type=query.resource_type,
                data=None,
                error=f"GraphQL errors: {result['errors']}"
            )

        return QueryResponse(
            success=True,
            connector_name=connector.name,
            resource_type=query.resource_type,
            data=result.get('data'),
            metadata={'status_code': response.status_code}
        )

    def _query_mcp_server(self, connector: APIConnector, query: QueryRequest) -> QueryResponse:
        """Query an MCP server via stdio"""
        # Build command
        cmd = [connector.mcp_command] + (connector.mcp_args or [])

        # Prepare environment
        env = os.environ.copy()
        if connector.mcp_env:
            env.update(connector.mcp_env)

        # Build MCP request
        mcp_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'resources/read',
            'params': {
                'uri': query.endpoint,
                'arguments': query.params or {}
            }
        }

        # Execute MCP server
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )

            # Send request and get response
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request),
                timeout=30
            )

            if process.returncode != 0:
                return QueryResponse(
                    success=False,
                    connector_name=connector.name,
                    resource_type=query.resource_type,
                    data=None,
                    error=f"MCP server error: {stderr}"
                )

            # Parse response
            response = json.loads(stdout)

            if 'error' in response:
                return QueryResponse(
                    success=False,
                    connector_name=connector.name,
                    resource_type=query.resource_type,
                    data=None,
                    error=f"MCP error: {response['error']}"
                )

            return QueryResponse(
                success=True,
                connector_name=connector.name,
                resource_type=query.resource_type,
                data=response.get('result'),
                metadata={'mcp_version': '2024-11-05'}
            )

        except subprocess.TimeoutExpired:
            process.kill()
            return QueryResponse(
                success=False,
                connector_name=connector.name,
                resource_type=query.resource_type,
                data=None,
                error="MCP server timeout"
            )

    def list_connectors(self) -> List[str]:
        """List all available connectors"""
        return list(self.connectors.keys())

    def validate(self) -> bool:
        """Validate skill configuration"""
        if not self.connectors:
            self.logger.warning("No connectors configured")
            return False

        # Check for required dependencies
        try:
            import requests
            import aiohttp
        except ImportError as e:
            self.logger.error(f"Missing required dependency: {e}")
            return False

        return True

    def cleanup(self):
        """Cleanup resources"""
        self.connectors.clear()


# Convenience functions for direct usage
def create_connector(config: Optional[Dict] = None) -> MCPAPIConnector:
    """Create an MCP API Connector instance"""
    return MCPAPIConnector(config)


def query(connector_name: str, resource_type: str, **kwargs) -> QueryResponse:
    """
    Quick query function

    Args:
        connector_name: Name of the connector (github, figma, etc.)
        resource_type: Type of resource to query
        **kwargs: Additional query parameters

    Returns:
        QueryResponse object
    """
    connector = create_connector()
    request = QueryRequest(
        connector_name=connector_name,
        resource_type=resource_type,
        **kwargs
    )
    return connector.execute(request)


if __name__ == "__main__":
    # Example usage
    print("MCP API Connector Skill")
    print("=" * 50)

    # Create connector
    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    print(f"\nAvailable connectors: {skill.list_connectors()}")
    print("\nSkill initialized successfully!")
    print("\nExample query:")
    print("""
    query = QueryRequest(
        connector_name="github",
        resource_type="repos",
        endpoint="/repos/anthropics/anthropic-sdk-python"
    )
    response = skill.execute(query)
    print(response.to_context())
    """)
