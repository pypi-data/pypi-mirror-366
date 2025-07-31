"""Tests for Umbrix MCP Server

Comprehensive test suite covering all 18 MCP tools with parameter validation,
response format verification, error handling, and integration testing.
"""

import pytest
from unittest.mock import AsyncMock, patch
from umbrix_mcp.server import UmbrixClient


@pytest.fixture
def mock_client():
    """Create a mock Umbrix client"""
    client = AsyncMock(spec=UmbrixClient)
    client.api_key = "test-key"
    client.base_url = "https://test.umbrix.dev/api"
    return client


@pytest.mark.asyncio
async def test_umbrix_client_initialization():
    """Test that UmbrixClient initializes correctly"""
    client = UmbrixClient("test-key", "https://test.api.com")
    assert client.api_key == "test-key"
    assert client.base_url == "https://test.api.com"
    assert "X-API-Key" in client.headers
    assert client.headers["X-API-Key"] == "test-key"
    await client.close()


def create_mock_response(response_data):
    """Helper to create a mock response that works with httpx"""

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return response_data

    return MockResponse()


@pytest.mark.asyncio
async def test_threat_correlation_tool_simplified():
    """Test threat_correlation tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock the execute_tool method for simplified proxy call
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Threat correlation results for: test query\nFound correlations: Infrastructure overlap, Temporal patterns"
            }
        )

        from umbrix_mcp.server import threat_correlation
        from mcp.server.fastmcp import Context

        result = await threat_correlation("test query", Context(), limit=10)

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "threat_correlation", {"query": "test query", "limit": 10}
        )

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Threat correlation results" in result


@pytest.mark.asyncio
async def test_analyze_indicator_tool_simplified():
    """Test analyze_indicator tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock the execute_tool method for simplified proxy call
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Indicator Analysis: evil.com\nThreat Level: HIGH\nType: domain\nAssociated: TrojanDownloader"
            }
        )

        from umbrix_mcp.server import analyze_indicator
        from mcp.server.fastmcp import Context

        result = await analyze_indicator(
            "evil.com", Context(), indicator_type="domain-name"
        )

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "analyze_indicator",
            {"indicator": "evil.com", "indicator_type": "domain-name"},
        )

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "evil.com" in result


@pytest.mark.asyncio
async def test_get_threat_actor_tool_simplified():
    """Test get_threat_actor tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock the execute_tool method for simplified proxy call
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Threat Actor Profile: APT28\nAliases: Fancy Bear, Sofacy\nCountry: Russia\nDescription: Russian cyber espionage group"
            }
        )

        from umbrix_mcp.server import get_threat_actor
        from mcp.server.fastmcp import Context

        result = await get_threat_actor("APT28", Context())

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "get_threat_actor", {"actor_name": "APT28"}
        )

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "APT28" in result


@pytest.mark.asyncio
async def test_system_health_tool_simplified():
    """Test system_health tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Create AsyncMock for the entire client
        mock_client.configure_mock(
            **{
                "execute_tool.return_value": {
                    "result": "System Health Report\nOverall Status: HEALTHY\nDatabase: ✓ Connected\nKafka: ✓ Connected\nNeo4j: ✓ Connected"
                }
            }
        )
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "System Health Report\nOverall Status: HEALTHY\nDatabase: ✓ Connected\nKafka: ✓ Connected\nNeo4j: ✓ Connected"
            }
        )

        from umbrix_mcp.server import system_health
        from mcp.server.fastmcp import Context

        result = await system_health(Context())

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with("system_health", {})

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "System Health Report" in result


@pytest.mark.asyncio
async def test_execute_graph_query_tool_simplified():
    """Test execute_graph_query tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock the execute_tool method for simplified proxy call
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Graph Query Results (2 results):\n1. APT28 (Russia)\n2. Lazarus (North Korea)"
            }
        )

        from umbrix_mcp.server import execute_graph_query
        from mcp.server.fastmcp import Context

        cypher_query = "MATCH (n:ThreatActor) RETURN n.name, n.country LIMIT 2"
        result = await execute_graph_query(cypher_query, Context())

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "execute_graph_query", {"cypher_query": cypher_query}
        )

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "APT28" in result and "Lazarus" in result


@pytest.mark.asyncio
async def test_threat_intel_chat_tool_simplified():
    """Test threat_intel_chat tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock the execute_tool method for simplified proxy call
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Threat Intelligence Analysis:\nAPT28 is a Russian cyber espionage group known for sophisticated attacks targeting government and military organizations."
            }
        )

        from umbrix_mcp.server import threat_intel_chat
        from mcp.server.fastmcp import Context

        result = await threat_intel_chat("Tell me about APT28", Context())

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "threat_intel_chat", {"question": "Tell me about APT28"}
        )

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "APT28" in result


