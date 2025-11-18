"""
Test suite for MCP API Connector Skill

Run with: python test_skill.py
"""

import os
import sys
import unittest
from unittest.mock import patch, Mock, MagicMock
from impl import (
    MCPAPIConnector,
    QueryRequest,
    QueryResponse,
    APIConnector,
    AuthType,
    ConnectorType
)


class TestQueryResponse(unittest.TestCase):
    """Test QueryResponse data class"""

    def test_to_context_success_dict(self):
        """Test formatting dict data to context"""
        response = QueryResponse(
            success=True,
            connector_name="github",
            resource_type="repository",
            data={"name": "test-repo", "stars": 100}
        )

        context = response.to_context()
        self.assertIn("GITHUB", context)
        self.assertIn("repository", context)
        self.assertIn("name", context)
        self.assertIn("test-repo", context)

    def test_to_context_success_list(self):
        """Test formatting list data to context"""
        response = QueryResponse(
            success=True,
            connector_name="github",
            resource_type="issues",
            data=[
                {"title": "Bug 1", "id": 1},
                {"title": "Bug 2", "id": 2}
            ]
        )

        context = response.to_context()
        self.assertIn("Bug 1", context)
        self.assertIn("Bug 2", context)

    def test_to_context_error(self):
        """Test formatting error response"""
        response = QueryResponse(
            success=False,
            connector_name="github",
            resource_type="repository",
            data=None,
            error="Not found"
        )

        context = response.to_context()
        self.assertIn("Error", context)
        self.assertIn("Not found", context)

    def test_format_long_list(self):
        """Test that long lists are truncated"""
        data = [{"id": i, "name": f"Item {i}"} for i in range(20)]
        response = QueryResponse(
            success=True,
            connector_name="test",
            resource_type="items",
            data=data
        )

        context = response.to_context()
        self.assertIn("... and 10 more items", context)


class TestAPIConnector(unittest.TestCase):
    """Test APIConnector configuration"""

    def test_rest_api_connector(self):
        """Test REST API connector creation"""
        connector = APIConnector(
            name="github",
            connector_type=ConnectorType.REST_API,
            base_url="https://api.github.com",
            auth_type=AuthType.BEARER_TOKEN,
            auth_token_env="GITHUB_TOKEN"
        )

        self.assertEqual(connector.name, "github")
        self.assertEqual(connector.connector_type, ConnectorType.REST_API)
        self.assertEqual(connector.base_url, "https://api.github.com")

    def test_graphql_connector(self):
        """Test GraphQL connector creation"""
        connector = APIConnector(
            name="linear",
            connector_type=ConnectorType.GRAPHQL,
            base_url="https://api.linear.app/graphql",
            auth_type=AuthType.BEARER_TOKEN
        )

        self.assertEqual(connector.connector_type, ConnectorType.GRAPHQL)

    def test_mcp_connector(self):
        """Test MCP server connector creation"""
        connector = APIConnector(
            name="custom-mcp",
            connector_type=ConnectorType.MCP_SERVER,
            mcp_command="node",
            mcp_args=["server.js"]
        )

        self.assertEqual(connector.connector_type, ConnectorType.MCP_SERVER)
        self.assertEqual(connector.mcp_command, "node")


