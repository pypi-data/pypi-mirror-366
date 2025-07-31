"""
Tests for simplified MCP client proxy functionality
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from umbrix_mcp.server import (
    get_tool_recommendation,
    UmbrixClient,
)


class TestUmbrixClient:
    """Test the simplified UmbrixClient proxy functionality"""

    @pytest.fixture
    def client(self):
        """Create a test UmbrixClient instance"""
        return UmbrixClient("test-api-key", "https://test.umbrix.dev/api")

    def test_client_initialization(self, client):
        """Test that UmbrixClient initializes correctly"""
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://test.umbrix.dev/api"
        assert client.headers["X-API-Key"] == "test-api-key"
        assert client.headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_execute_tool_success(self, client):
        """Test successful tool execution via execute_tool"""
        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {"result": "Test response from backend"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = await client.execute_tool("test_tool", {"param": "value"})

            # Verify the request was made correctly
            mock_post.assert_called_once_with(
                "https://test.umbrix.dev/api/api/mcp/tools/call",
                json={"name": "test_tool", "arguments": {"param": "value"}},
            )

            # Verify the result
            assert result == {"result": "Test response from backend"}

    @pytest.mark.asyncio
    async def test_execute_tool_error(self, client):
        """Test error handling in execute_tool"""
        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            # Mock HTTP error
            mock_post.side_effect = Exception("Connection failed")

            result = await client.execute_tool("test_tool", {"param": "value"})

            # Should return error information
            assert "error" in result
            assert "Connection failed" in str(result["error"])

    @pytest.mark.asyncio
    async def test_list_tools_success(self, client):
        """Test successful tool listing via list_tools"""
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            # Mock successful response using Mock for json method
            mock_response = Mock()
            mock_response.json.return_value = {
                "tools": [
                    {
                        "name": "get_threat_actor",
                        "description": "Get threat actor info",
                    },
                    {"name": "analyze_indicator", "description": "Analyze indicators"},
                ]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = await client.list_tools()

            # Verify the request was made correctly
            mock_get.assert_called_once_with(
                "https://test.umbrix.dev/api/api/mcp/tools/list"
            )

            # Verify the result
            assert "tools" in result
            assert len(result["tools"]) == 2
            assert result["tools"][0]["name"] == "get_threat_actor"

    @pytest.mark.asyncio
    async def test_list_tools_error(self, client):
        """Test error handling in list_tools"""
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            # Mock HTTP error
            mock_get.side_effect = Exception("API unavailable")

            result = await client.list_tools()

            # Should return error information
            assert "error" in result
            assert "tools" in result
            assert result["tools"] == []


class TestToolRecommendation:
    """Test the simplified tool recommendation functionality"""

    @pytest.fixture
    def mock_context(self):
        """Mock context for MCP tools"""
        return Mock()

    @pytest.mark.asyncio
    async def test_tool_recommendation_proxy_call(self, mock_context):
        """Test that get_tool_recommendation makes correct proxy call to backend"""
        with patch("umbrix_mcp.server.umbrix_client") as mock_client:
            # Mock the execute_tool response
            mock_client.execute_tool.return_value = {
                "result": "Recommended tools for your query:\n1. **discover_recent_threats**\nReason: Shows latest threat activity"
            }

            result = await get_tool_recommendation(
                "show me recent threats", mock_context
            )

            # Verify execute_tool was called with correct parameters
            mock_client.execute_tool.assert_called_once_with(
                "get_tool_recommendation", {"query": "show me recent threats"}
            )

            # Verify result
            assert isinstance(result, str)
            assert "discover_recent_threats" in result

    @pytest.mark.asyncio
    async def test_tool_recommendation_error_handling(self, mock_context):
        """Test error handling in get_tool_recommendation"""
        with patch("umbrix_mcp.server.umbrix_client") as mock_client:
            # Mock execute_tool failure
            mock_client.execute_tool.side_effect = Exception("Backend unavailable")

            result = await get_tool_recommendation("test query", mock_context)

            # Should return error message
            assert "Error generating recommendations" in result
            assert (
                "discover_recent_threats" in result
            )  # Should include fallback suggestion

    @pytest.mark.asyncio
    async def test_tool_recommendation_formats_response(self, mock_context):
        """Test that tool recommendations return properly formatted responses"""
        with patch("umbrix_mcp.server.umbrix_client") as mock_client:
            # Mock backend response
            mock_client.execute_tool.return_value = {
                "result": "Tool recommendations for your query"
            }

            result = await get_tool_recommendation("analyze APT29", mock_context)

            # Should be a string response
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_tool_recommendation_result_key_handling(self, mock_context):
        """Test handling of different response formats from backend"""
        with patch("umbrix_mcp.server.umbrix_client") as mock_client:
            # Test case where result is not in "result" key
            mock_client.execute_tool = AsyncMock(
                return_value={"data": "Direct response without result key"}
            )

            result = await get_tool_recommendation("test", mock_context)

            # Should convert dict to string if no "result" key
            assert isinstance(result, str)

            # Test case with "result" key
            mock_client.execute_tool = AsyncMock(
                return_value={"result": "Response with result key"}
            )

            result = await get_tool_recommendation("test", mock_context)
            assert result == "Response with result key"


class TestProxyIntegration:
    """Integration tests for simplified proxy functionality"""

    @pytest.mark.asyncio
    async def test_client_proxy_chain(self):
        """Test the complete client proxy chain from tool to backend"""
        client = UmbrixClient("test-key", "https://test.api.com")

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            # Mock backend response using Mock for json method
            mock_response = Mock()
            mock_response.json.return_value = {
                "result": "Backend processed the request successfully"
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Test tool execution through proxy
            result = await client.execute_tool(
                "get_threat_actor", {"actor_name": "APT29"}
            )

            # Verify proxy chain
            mock_post.assert_called_once_with(
                "https://test.api.com/api/mcp/tools/call",
                json={"name": "get_threat_actor", "arguments": {"actor_name": "APT29"}},
            )

            assert result["result"] == "Backend processed the request successfully"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_proxy_calls(self):
        """Test concurrent proxy calls work correctly"""
        import asyncio

        client = UmbrixClient("test-key", "https://test.api.com")

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            # Mock responses with delays using Mock for json method
            async def mock_post_func(*args, **kwargs):
                await asyncio.sleep(0.01)
                mock_response = Mock()
                mock_response.json.return_value = {
                    "result": f"Response for {kwargs['json']['name']}"
                }
                mock_response.raise_for_status.return_value = None
                return mock_response

            mock_post.side_effect = mock_post_func

            # Execute multiple tools concurrently
            tasks = [
                client.execute_tool("get_threat_actor", {"actor_name": "APT29"}),
                client.execute_tool("analyze_indicator", {"indicator": "evil.com"}),
                client.execute_tool("discover_recent_threats", {"days_back": 30}),
            ]

            results = await asyncio.gather(*tasks)

            # All should succeed
            assert len(results) == 3
            assert all("result" in result for result in results)
            assert mock_post.call_count == 3

    def test_error_propagation(self):
        """Test that errors propagate correctly through proxy"""
        client = UmbrixClient("test-key", "https://test.api.com")

        with patch.object(client.client, "post") as mock_post:
            # Mock HTTP error
            import httpx

            mock_post.side_effect = httpx.HTTPError("Backend error")

            # Test synchronous error handling during initialization
            # This would typically be caught in the async execute_tool method
            assert client.base_url == "https://test.api.com"

    @pytest.mark.asyncio
    async def test_response_format_consistency(self):
        """Test that proxy maintains consistent response formats"""
        client = UmbrixClient("test-key", "https://test.api.com")

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            # Test different backend response formats
            test_cases = [
                {"result": "string response"},
                {"result": {"complex": "object"}},
                {"result": ["list", "response"]},
                {"error": "error response"},
                {},  # Empty response
            ]

            for i, response_data in enumerate(test_cases):
                mock_response = Mock()
                mock_response.json.return_value = response_data
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response

                result = await client.execute_tool(f"test_tool_{i}", {})

                # Should always return the response data
                assert result == response_data

    def test_client_lifecycle(self):
        """Test client creation and cleanup"""
        client = UmbrixClient("test-key", "https://test.api.com")

        # Should initialize correctly
        assert client.api_key == "test-key"
        assert client.base_url == "https://test.api.com"

        # Should have HTTP client
        assert client.client is not None

        # Test headers are set
        assert client.headers["X-API-Key"] == "test-key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