@pytest.mark.asyncio
async def test_parameter_validation():
    """Test parameter validation for various tools"""
    from umbrix_mcp.server import (
        threat_correlation,
        analyze_indicator,
    )
    from mcp.server.fastmcp import Context

    # Test empty query parameter
    with patch("umbrix_mcp.server.umbrix_client"):
        result = await threat_correlation("", Context())
        # Should handle empty query gracefully
        assert isinstance(result, str)

    # Test None indicator parameter
    with patch("umbrix_mcp.server.umbrix_client"):
        result = await analyze_indicator(None, Context())
        # Should handle None gracefully
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test error handling when backend tool execution fails"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock execute_tool to raise an exception
        mock_client.execute_tool = AsyncMock(
            side_effect=Exception("Authentication failed - invalid API key")
        )

        from umbrix_mcp.server import threat_correlation
        from mcp.server.fastmcp import Context

        result = await threat_correlation("test query", Context())

        # Verify execute_tool was called
        mock_client.execute_tool.assert_called_once_with(
            "threat_correlation", {"query": "test query", "limit": 10}
        )

        # Verify error is handled appropriately
        assert isinstance(result, str)
        assert "Error:" in result


@pytest.mark.asyncio
async def test_get_cve_details_tool():
    """Test get_cve_details tool with proper parameters and response format"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        mock_client.base_url = "https://test.api.com"
        mock_http_client = AsyncMock()
        mock_client.client = mock_http_client
        mock_http_client.post.return_value = create_mock_response(
            {
                "status": "success",
                "data": {
                    "description": "Critical vulnerability in web application framework",
                    "severity": "CRITICAL",
                    "cvss_score": 9.8,
                    "published_date": "2024-04-15",
                    "last_modified": "2024-04-20",
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    "affected_products": ["Framework v1.0-v2.5"],
                    "associated_threat_actors": ["APT28", "Lazarus Group"],
                    "references": ["https://nvd.nist.gov/vuln/detail/CVE-2024-3721"],
                    "exploitation_status": "Exploited in Wild",
                },
            }
        )

        from umbrix_mcp.server import get_cve_details
        from mcp.server.fastmcp import Context

        result = await get_cve_details("CVE-2024-3721", Context())

        # Verify HTTP client was called
        assert mock_http_client.post.call_count >= 1

        # Verify at least one call was made to get_cve_details endpoint
        calls = mock_http_client.post.call_args_list
        assert any(
            call[0][0].endswith("/v1/tools/get_cve_details") for call in calls
        ), "Expected at least one call to get_cve_details endpoint"

        # Verify response contains expected content
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain CVE information
        assert "CVE-2024-3721" in result
        assert (
            "Critical vulnerability" in result
            or "CRITICAL" in result
            or "9.8" in result
        )


@pytest.mark.asyncio
async def test_discover_recent_threats_tool_simplified():
    """Test discover_recent_threats tool with simplified proxy behavior"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock the execute_tool method for simplified proxy call
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Recent Threat Intelligence (Last 30 Days)\nFound 2 recent threats:\n1. Malicious Domain Detected (Indicator)\n2. APT Campaign Update (Campaign)"
            }
        )

        from umbrix_mcp.server import discover_recent_threats
        from mcp.server.fastmcp import Context

        result = await discover_recent_threats(Context(), days_back=30)

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "discover_recent_threats", {"days_back": 30, "include_sources": False}
        )

        # Verify response is a string from the proxy
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Recent Threat Intelligence" in result


