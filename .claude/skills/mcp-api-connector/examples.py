"""
Example usage of the MCP API Connector Skill

This file demonstrates various ways to use the skill to interact
with external APIs and MCP servers.
"""

from impl import MCPAPIConnector, QueryRequest, QueryResponse
import json


def example_github_repo_info():
    """Example: Get GitHub repository information"""
    print("\n" + "=" * 60)
    print("Example 1: Get GitHub Repository Information")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    query = QueryRequest(
        connector_name="github",
        resource_type="repository",
        endpoint="/repos/anthropics/anthropic-sdk-python"
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully fetched repository data")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")


def example_github_issues():
    """Example: List GitHub issues"""
    print("\n" + "=" * 60)
    print("Example 2: List GitHub Issues")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    query = QueryRequest(
        connector_name="github",
        resource_type="issues",
        endpoint="/repos/microsoft/vscode/issues",
        params={
            "state": "open",
            "labels": "bug",
            "per_page": 5
        }
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully fetched issues")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")


def example_github_search():
    """Example: Search GitHub repositories"""
    print("\n" + "=" * 60)
    print("Example 3: Search GitHub Repositories")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    query = QueryRequest(
        connector_name="github",
        resource_type="search",
        endpoint="/search/repositories",
        params={
            "q": "language:python stars:>10000",
            "sort": "stars",
            "per_page": 5
        }
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully searched repositories")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")


def example_github_user():
    """Example: Get GitHub user information"""
    print("\n" + "=" * 60)
    print("Example 4: Get GitHub User Information")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    query = QueryRequest(
        connector_name="github",
        resource_type="user",
        endpoint="/users/torvalds"
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully fetched user data")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")


def example_figma_file():
    """Example: Get Figma design file (requires FIGMA_TOKEN)"""
    print("\n" + "=" * 60)
    print("Example 5: Get Figma Design File")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'figma': {'enabled': True}
        }
    })

    # Note: Replace FILE_KEY with an actual Figma file key
    query = QueryRequest(
        connector_name="figma",
        resource_type="file",
        endpoint="/files/FILE_KEY"
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully fetched Figma file")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")
        print("Note: Make sure FIGMA_TOKEN is set and FILE_KEY is valid")


def example_linear_graphql():
    """Example: Query Linear issues via GraphQL (requires LINEAR_TOKEN)"""
    print("\n" + "=" * 60)
    print("Example 6: Query Linear Issues (GraphQL)")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'linear': {'enabled': True}
        }
    })

    query = QueryRequest(
        connector_name="linear",
        resource_type="issues",
        endpoint="""
            query {
                issues(first: 5) {
                    nodes {
                        id
                        title
                        description
                        state { name }
                        priority
                        createdAt
                    }
                }
            }
        """,
        method="POST"
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully queried Linear issues")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")
        print("Note: Make sure LINEAR_TOKEN is set in .env")


def example_slack_channels():
    """Example: List Slack channels (requires SLACK_TOKEN)"""
    print("\n" + "=" * 60)
    print("Example 7: List Slack Channels")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'slack': {'enabled': True}
        }
    })

    query = QueryRequest(
        connector_name="slack",
        resource_type="channels",
        endpoint="/conversations.list",
        params={
            "types": "public_channel",
            "limit": 10
        }
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Successfully fetched Slack channels")
        print(response.to_context())
    else:
        print(f"\n✗ Error: {response.error}")
        print("Note: Make sure SLACK_TOKEN is set in .env")


def example_multiple_queries():
    """Example: Execute multiple queries in sequence"""
    print("\n" + "=" * 60)
    print("Example 8: Multiple Queries - GitHub Repo Analysis")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    repo_owner = "anthropics"
    repo_name = "anthropic-sdk-python"

    # Query 1: Get repository info
    print("\n1. Fetching repository information...")
    query1 = QueryRequest(
        connector_name="github",
        resource_type="repository",
        endpoint=f"/repos/{repo_owner}/{repo_name}"
    )
    response1 = skill.execute(query1)

    # Query 2: Get latest releases
    print("2. Fetching latest releases...")
    query2 = QueryRequest(
        connector_name="github",
        resource_type="releases",
        endpoint=f"/repos/{repo_owner}/{repo_name}/releases",
        params={"per_page": 3}
    )
    response2 = skill.execute(query2)

    # Query 3: Get contributors
    print("3. Fetching contributors...")
    query3 = QueryRequest(
        connector_name="github",
        resource_type="contributors",
        endpoint=f"/repos/{repo_owner}/{repo_name}/contributors",
        params={"per_page": 5}
    )
    response3 = skill.execute(query3)

    # Combine results
    print("\n" + "=" * 60)
    print("COMBINED RESULTS")
    print("=" * 60)

    if response1.success:
        print(f"\n{response1.to_context()}\n")

    if response2.success:
        print(f"\n{response2.to_context()}\n")

    if response3.success:
        print(f"\n{response3.to_context()}\n")


def example_error_handling():
    """Example: Demonstrate error handling"""
    print("\n" + "=" * 60)
    print("Example 9: Error Handling")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True}
        }
    })

    # Try to access a non-existent repository
    query = QueryRequest(
        connector_name="github",
        resource_type="repository",
        endpoint="/repos/nonexistent/repository-that-does-not-exist"
    )

    response = skill.execute(query)

    if response.success:
        print("\n✓ Success (unexpected)")
        print(response.to_context())
    else:
        print(f"\n✗ Error (expected): {response.error}")
        print("\nThis demonstrates proper error handling.")


def example_list_connectors():
    """Example: List available connectors"""
    print("\n" + "=" * 60)
    print("Example 10: List Available Connectors")
    print("=" * 60)

    skill = MCPAPIConnector({
        'api_connectors': {
            'github': {'enabled': True},
            'figma': {'enabled': True},
            'slack': {'enabled': False},
            'linear': {'enabled': True}
        }
    })

    connectors = skill.list_connectors()

    print(f"\n✓ Found {len(connectors)} enabled connector(s):")
    for connector in connectors:
        print(f"  - {connector}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MCP API Connector Skill - Examples")
    print("=" * 60)

    examples = [
        ("GitHub Repository Info", example_github_repo_info),
        ("GitHub Issues", example_github_issues),
        ("GitHub Search", example_github_search),
        ("GitHub User", example_github_user),
        ("Multiple Queries", example_multiple_queries),
        ("Error Handling", example_error_handling),
        ("List Connectors", example_list_connectors),
        # Uncomment if you have tokens configured:
        # ("Figma File", example_figma_file),
        # ("Linear GraphQL", example_linear_graphql),
        # ("Slack Channels", example_slack_channels),
    ]

    print("\nNote: Examples requiring authentication tokens are commented out.")
    print("Set tokens in .claude/.env to enable them.\n")

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n✗ Error in '{name}': {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