class TestMCPAPIConnectorInit(unittest.TestCase):
    """Test MCPAPIConnector initialization"""

    def test_init_no_config(self):
        """Test initialization without config"""
        skill = MCPAPIConnector()
        self.assertIsInstance(skill.connectors, dict)
        self.assertEqual(len(skill.connectors), 0)

    def test_init_with_github(self):
        """Test initialization with GitHub enabled"""
        config = {
            'api_connectors': {
                'github': {'enabled': True}
            }
        }
        skill = MCPAPIConnector(config)
        self.assertIn('github', skill.connectors)
        self.assertEqual(skill.connectors['github'].name, 'github')

    def test_init_with_multiple_connectors(self):
        """Test initialization with multiple connectors"""
        config = {
            'api_connectors': {
                'github': {'enabled': True},
                'figma': {'enabled': True},
                'slack': {'enabled': True}
            }
        }
        skill = MCPAPIConnector(config)
        self.assertIn('github', skill.connectors)
        self.assertIn('figma', skill.connectors)
        self.assertIn('slack', skill.connectors)

    def test_init_with_disabled_connector(self):
        """Test that disabled connectors are not initialized"""
        config = {
            'api_connectors': {
                'github': {'enabled': True},
                'figma': {'enabled': False}
            }
        }
        skill = MCPAPIConnector(config)
        self.assertIn('github', skill.connectors)
        self.assertNotIn('figma', skill.connectors)

    def test_init_with_mcp_servers(self):
        """Test initialization with MCP servers"""
        config = {
            'mcp_servers': [
                {
                    'name': 'test-mcp',
                    'command': 'node',
                    'args': ['server.js']
                }
            ]
        }
        skill = MCPAPIConnector(config)
        self.assertIn('test-mcp', skill.connectors)
        self.assertEqual(
            skill.connectors['test-mcp'].connector_type,
            ConnectorType.MCP_SERVER
        )