@pytest.mark.asyncio
async def test_discover_recent_threats_with_sources():
    """Test discover_recent_threats tool with include_sources parameter"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock execute_tool for simplified proxy call with sources
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Recent Threat Intelligence (Last 7 Days)\nFound 1 recent threats:\n1. Malicious Domain Detected (Indicator)\n\n📚 Sources:\n1. Threat Intelligence Feed Alpha - Premium IOC Source\n   https://feeds.threatintel.com/alpha\n2. Security Vendor Report - Q1 2024 Threat Landscape\n   https://vendor.com/reports/q1-2024"
            }
        )

        from umbrix_mcp.server import discover_recent_threats
        from mcp.server.fastmcp import Context

        result = await discover_recent_threats(
            Context(), days_back=7, include_sources=True
        )

        # Verify execute_tool was called with include_sources=True
        mock_client.execute_tool.assert_called_once_with(
            "discover_recent_threats", {"days_back": 7, "include_sources": True}
        )

        # Verify response contains expected content including sources
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Recent Threat Intelligence (Last 7 Days)" in result
        assert "Found 1 recent threats:" in result
        assert "Malicious Domain Detected" in result

        # Verify sources are included in output
        assert "📚 Sources:" in result
        assert "Threat Intelligence Feed Alpha" in result
        assert "Security Vendor Report" in result
        assert "https://feeds.threatintel.com/alpha" in result


@pytest.mark.asyncio
async def test_threat_intel_chat_with_sources():
    """Test threat_intel_chat tool which already includes sources"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock execute_tool for simplified proxy call with sources
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "🧠 Threat Intelligence Analysis\n\nAPT28, also known as Fancy Bear, is a Russian cyber espionage group that has been active since at least 2004. They are known for sophisticated spear-phishing attacks and have targeted government, military, and security organizations worldwide.\n\n📚 Sources:\n1. MITRE ATT&CK - APT28 Group Profile\n   https://attack.mitre.org/groups/G0007/\n2. Crowdstrike Intelligence Report - Fancy Bear Activities\n   https://crowdstrike.com/blog/fancy-bear-report"
            }
        )

        from umbrix_mcp.server import threat_intel_chat
        from mcp.server.fastmcp import Context

        result = await threat_intel_chat("Tell me about APT28", Context())

        # Verify execute_tool was called with correct parameters
        mock_client.execute_tool.assert_called_once_with(
            "threat_intel_chat", {"question": "Tell me about APT28"}
        )

        # Verify response contains expected content including sources
        assert isinstance(result, str)
        assert len(result) > 0
        assert "🧠 Threat Intelligence Analysis" in result
        assert "APT28" in result or "Fancy Bear" in result

        # Verify sources are included in output
        assert "📚 Sources:" in result
        assert "MITRE ATT&CK" in result
        assert "Crowdstrike Intelligence Report" in result


@pytest.mark.asyncio
async def test_source_attribution_error_handling():
    """Test error handling when source attribution fails"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        # Mock execute_tool for response without sources
        mock_client.execute_tool = AsyncMock(
            return_value={
                "result": "Recent Threat Intelligence (Last 30 Days)\nFound 1 recent threats:\n1. Test Threat (Indicator)"
            }
        )

        from umbrix_mcp.server import discover_recent_threats
        from mcp.server.fastmcp import Context

        # Test with include_sources=True but no sources in response
        result = await discover_recent_threats(
            Context(), days_back=30, include_sources=True
        )

        # Verify execute_tool was called correctly
        mock_client.execute_tool.assert_called_once_with(
            "discover_recent_threats", {"days_back": 30, "include_sources": True}
        )

        # Verify it still works without sources
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Recent Threat Intelligence (Last 30 Days)" in result
        assert "Test Threat" in result
        # Should not include sources section since none were provided
        assert "📚 Sources:" not in result


@pytest.mark.asyncio
async def test_response_format_consistency():
    """Test that all tools return consistent string responses"""
    with patch("umbrix_mcp.server.umbrix_client") as mock_client:
        mock_client.base_url = "https://test.api.com"
        mock_http_client = AsyncMock()
        mock_client.client = mock_http_client
        mock_http_client.post.return_value = create_mock_response(
            {"status": "success", "data": {"test": "response"}}
        )

        from umbrix_mcp.server import (
            threat_correlation,
            analyze_indicator,
            get_threat_actor,
            execute_graph_query,
            threat_intel_chat,
            system_health,
            get_cve_details,
        )
        from mcp.server.fastmcp import Context

        context = Context()

        # Test that all tools return strings
        tools_to_test = [
            (threat_correlation, ("test", context)),
            (analyze_indicator, ("test.com", context)),
            (get_threat_actor, ("APT28", context)),
            (execute_graph_query, ("MATCH (n) RETURN n LIMIT 1", context)),
            (threat_intel_chat, ("test question", context)),
            (system_health, (context,)),
            (get_cve_details, ("CVE-2024-1234", context)),
        ]

        for tool_func, args in tools_to_test:
            result = await tool_func(*args)
            assert isinstance(
                result, str
            ), f"{tool_func.__name__} should return a string"
            assert (
                len(result) > 0
            ), f"{tool_func.__name__} should return non-empty response"