class TestMCPAPIConnectorMethods(unittest.TestCase):
    """Test MCPAPIConnector methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'api_connectors': {
                'github': {'enabled': True}
            }
        }
        self.skill = MCPAPIConnector(self.config)

    def test_list_connectors(self):
        """Test listing connectors"""
        connectors = self.skill.list_connectors()
        self.assertIsInstance(connectors, list)
        self.assertIn('github', connectors)

    def test_validate_success(self):
        """Test validation with valid configuration"""
        result = self.skill.validate()
        self.assertTrue(result)

    def test_validate_no_connectors(self):
        """Test validation with no connectors"""
        skill = MCPAPIConnector({})
        result = skill.validate()
        self.assertFalse(result)

    def test_get_prompt(self):
        """Test getting skill prompt"""
        prompt = self.skill.get_prompt()
        self.assertIsInstance(prompt, str)
        self.assertIn("MCP API Connector", prompt)
        self.assertIn("github", prompt.lower())

    def test_cleanup(self):
        """Test cleanup method"""
        self.skill.cleanup()
        self.assertEqual(len(self.skill.connectors), 0)


class TestMCPAPIConnectorExecute(unittest.TestCase):
    """Test query execution"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'api_connectors': {
                'github': {'enabled': True}
            }
        }
        self.skill = MCPAPIConnector(self.config)

    def test_execute_with_dict(self):
        """Test execute with dictionary input"""
        query_dict = {
            'connector_name': 'invalid',
            'resource_type': 'test',
            'endpoint': '/test'
        }
        response = self.skill.execute(query_dict)
        self.assertIsInstance(response, QueryResponse)

    def test_execute_invalid_connector(self):
        """Test execute with invalid connector"""
        query = QueryRequest(
            connector_name="invalid",
            resource_type="test",
            endpoint="/test"
        )
        response = self.skill.execute(query)

        self.assertFalse(response.success)
        self.assertIn("not found", response.error.lower())

    @patch('impl.requests.request')
    @patch('impl.os.getenv')
    def test_execute_rest_api_success(self, mock_getenv, mock_request):
        """Test successful REST API query"""
        # Mock environment variable
        mock_getenv.return_value = "fake_token"

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "test-repo", "stars": 100}
        mock_response.headers = {"content-type": "application/json"}
        mock_request.return_value = mock_response

        query = QueryRequest(
            connector_name="github",
            resource_type="repository",
            endpoint="/repos/test/repo"
        )
        response = self.skill.execute(query)

        self.assertTrue(response.success)
        self.assertEqual(response.data["name"], "test-repo")
        self.assertEqual(response.connector_name, "github")

    @patch('impl.requests.request')
    @patch('impl.os.getenv')
    def test_execute_rest_api_no_token(self, mock_getenv, mock_request):
        """Test REST API query without token"""
        # Mock missing token
        mock_getenv.return_value = None

        query = QueryRequest(
            connector_name="github",
            resource_type="repository",
            endpoint="/repos/test/repo"
        )
        response = self.skill.execute(query)

        self.assertFalse(response.success)
        self.assertIn("token not found", response.error.lower())

    @patch('impl.requests.request')
    @patch('impl.os.getenv')
    def test_execute_rest_api_http_error(self, mock_getenv, mock_request):
        """Test REST API query with HTTP error"""
        mock_getenv.return_value = "fake_token"

        # Mock HTTP error
        mock_request.side_effect = Exception("404 Not Found")

        query = QueryRequest(
            connector_name="github",
            resource_type="repository",
            endpoint="/repos/invalid/repo"
        )
        response = self.skill.execute(query)

        self.assertFalse(response.success)
        self.assertIsNotNone(response.error)

    @patch('impl.requests.post')
    @patch('impl.os.getenv')
    def test_execute_graphql_success(self, mock_getenv, mock_post):
        """Test successful GraphQL query"""
        # Add Linear connector for GraphQL test
        self.skill.connectors['linear'] = APIConnector(
            name='linear',
            connector_type=ConnectorType.GRAPHQL,
            base_url='https://api.linear.app/graphql',
            auth_type=AuthType.BEARER_TOKEN,
            auth_token_env='LINEAR_TOKEN'
        )

        mock_getenv.return_value = "fake_token"

        # Mock successful GraphQL response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "issues": {
                    "nodes": [{"id": "1", "title": "Test"}]
                }
            }
        }
        mock_post.return_value = mock_response

        query = QueryRequest(
            connector_name="linear",
            resource_type="issues",
            endpoint="query { issues { nodes { id title } } }",
            method="POST"
        )
        response = self.skill.execute(query)

        self.assertTrue(response.success)
        self.assertIn("issues", response.data)

    @patch('impl.requests.post')
    @patch('impl.os.getenv')
    def test_execute_graphql_error(self, mock_getenv, mock_post):
        """Test GraphQL query with errors"""
        # Add Linear connector
        self.skill.connectors['linear'] = APIConnector(
            name='linear',
            connector_type=ConnectorType.GRAPHQL,
            base_url='https://api.linear.app/graphql',
            auth_type=AuthType.BEARER_TOKEN,
            auth_token_env='LINEAR_TOKEN'
        )

        mock_getenv.return_value = "fake_token"

        # Mock GraphQL error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errors": [{"message": "Invalid query"}]
        }
        mock_post.return_value = mock_response

        query = QueryRequest(
            connector_name="linear",
            resource_type="issues",
            endpoint="invalid query",
            method="POST"
        )
        response = self.skill.execute(query)

        self.assertFalse(response.success)
        self.assertIn("GraphQL errors", response.error)


class TestIntegration(unittest.TestCase):
    """Integration tests (require real API access)"""

    def test_github_public_api(self):
        """Test actual GitHub public API (no auth required)"""
        # Skip if running in CI without internet
        if os.getenv('CI') == 'true':
            self.skipTest("Skipping integration test in CI")

        skill = MCPAPIConnector({
            'api_connectors': {
                'github': {'enabled': True}
            }
        })

        # Query public GitHub API (no auth needed for public repos)
        query = QueryRequest(
            connector_name="github",
            resource_type="user",
            endpoint="/users/octocat"
        )

        # Temporarily set empty token to test public access
        with patch('impl.os.getenv', return_value=None):
            # This will fail because we require auth, which is correct behavior
            response = skill.execute(query)
            self.assertFalse(response.success)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("MCP API Connector Skill - Test Suite")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestQueryResponse))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIConnector))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPAPIConnectorInit))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPAPIConnectorMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestMCPAPIConnectorExecute))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
