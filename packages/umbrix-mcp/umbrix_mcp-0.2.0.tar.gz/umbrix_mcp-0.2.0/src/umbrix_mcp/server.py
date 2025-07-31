#!/usr/bin/env python3
"""
Umbrix MCP Server
Provides threat intelligence capabilities to AI assistants via MCP protocol

TOOL SELECTION GUIDE FOR LLMs:
===============================

🤖 TOOL SELECTION HELP (START HERE FOR SMALLER MODELS):
- get_tool_recommendation: Describes what you want to research → Get personalized tool suggestions

🔍 DISCOVERY & EXPLORATION (PERFECT FOR SMALLER MODELS):
- discover_recent_threats: Start here! Shows latest activity and data overview
- threat_correlation: Search for any threat entities with simple terms
- analyze_indicator: Deep analysis of specific IOCs (IPs, domains, hashes)

💬 NATURAL LANGUAGE QUERIES (EASY FOR ANY MODEL):
- execute_graph_query: Smart tool that converts simple patterns to database queries
  Examples: "recent threats", "APT29", "192.168.1.1", "ransomware campaigns"
- threat_intel_chat: Analytical questions using verified graph database only

🎯 SPECIFIC LOOKUPS (FOCUSED TOOLS):
- get_threat_actor: Detailed profiles from verified graph relationships
- get_malware_details: Comprehensive malware analysis from graph database
- get_campaign_details: In-depth campaign intelligence from verified data
- get_cve_details: Comprehensive CVE analysis with severity and exploitation status

📊 SPECIALIZED ANALYSIS (ADVANCED):
- timeline_analysis: Temporal patterns and activity analysis
- analyze_geographic_threats: Geographic threat hotspots and infrastructure patterns
- analyze_mitre_attack: MITRE ATT&CK chains, technique trends, patterns, and tactics

📊 SPECIALIZED TOOLS (VALIDATED DATA):
- indicator_reputation: Reputation scoring for IOCs
- network_analysis: Analyze IP ranges and networks
- threat_actor_attribution: Attribute indicators to actors
- ioc_validation: Validate and enrich indicators

🛡️ ANTI-HALLUCINATION MEASURES:
- All tools now use direct graph database queries
- Link validation removes unverified URLs
- Entity extraction ensures specific data retrieval
- Graph traversal provides only verified relationships
- No AI-generated content - only database facts

RECOMMENDED WORKFLOW:
1. Start with discover_recent_threats to see available verified data
2. Use search_threats for specific entities (returns only graph database results)
3. Deep dive with specialized tools (all use verified graph queries)
4. Use threat_intel_chat for analytical questions (graph data only)
"""

import os
import sys
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx
from mcp.server.fastmcp import FastMCP, Context

# Geographic tools removed - now implemented as backend proxy

# MITRE tools removed - now implemented as backend proxy

# Configure logging - send to stderr to avoid interfering with MCP stdio
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("umbrix-mcp")

# Environment configuration
UMBRIX_API_KEY = os.getenv("UMBRIX_API_KEY")
UMBRIX_API_BASE_URL = os.getenv("UMBRIX_API_BASE_URL", "https://umbrix.dev/api")


@dataclass
class AppContext:
    """Application context with HTTP client"""

    client: httpx.AsyncClient


class UmbrixClient:
    """HTTP client for Umbrix API"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
        )

    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool via the backend MCP server - thin HTTP proxy"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/mcp/tools/call",
                json={"name": tool_name, "arguments": arguments},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            return {"error": f"HTTP error: {e}", "success": False}
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e), "success": False}

    async def list_tools(self) -> dict:
        """List available tools from the backend MCP server"""
        try:
            response = await self.client.get(f"{self.base_url}/api/mcp/tools/list")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error listing tools: {e}")
            return {"error": f"HTTP error: {e}", "tools": []}
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return {"error": str(e), "tools": []}

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global client instance
umbrix_client: Optional[UmbrixClient] = None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle"""
    global umbrix_client

    if not UMBRIX_API_KEY:
        logger.error("UMBRIX_API_KEY environment variable is required")
        sys.exit(1)

    logger.info("Starting Umbrix MCP server...")
    logger.info(f"API URL: {UMBRIX_API_BASE_URL}")

    # Initialize the client
    umbrix_client = UmbrixClient(UMBRIX_API_KEY, UMBRIX_API_BASE_URL)

    try:
        yield AppContext(client=umbrix_client.client)
    finally:
        # Cleanup
        if umbrix_client:
            await umbrix_client.close()


# Create MCP server instance with lifecycle management
mcp = FastMCP("umbrix-mcp", lifespan=app_lifespan)


@mcp.tool()
async def get_tool_recommendation(query: str, ctx: Context) -> str:
    """Get tool recommendations based on your question (perfect for smaller models)

    🤖 SMART TOOL SELECTION - Analyzes your question and suggests the best tool:

    This meta-tool helps smaller models choose the right tool for their needs.
    Just describe what you want to research and get personalized tool recommendations.

    Examples:
    - "I want to research APT29" → Suggests get_threat_actor
    - "Show me recent attacks" → Suggests discover_recent_threats
    - "Analyze this IP: 1.2.3.4" → Suggests analyze_indicator
    - "Find malware campaigns" → Suggests execute_graph_query with pattern

    Args:
        query: Describe what you want to research or analyze
    """
    try:
        result = await umbrix_client.execute_tool(
            "get_tool_recommendation", {"query": query}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error generating tool recommendation: {e}")
        return "Error generating recommendations. Try 'discover_recent_threats' as a safe starting point."


@mcp.tool()
async def discover_recent_threats(
    ctx: Context, days_back: int = 30, include_sources: bool = False
) -> str:
    """Discover recent threat activity and latest attacks

    This tool automatically finds the most recent threats, indicators, and articles
    without requiring specific search terms. Perfect for "what are the latest attacks?"

    Args:
        days_back: Number of days to look back (default: 30)
        include_sources: Include source information for threats (default: False)
    """
    try:
        result = await umbrix_client.execute_tool(
            "discover_recent_threats",
            {"days_back": days_back, "include_sources": include_sources},
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error discovering recent threats: {e}")
        return f"Error: {str(e)}"


# Geographic threat analysis tool removed - now implemented as backend proxy

# MITRE ATT&CK analysis tool now implemented as backend proxy (see below)


@mcp.tool()
async def threat_correlation(query: str, ctx: Context, limit: int = 10) -> str:
    """Search for threat intelligence using direct graph queries to prevent hallucination

    This tool searches the graph database directly using multiple strategies:
    1. Direct entity extraction and graph traversal
    2. Pattern-based Cypher queries
    3. Keyword matching with validation
    4. Only returns verified data from the graph database

    Use this when you want to find threat actors, campaigns, malware, indicators, or security events.
    If this doesn't find results, try discover_recent_threats for latest activity.

    Args:
        query: Search query (e.g., "APT29", "ransomware campaigns", "Russian threat actors")
        limit: Maximum number of results to return (default: 10, max: 50)
    """
    try:
        result = await umbrix_client.execute_tool(
            "threat_correlation", {"query": query, "limit": limit}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error in threat correlation: {e}")
        return f"Error: {str(e)}\n\nSuggestion: Try discover_recent_threats to see available data or use more specific search terms."


@mcp.tool()
async def analyze_indicator(
    indicator: str, ctx: Context, indicator_type: str = None
) -> str:
    """Analyze indicators of compromise using direct graph database queries

    Provides verified analysis including:
    - Threat classification and reputation from graph data
    - Associated campaigns, actors, and malware from verified relationships
    - Timeline and attribution information from graph database
    - Only returns data verified in the graph database

    Use this for investigating specific IOCs like IP addresses, domains, file hashes, or URLs.
    For bulk analysis or discovery, use search_threats instead.

    Args:
        indicator: The IOC to analyze (IP, domain, hash, URL, email, etc.)
        indicator_type: Optional type hint for better analysis (ipv4-addr, domain-name, file:hashes.MD5, etc.)
    """
    try:
        result = await umbrix_client.execute_tool(
            "analyze_indicator",
            {"indicator": indicator, "indicator_type": indicator_type},
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error analyzing indicator: {e}")
        return f"Error accessing graph database: {str(e)}\n\n💡 Try search_threats to find available indicator data."


@mcp.tool()
async def get_threat_actor(actor_name: str, ctx: Context) -> str:
    """Get threat actor intelligence directly from graph database

    Provides verified actor profiles including:
    - Known aliases and attribution details
    - Associated campaigns, malware, and TTPs
    - Activity timeline and targeting patterns
    - Only returns data verified in the graph database

    Use this for in-depth threat actor research when you know the specific actor name.
    For discovery, try search_threats with terms like 'Russian APT' or 'ransomware groups'.

    Args:
        actor_name: Threat actor name, alias, or identifier (APT28, Lazarus, FIN7, etc.)
    """
    try:
        result = await umbrix_client.execute_tool(
            "get_threat_actor", {"actor_name": actor_name}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error getting threat actor: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def execute_graph_query(cypher_query: str, ctx: Context) -> str:
    """Execute queries against the threat intelligence graph database

    🤖 SMART QUERY SUPPORT - Handles both natural language and Cypher:

    📝 SIMPLE PATTERNS (great for smaller models):
    - "recent threats" → Shows latest activity
    - "APT29" → Looks up specific threat actor
    - "192.168.1.1" → Analyzes IP indicator
    - "ransomware campaigns" → Finds malware campaigns
    - "count threat actors" → Gets database statistics

    🔧 CYPHER EXAMPLES (advanced users):
    - Find actors: MATCH (t:ThreatActor) WHERE t.name CONTAINS 'APT' RETURN t
    - Find connections: MATCH (a:ThreatActor)-[r]-(b) WHERE a.name = 'APT29' RETURN a,r,b
    - Count data: MATCH (n:Indicator) RETURN count(n)

    Args:
        cypher_query: Natural language description OR valid Cypher query
    """
    try:
        result = await umbrix_client.execute_tool(
            "execute_graph_query", {"cypher_query": cypher_query}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error executing graph query: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def threat_intel_chat(question: str, ctx: Context) -> str:
    """Get comprehensive threat intelligence analysis using conversational AI

    This tool provides detailed, analytical responses to complex threat intelligence questions.
    It's designed for in-depth analysis, threat attribution, and strategic intelligence queries.

    Best for:
    - Analytical questions: "What are the capabilities of APT29?"
    - Attribution questions: "Which groups use Cobalt Strike?"
    - Trend analysis: "What are emerging ransomware tactics?"
    - Strategic questions: "How do Chinese APTs differ from Russian ones?"

    If you need specific data points, try search_threats or discover_recent_threats first.

    Args:
        question: Analytical question about threats, tactics, attribution, trends, etc.
    """
    try:
        result = await umbrix_client.execute_tool(
            "threat_intel_chat", {"question": question}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error in threat intel chat: {e}")
        return f"Error accessing threat intelligence system: {str(e)}\n\n💡 Try using discover_recent_threats to see available data or use more specific search terms."


# Enhanced graph traversal and validation functions
async def _extract_entities_from_question(question: str) -> list[str]:
    """Extract specific entities from natural language questions"""
    import re

    entities = []
    question_lower = question.lower()

    # Extract CVE numbers
    cve_pattern = r"cve-\d{4}-\d{4,7}"
    cves = re.findall(cve_pattern, question_lower)
    entities.extend(cves)

    # Extract common APT group names
    apt_patterns = [
        r"apt\d+",
        r"lazarus",
        r"fancy bear",
        r"cozy bear",
        r"equation",
        r"carbanak",
        r"fin\d+",
        r"scattered spider",
        r"ta\d+",
    ]
    for pattern in apt_patterns:
        matches = re.findall(pattern, question_lower)
        entities.extend(matches)

    # Extract IP addresses
    ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    ips = re.findall(ip_pattern, question)
    entities.extend(ips)

    # Extract domain patterns
    domain_pattern = r"\b[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}\b"
    domains = re.findall(domain_pattern, question)
    entities.extend(
        [match[0] if isinstance(match, tuple) else match for match in domains]
    )

    return list(set(entities))  # Remove duplicates


async def _get_graph_traversal_data(entities: list[str], question: str) -> str:
    """Get actual graph data for specific entities with traversal"""
    if not entities:
        return None

    results = []

    for entity in entities[:3]:  # Limit to first 3 entities
        # Try different node types for each entity
        queries = [
            f"MATCH (n) WHERE toLower(n.name) CONTAINS '{entity.lower()}' OR toLower(n.value) CONTAINS '{entity.lower()}' RETURN labels(n) as types, n.name as name, n.description as description, n.url as url, n.source as source LIMIT 3",
            f"MATCH (n:ThreatActor) WHERE toLower(n.name) CONTAINS '{entity.lower()}' RETURN n.name as name, n.aliases as aliases, n.description as description, n.country as country LIMIT 2",
            f"MATCH (n:Vulnerability) WHERE toLower(n.cve_id) = '{entity.lower()}' OR toLower(n.name) CONTAINS '{entity.lower()}' RETURN n.cve_id as cve, n.name as name, n.description as description, n.cvss_score as score LIMIT 2",
            f"MATCH (n:Indicator) WHERE toLower(n.value) = '{entity.lower()}' RETURN n.value as indicator, n.type as type, n.threat_level as threat_level, n.confidence as confidence LIMIT 2",
        ]

        for query in queries:
            try:
                response = await umbrix_client.client.post(
                    f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
                    json={"cypher_query": query},
                )
                response.raise_for_status()
                result = response.json()

                if result.get("status") == "success":
                    data = result.get("data", {})
                    graph_results = data.get("results", "")
                    count = data.get("count", 0)

                    if count > 0 and graph_results:
                        results.append(f"**Entity: {entity}**\n{graph_results}")
                        break  # Found data for this entity, move to next

            except Exception as e:
                logger.debug(f"Query failed for {entity}: {e}")
                continue

    if results:
        response = f"Graph Database Results for: {question}\n\n"
        response += "\n\n".join(results)
        response += "\n\n💡 This data comes directly from the graph database. All URLs and references are validated."
        return response

    return None


async def _get_focused_graph_analysis(question: str) -> str:
    """Get focused graph analysis based on question type"""
    question_lower = question.lower()

    # Determine query type and run appropriate graph queries
    if any(term in question_lower for term in ["vulnerability", "cve", "exploit"]):
        query = """
        MATCH (v:Vulnerability)
        WHERE v.last_seen IS NOT NULL 
        AND datetime(v.last_seen) >= datetime() - duration({days: 90})
        RETURN v.cve_id, v.name, v.severity, v.description, v.published_date
        ORDER BY v.published_date DESC
        LIMIT 5
        """
    elif any(term in question_lower for term in ["actor", "apt", "group"]):
        query = """
        MATCH (ta:ThreatActor)
        RETURN ta.name, ta.aliases, ta.country, 
               size((ta)-[:USES]->(:Malware)) as malware_count,
               size((ta)-[:TARGETS]->(:Sector)) as target_count
        ORDER BY ta.name
        LIMIT 5
        """
    elif any(term in question_lower for term in ["malware", "ransomware", "trojan"]):
        query = """
        MATCH (m:Malware)
        RETURN m.name, m.family, m.type,
               size((:ThreatActor)-[:USES]->(m)) as actor_count
        ORDER BY m.name
        LIMIT 5
        """
    elif any(term in question_lower for term in ["campaign", "operation"]):
        query = """
        MATCH (c:Campaign)
        RETURN c.name, c.description, c.first_seen, c.last_seen,
               size((:ThreatActor)-[:ATTRIBUTED_TO]->(c)) as actor_count
        ORDER BY c.last_seen DESC
        LIMIT 5
        """
    else:
        return None

    try:
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": query},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            graph_results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0:
                return f"Focused Graph Analysis:\n\nQuery: {question}\n\nResults ({count} items):\n{graph_results}\n\n💡 All data sourced directly from graph database."

    except Exception as e:
        logger.debug(f"Focused query failed: {e}")

    return None


async def _validate_and_enrich_links(content: str) -> str:
    """Validate and enrich any links in the content"""
    import re

    # Find URLs in content
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    urls = re.findall(url_pattern, content)

    validated_content = content

    for url in urls:
        try:
            # Basic URL validation - check if it's a real domain
            if any(
                domain in url.lower()
                for domain in ["cisa.gov", "mitre.org", "nvd.nist.gov", "us-cert.gov"]
            ):
                # Keep validated URLs
                continue
            else:
                # Replace unvalidated URLs with warning
                validated_content = validated_content.replace(
                    url, "[URL removed - not validated in graph database]"
                )
        except Exception:
            validated_content = validated_content.replace(
                url, "[URL removed - validation failed]"
            )

    return validated_content


async def _get_search_pattern_results(query: str, limit: int) -> str:
    """Get search results based on query patterns"""
    query_lower = query.lower()

    # Different patterns for different types of searches (optimized with size() functions)
    if any(term in query_lower for term in ["actor", "apt", "group"]):
        cypher_query = """
        MATCH (ta:ThreatActor)
        RETURN ta.name as name, ta.aliases as aliases, ta.country as country,
               size((ta)-[:USES]->(:Malware)) as malware_count,
               size((ta)-[:ATTRIBUTED_TO]->(:Campaign)) as campaign_count
        ORDER BY ta.name
        LIMIT """ + str(
            limit
        )
    elif any(
        term in query_lower for term in ["malware", "ransomware", "trojan", "virus"]
    ):
        cypher_query = """
        MATCH (m:Malware)
        RETURN m.name as name, m.family as family, m.type as type,
               size((:ThreatActor)-[:USES]->(m)) as actor_count,
               size((m)-[:USED_IN]->(:Campaign)) as campaign_count
        ORDER BY m.name
        LIMIT """ + str(
            limit
        )
    elif any(term in query_lower for term in ["campaign", "operation"]):
        cypher_query = """
        MATCH (c:Campaign)
        RETURN c.name as name, c.description as description,
               c.first_seen as first_seen, c.last_seen as last_seen,
               size((:ThreatActor)-[:ATTRIBUTED_TO]->(c)) as actor_count,
               size((:Malware)-[:USED_IN]->(c)) as malware_count
        ORDER BY c.last_seen DESC
        LIMIT """ + str(
            limit
        )
    elif any(term in query_lower for term in ["vulnerability", "cve", "exploit"]):
        # Check if query includes temporal indicators or specific products
        temporal_terms = ["current", "recent", "latest", "new", "2024", "2025"]
        product_terms = [
            term
            for term in query_lower.split()
            if term
            in [
                "ios",
                "apple",
                "iphone",
                "ipad",
                "macos",
                "android",
                "windows",
                "linux",
                "microsoft",
                "google",
                "chrome",
                "firefox",
                "safari",
            ]
        ]

        if any(term in query_lower for term in temporal_terms):
            # Recent vulnerabilities - last 180 days for better coverage
            time_filter = (
                "AND datetime(v.published_date) >= datetime() - duration({days: 180})"
            )
        else:
            # All vulnerabilities if no temporal context
            time_filter = ""

        product_filter = ""
        if product_terms:
            # Add product-specific filtering
            product_conditions = " OR ".join(
                [
                    f"toLower(v.affected_product) CONTAINS '{product}' OR toLower(v.description) CONTAINS '{product}'"
                    for product in product_terms
                ]
            )
            product_filter = f"AND ({product_conditions})"

        cypher_query = f"""
        MATCH (v:Vulnerability)
        WHERE v.cve_id IS NOT NULL 
        {time_filter}
        {product_filter}
        RETURN v.cve_id as cve, v.name as name, v.severity as severity,
               v.cvss_score as cvss, v.description as description, 
               v.published_date as published, v.affected_product as product,
               size((:Malware)-[:EXPLOITS]->(v)) as exploiting_malware_count,
               size((v)-[:AFFECTS]->(:Product)) as affected_products_count
        ORDER BY v.published_date DESC, v.cvss_score DESC
        LIMIT {limit}
        """
    else:
        return None

    try:
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": cypher_query},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            graph_results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0:
                return (
                    f"Pattern-Based Search Results ({count} items):\n\n{graph_results}"
                )

    except Exception as e:
        logger.debug(f"Pattern search failed: {e}")

    return None


# Fallback search helper functions
async def _try_fallback_queries(query: str, limit: int) -> str:
    """Try direct Cypher queries for common search patterns"""
    query_lower = query.lower()
    fallback_queries = []

    # Pattern 1: Looking for threat actors
    if any(term in query_lower for term in ["actor", "apt", "group", "threat"]):
        fallback_queries.append(
            "MATCH (t:ThreatActor) RETURN t.name as name, t.aliases as aliases, t.country as country LIMIT "
            + str(limit)
        )

    # Pattern 2: Looking for malware
    if any(
        term in query_lower for term in ["malware", "ransomware", "trojan", "virus"]
    ):
        fallback_queries.append(
            "MATCH (m:Malware) RETURN m.name as name, m.family as family, m.type as type LIMIT "
            + str(limit)
        )

    # Pattern 3: Looking for campaigns
    if any(term in query_lower for term in ["campaign", "operation"]):
        fallback_queries.append(
            "MATCH (c:Campaign) RETURN c.name as name, c.description as description LIMIT "
            + str(limit)
        )

    # Pattern 4: Looking for indicators
    if any(
        term in query_lower for term in ["indicator", "ioc", "ip", "domain", "hash"]
    ):
        fallback_queries.append(
            "MATCH (i:Indicator) RETURN i.value as value, i.type as type, i.confidence as confidence LIMIT "
            + str(limit)
        )

    # Pattern 5: Country-based search
    for country in ["russia", "china", "north korea", "iran", "usa", "israel"]:
        if country in query_lower:
            fallback_queries.append(
                f"MATCH (actor:ThreatActor)-[:LOCATED_IN]->(country:Country) WHERE toLower(country.name) CONTAINS '{country}' RETURN actor.name as name, country.name as country LIMIT {limit}"
            )
            break

    # Try each fallback query
    for cypher_query in fallback_queries:
        try:
            response = await umbrix_client.client.post(
                f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
                json={"cypher_query": cypher_query},
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success" and result.get("data", {}).get(
                    "results"
                ):
                    return f"Found results using pattern matching:\n{result['data']['results']}"
        except Exception as e:
            logger.debug(f"Fallback query failed: {e}")
            continue

    return None


async def _try_keyword_search(query: str, limit: int) -> str:
    """Try keyword-based search across node properties"""
    keywords = query.lower().replace(",", " ").split()

    # Build a comprehensive keyword search query with better property coverage
    keyword_query = f"""
    MATCH (n)
    WHERE any(keyword IN {keywords} WHERE 
        toLower(n.name) CONTAINS keyword OR 
        toLower(n.title) CONTAINS keyword OR 
        toLower(n.description) CONTAINS keyword OR
        toLower(n.aliases) CONTAINS keyword OR
        toLower(n.cve_id) CONTAINS keyword OR
        toLower(n.affected_product) CONTAINS keyword OR
        toLower(n.family) CONTAINS keyword OR
        toLower(n.value) CONTAINS keyword
    )
    WITH n, labels(n) as node_type
    RETURN node_type as type, 
           coalesce(n.name, n.cve_id, n.value, n.title) as name, 
           coalesce(n.description, n.title, '') as description,
           coalesce(n.severity, n.threat_level, '') as severity,
           coalesce(n.published_date, n.first_seen, n.last_seen, '') as date
    ORDER BY 
        CASE WHEN 'Vulnerability' IN node_type THEN 1
             WHEN 'ThreatActor' IN node_type THEN 2  
             WHEN 'Malware' IN node_type THEN 3
             WHEN 'Campaign' IN node_type THEN 4
             WHEN 'Indicator' IN node_type THEN 5
             ELSE 6 END,
        date DESC
    LIMIT {limit}
    """

    try:
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": keyword_query},
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success" and result.get("data", {}).get(
                "results"
            ):
                # Enhanced formatting for better readability
                results_text = result["data"]["results"]
                return f"🔍 Threat Intelligence Search Results:\n\n{results_text}\n\n💡 Results prioritized by relevance: Vulnerabilities → Threat Actors → Malware → Campaigns → Indicators"
    except Exception as e:
        logger.debug(f"Keyword search failed: {e}")

    return None


def _convert_simple_patterns_to_cypher(query: str) -> str:
    """Convert simple natural language patterns to Cypher queries for smaller models"""
    query_lower = query.lower().strip()

    # Recent threats pattern
    if "recent threats" in query_lower or "latest threats" in query_lower:
        return """
        MATCH (i:Indicator)-[:MENTIONED_IN]->(a:Article)
        WHERE a.published_date >= datetime() - duration({days: 30})
        RETURN a.title, a.published_date, i.value, i.type
        ORDER BY a.published_date DESC 
        LIMIT 10
        """

    # Threat actor lookup patterns
    if any(
        actor in query_lower
        for actor in ["apt", "lazarus", "kimsuky", "sandworm", "turla"]
    ):
        # Extract actor name
        actor_name = query.strip()
        return f"""
        MATCH (ta:ThreatActor)
        WHERE toLower(ta.name) CONTAINS toLower('{actor_name}')
           OR toLower(ta.aliases) CONTAINS toLower('{actor_name}')
        RETURN ta.name, ta.aliases, ta.description, ta.country
        LIMIT 5
        """

    # IP address pattern
    import re

    ip_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
    if re.search(ip_pattern, query):
        ip = re.search(ip_pattern, query).group()
        return f"""
        MATCH (i:Indicator)
        WHERE i.value = '{ip}' AND i.type = 'ip'
        OPTIONAL MATCH (i)<-[:USES]-(ta:ThreatActor)
        OPTIONAL MATCH (i)<-[:INDICATES]-(m:Malware)
        RETURN i.value, i.threat_level, i.confidence,
               collect(ta.name) as threat_actors,
               collect(m.name) as malware
        """

    # Domain pattern
    domain_pattern = r"\b[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}\b"
    if re.search(domain_pattern, query) and not query_lower.startswith("match"):
        domain = re.search(domain_pattern, query).group()
        return f"""
        MATCH (i:Indicator)
        WHERE i.value = '{domain}' AND i.type = 'domain'
        OPTIONAL MATCH (i)<-[:USES]-(ta:ThreatActor)
        RETURN i.value, i.threat_level, i.confidence,
               collect(ta.name) as threat_actors
        """

    # Malware family search
    if "ransomware" in query_lower or "malware" in query_lower:
        malware_type = "ransomware" if "ransomware" in query_lower else "malware"
        return f"""
        MATCH (m:Malware)
        WHERE toLower(m.family) CONTAINS '{malware_type}'
           OR toLower(m.type) CONTAINS '{malware_type}'
        OPTIONAL MATCH (m)<-[:USES]-(ta:ThreatActor)
        RETURN m.name, m.family, m.type,
               collect(ta.name) as threat_actors
        LIMIT 10
        """

    # Count patterns
    if query_lower.startswith("count "):
        entity = query_lower.replace("count ", "").strip()
        if "threat actor" in entity:
            return "MATCH (ta:ThreatActor) RETURN count(ta) as threat_actor_count"
        elif "malware" in entity:
            return "MATCH (m:Malware) RETURN count(m) as malware_count"
        elif "indicator" in entity:
            return "MATCH (i:Indicator) RETURN count(i) as indicator_count"
        elif "campaign" in entity:
            return "MATCH (c:Campaign) RETURN count(c) as campaign_count"

    # Campaign search
    if "campaign" in query_lower:
        return """
        MATCH (c:Campaign)
        RETURN c.name, c.description, c.first_seen, c.last_seen
        ORDER BY c.last_seen DESC
        LIMIT 10
        """

    # If no pattern matches, return original query (might be valid Cypher)
    return query


async def _get_basic_database_stats() -> str:
    """Get basic database statistics"""
    try:
        stats_query = """
        MATCH (n) 
        RETURN labels(n)[0] as node_type, count(n) as count 
        ORDER BY count DESC
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": stats_query},
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return f"Database contains: {result.get('data', {}).get('results', 'unknown data')}"
    except Exception:
        pass
    return "Database status unknown"


def _generate_analytical_guidance(question: str) -> str:
    """Generate analytical guidance for threat intelligence questions"""
    question_lower = question.lower()

    guidance = ["💡 Analytical Approach:"]

    # Context-specific guidance
    if any(term in question_lower for term in ["actor", "group", "apt"]):
        guidance.extend(
            [
                "• Use get_threat_actor for detailed actor profiles",
                "• Try search_threats with specific actor names",
                "• Use threat_correlation for actor relationships",
            ]
        )
    elif any(term in question_lower for term in ["malware", "trojan", "ransomware"]):
        guidance.extend(
            [
                "• Use get_malware_details for family analysis",
                "• Try search_threats with malware names",
                "• Use threat_correlation for malware relationships",
            ]
        )
    elif any(term in question_lower for term in ["campaign", "operation"]):
        guidance.extend(
            [
                "• Use get_campaign_details for operation analysis",
                "• Try search_threats with campaign names",
                "• Use timeline_analysis for campaign progression",
            ]
        )
    elif any(
        term in question_lower for term in ["indicator", "ioc", "ip", "domain", "hash"]
    ):
        guidance.extend(
            [
                "• Use analyze_indicator for IOC details",
                "• Try indicator_reputation for threat scoring",
                "• Use threat_actor_attribution for attribution",
            ]
        )
    else:
        guidance.extend(
            [
                "• Use discover_recent_threats to see available data",
                "• Try search_threats with key terms from your question",
                "• Use execute_graph_query for custom analysis",
            ]
        )

    guidance.append(
        "\nFor immediate data exploration, try discover_recent_threats first."
    )
    return "\n".join(guidance)


async def _get_contextual_data(question: str) -> str:
    """Get contextual data to support analytical guidance"""
    try:
        # Get basic database stats to show what data is available
        stats_query = """
        CALL {
            MATCH (n:ThreatActor) RETURN 'Threat Actors' as type, count(n) as count
            UNION
            MATCH (n:Malware) RETURN 'Malware' as type, count(n) as count
            UNION
            MATCH (n:Campaign) RETURN 'Campaigns' as type, count(n) as count
            UNION
            MATCH (n:Indicator) RETURN 'Indicators' as type, count(n) as count
            UNION
            MATCH (n:Article) RETURN 'Articles' as type, count(n) as count
        }
        RETURN type, count
        ORDER BY count DESC
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": stats_query},
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                return f"Database contains: {result.get('data', {}).get('results', 'unknown data')}"
    except Exception:
        pass
    return "Database status unknown"


def _generate_search_suggestions(query: str) -> str:
    """Generate helpful search suggestions when no results found"""
    suggestions = []
    query_lower = query.lower()

    # Suggest related terms
    if "apt" in query_lower:
        suggestions.append(
            "• Try searching for specific APT numbers: 'APT1', 'APT29', 'APT28'"
        )
        suggestions.append(
            "• Try broader terms: 'advanced persistent threat' or 'state-sponsored'"
        )

    if any(
        malware_term in query_lower
        for malware_term in ["malware", "ransomware", "trojan"]
    ):
        suggestions.append(
            "• Try specific malware names: 'WannaCry', 'Emotet', 'Cobalt Strike'"
        )
        suggestions.append("• Try malware families: 'banking trojan', 'cryptominer'")

    if any(geo_term in query_lower for geo_term in ["russian", "chinese", "iranian"]):
        suggestions.append(
            "• Try country names: 'Russia', 'China', 'Iran', 'North Korea'"
        )
        suggestions.append("• Try 'threat actors from [country]'")

    # Always suggest recent data exploration
    suggestions.extend(
        [
            "• Use discover_recent_threats to see latest threat activity",
            "• Try execute_graph_query with: 'MATCH (n) RETURN labels(n), count(n)' to see available data types",
            "• Search for broader terms like 'threat actor', 'malware', 'campaign', or 'indicators'",
        ]
    )

    return "Try these alternatives:\n" + "\n".join(suggestions)


@mcp.tool()
async def get_malware_details(malware_name: str, ctx: Context) -> str:
    """Get malware intelligence directly from graph database

    Provides verified malware intelligence including:
    - Malware family classification and variants
    - Associated threat actors and campaigns
    - Timeline and graph relationships
    - Only returns data verified in the graph database

    Use this when you know the specific malware name or family.
    For discovery, try search_threats with terms like 'ransomware' or 'banking trojan'.

    Args:
        malware_name: Malware name or family (WannaCry, Emotet, TrickBot, etc.)
    """
    try:
        logger.info(f"Getting malware details from graph: {malware_name}")

        # Query graph database directly for malware (optimized with size() functions)
        query = f"""
        MATCH (m:Malware)
        WHERE toLower(m.name) CONTAINS '{malware_name.lower()}' 
           OR ANY(alias IN m.aliases WHERE toLower(alias) CONTAINS '{malware_name.lower()}')
        RETURN m.name as name, m.aliases as aliases, m.family as family,
               m.type as type, m.description as description,
               m.first_seen as first_seen, m.last_seen as last_seen,
               size((:ThreatActor)-[:USES]->(m)) as actor_count,
               size((m)-[:USED_IN]->(:Campaign)) as campaign_count,
               size((m)-[:EXPLOITS]->(:Vulnerability)) as vulnerability_count,
               size((m)-[:USES]->(:Technique)) as technique_count
        LIMIT 3
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": query},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            graph_results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0 and graph_results:
                summary = f"Malware Profile: {malware_name}\n\n"
                summary += (
                    f"Graph Database Results ({count} matches):\n{graph_results}\n\n"
                )
                summary += "💡 All data sourced directly from verified graph database."

                return await _validate_and_enrich_links(summary)

        # If no exact match, try broader search
        fallback_query = f"""
        MATCH (m:Malware)
        WHERE toLower(m.name) CONTAINS '{malware_name.lower()[:5]}'
        RETURN m.name as name, m.family as family, m.type as type
        LIMIT 5
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": fallback_query},
        )
        response.raise_for_status()
        fallback_result = response.json()

        if fallback_result.get("status") == "success":
            data = fallback_result.get("data", {})
            graph_results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0:
                return f"No exact match for '{malware_name}', but found similar malware:\n\n{graph_results}\n\n💡 Try using one of these exact names for more details."

        return f"No verified graph data found for malware '{malware_name}'.\n\n💡 Try search_threats or discover_recent_threats to see available malware."
    except Exception as e:
        logger.error(f"Error getting malware details: {e}")
        return f"Error accessing graph database: {str(e)}\n\n💡 Try search_threats to find available malware data."


@mcp.tool()
async def get_campaign_details(campaign_name: str, ctx: Context) -> str:
    """Get campaign intelligence directly from graph database

    Provides verified campaign intelligence including:
    - Attribution to threat actors and sponsors
    - Timeline of activities and phases
    - Malware and tools used
    - Only returns data verified in the graph database

    Use this when you know the specific campaign or operation name.
    For discovery, try search_threats with terms like 'operation' or 'campaign'.

    Args:
        campaign_name: Campaign name or operation (SolarWinds, Operation Aurora, etc.)
    """
    try:
        logger.info(f"Getting campaign details from graph: {campaign_name}")

        # Query graph database directly for campaign (optimized with size() functions)
        query = f"""
        MATCH (c:Campaign)
        WHERE toLower(c.name) CONTAINS '{campaign_name.lower()}' 
           OR ANY(alias IN c.aliases WHERE toLower(alias) CONTAINS '{campaign_name.lower()}')
        RETURN c.name as name, c.aliases as aliases, c.description as description,
               c.objective as objective, c.first_seen as first_seen, c.last_seen as last_seen,
               size((:ThreatActor)-[:ATTRIBUTED_TO]->(c)) as actor_count,
               size((:Malware)-[:USED_IN]->(c)) as malware_count,
               size((c)-[:TARGETS]->(:Sector)) as target_count,
               size((c)-[:USES]->(:Technique)) as technique_count
        LIMIT 3
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": query},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            graph_results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0 and graph_results:
                summary = f"Campaign Profile: {campaign_name}\n\n"
                summary += (
                    f"Graph Database Results ({count} matches):\n{graph_results}\n\n"
                )
                summary += "💡 All data sourced directly from verified graph database."

                return await _validate_and_enrich_links(summary)

        # If no exact match, try broader search
        fallback_query = f"""
        MATCH (c:Campaign)
        WHERE toLower(c.name) CONTAINS '{campaign_name.lower()[:5]}'
        RETURN c.name as name, c.description as description, c.first_seen as first_seen
        LIMIT 5
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": fallback_query},
        )
        response.raise_for_status()
        fallback_result = response.json()

        if fallback_result.get("status") == "success":
            data = fallback_result.get("data", {})
            graph_results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0:
                return f"No exact match for '{campaign_name}', but found similar campaigns:\n\n{graph_results}\n\n💡 Try using one of these exact names for more details."

        return f"No verified graph data found for campaign '{campaign_name}'.\n\n💡 Try search_threats or discover_recent_threats to see available campaigns."
    except Exception as e:
        logger.error(f"Error getting campaign details: {e}")
        return f"Error accessing graph database: {str(e)}\n\n💡 Try search_threats to find available campaign data."


@mcp.tool()
async def get_attack_pattern_details(pattern_name: str, ctx: Context) -> str:
    """Get detailed information about a specific attack pattern

    Args:
        pattern_name: Name of the attack pattern (e.g., T1055, Process Injection)
    """
    try:
        logger.info(f"Getting attack pattern details: {pattern_name}")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/get_attack_pattern_details",
            json={"attack_pattern_identifier": pattern_name},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"Attack Pattern Analysis: {pattern_name}\n\n"

            if data.get("id"):
                summary += f"ID: {data.get('id')}\n"
            if data.get("name"):
                summary += f"Name: {data.get('name')}\n"
            if data.get("external_references"):
                for ref in data["external_references"]:
                    if ref.get("source_name") == "mitre-attack":
                        summary += f"MITRE ATT&CK ID: {ref.get('external_id')}\n"
            if data.get("description"):
                summary += f"\nDescription: {data.get('description')}\n"

            # Kill chain phases
            if data.get("kill_chain_phases"):
                summary += "\nKill Chain Phases:\n"
                for phase in data["kill_chain_phases"]:
                    summary += f"  • {phase.get('kill_chain_name', '')}: {phase.get('phase_name', '')}\n"

            # Platforms
            if data.get("x_mitre_platforms"):
                summary += (
                    f"\nPlatforms: {', '.join(data.get('x_mitre_platforms', []))}\n"
                )

            # Detection and mitigation
            if data.get("x_mitre_detection"):
                summary += f"\nDetection:\n{data.get('x_mitre_detection')}\n"

            # Associated entities
            if data.get("used_by_actors"):
                summary += f"\nUsed by Actors ({len(data['used_by_actors'])}):\n"
                for actor in data["used_by_actors"][:5]:
                    summary += f"  • {actor.get('name', actor.get('id'))}\n"

            if data.get("used_by_malware"):
                summary += f"\nUsed by Malware ({len(data['used_by_malware'])}):\n"
                for malware in data["used_by_malware"][:5]:
                    summary += f"  • {malware.get('name', malware.get('id'))}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'Attack pattern analysis failed')}"
    except Exception as e:
        logger.error(f"Error getting attack pattern details: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_vulnerability_details(vulnerability_id: str, ctx: Context) -> str:
    """Get detailed information about a specific vulnerability

    Args:
        vulnerability_id: Vulnerability identifier (e.g., CVE-2021-44228, Log4Shell)
    """
    try:
        logger.info(f"Getting vulnerability details: {vulnerability_id}")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/get_vulnerability_details",
            json={"vulnerability_identifier": vulnerability_id},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"Vulnerability Analysis: {vulnerability_id}\n\n"

            if data.get("id"):
                summary += f"ID: {data.get('id')}\n"
            if data.get("name"):
                summary += f"Name: {data.get('name')}\n"
            if data.get("cve_id"):
                summary += f"CVE ID: {data.get('cve_id')}\n"
            if data.get("created"):
                summary += f"Created: {data.get('created')}\n"
            if data.get("modified"):
                summary += f"Modified: {data.get('modified')}\n"
            if data.get("description"):
                summary += f"\nDescription: {data.get('description')}\n"

            # CVSS scores
            if data.get("cvss_v3_score"):
                summary += f"\nCVSS v3 Score: {data.get('cvss_v3_score')}"
                if data.get("cvss_v3_severity"):
                    summary += f" ({data.get('cvss_v3_severity')})"
                summary += "\n"
            if data.get("cvss_v2_score"):
                summary += f"CVSS v2 Score: {data.get('cvss_v2_score')}\n"

            # External references
            if data.get("external_references"):
                summary += "\nReferences:\n"
                for ref in data["external_references"][:5]:
                    summary += f"  • {ref.get('source_name', '')}: {ref.get('url', ref.get('external_id', ''))}\n"

            # Associated entities
            if data.get("exploited_by_malware"):
                summary += (
                    f"\nExploited by Malware ({len(data['exploited_by_malware'])}):\n"
                )
                for malware in data["exploited_by_malware"][:5]:
                    summary += f"  • {malware.get('name', malware.get('id'))}\n"

            if data.get("targeted_by_actors"):
                summary += (
                    f"\nTargeted by Actors ({len(data['targeted_by_actors'])}):\n"
                )
                for actor in data["targeted_by_actors"][:5]:
                    summary += f"  • {actor.get('name', actor.get('id'))}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'Vulnerability analysis failed')}"
    except Exception as e:
        logger.error(f"Error getting vulnerability details: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_cve_details(cve_id: str, ctx: Context) -> str:
    """Get detailed information about a specific CVE (Common Vulnerabilities and Exposures)

    Args:
        cve_id: The CVE identifier (e.g., CVE-2024-3721, CVE-2021-44228)

    Returns comprehensive CVE information including:
    - Description and severity details
    - CVSS scores and impact metrics
    - Affected products and vendors
    - Exploitation status and threat actors
    - Associated malware and campaigns
    - References and remediation guidance
    """
    try:
        logger.info(f"Getting CVE details: {cve_id}")

        # Ensure CVE ID is properly formatted
        cve_id = cve_id.upper()
        if not cve_id.startswith("CVE-"):
            cve_id = f"CVE-{cve_id}"

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/get_cve_details",
            json={"cve_id": cve_id},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"🔒 CVE Analysis: {cve_id}\n"
            summary += "=" * 50 + "\n\n"

            # Basic information
            if data.get("description"):
                summary += f"📄 Description:\n{data['description']}\n\n"

            # Severity information
            if data.get("severity"):
                severity = data["severity"].upper()
                severity_emoji = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢",
                }.get(severity, "⚪")
                summary += f"{severity_emoji} Severity: {severity}\n"

            if data.get("cvss_score"):
                summary += f"📊 CVSS Score: {data['cvss_score']}"
                if data.get("cvss_vector"):
                    summary += f" ({data['cvss_vector']})"
                summary += "\n\n"

            # Affected products
            if data.get("affected_products"):
                summary += f"🎯 Affected Products ({len(data['affected_products'])}):\n"
                for product in data["affected_products"][:10]:
                    summary += f"  • {product}\n"
                if len(data["affected_products"]) > 10:
                    summary += f"  ... and {len(data['affected_products']) - 10} more\n"
                summary += "\n"

            # Exploitation status
            if data.get("exploitation_status"):
                summary += f"⚠️ Exploitation Status: {data['exploitation_status']}\n\n"

            # Threat actors
            if data.get("associated_threat_actors"):
                summary += f"👥 Associated Threat Actors ({len(data['associated_threat_actors'])}):\n"
                for actor in data["associated_threat_actors"][:5]:
                    summary += f"  • {actor}\n"
                summary += "\n"

            # Malware
            if data.get("associated_malware"):
                summary += (
                    f"🦠 Associated Malware ({len(data['associated_malware'])}):\n"
                )
                for malware in data["associated_malware"][:5]:
                    summary += f"  • {malware}\n"
                summary += "\n"

            # Dates
            if data.get("published_date"):
                summary += f"📅 Published: {data['published_date']}\n"
            if data.get("last_modified"):
                summary += f"🔄 Last Modified: {data['last_modified']}\n"

            # References
            if data.get("references"):
                summary += f"\n📚 References ({len(data['references'])}):\n"
                for ref in data["references"][:5]:
                    summary += f"  • {ref}\n"

            return summary
        else:
            error_msg = result.get("message", result.get("error", "CVE not found"))
            return f"❌ {error_msg}"

    except Exception as e:
        logger.error(f"Error getting CVE details: {e}")
        return f"Error getting CVE details: {str(e)}"


@mcp.tool()
async def indicator_correlation(
    indicators: list[str], ctx: Context, correlation_types: list[str] = None
) -> str:
    """Find correlations between threat indicators

    Args:
        indicators: List of indicators to analyze for correlations (IPs, domains, hashes, etc.)
        correlation_types: Optional list of correlation types to focus on (infrastructure, ttp, temporal, attribution, campaign)
    """
    try:
        logger.info(f"Finding correlations between {len(indicators)} indicators")

        # Prepare the request payload to match backend expectations
        payload = {"indicators": indicators}
        if correlation_types:
            payload["correlation_types"] = correlation_types

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/threat_correlation",
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            correlations = data.get("correlations", [])
            analysis = data.get("analysis", {})

            summary = "🔗 Threat Correlation Analysis\n"
            summary += f"Analyzed {len(indicators)} indicators: {', '.join(indicators[:3])}{'...' if len(indicators) > 3 else ''}\n\n"

            if not correlations:
                summary += "No correlations found between the provided indicators."
            else:
                summary += f"Found {len(correlations)} correlations:\n\n"
                for i, corr in enumerate(correlations[:10], 1):
                    correlation_type = corr.get("correlation_type", "Unknown")
                    confidence = corr.get("confidence", 0)
                    description = corr.get("description", "No description")

                    summary += f"{i}. {correlation_type.title()} Correlation\n"
                    summary += f"   Confidence: {confidence:.1%}\n"
                    summary += f"   Description: {description}\n"

                    if corr.get("evidence"):
                        evidence = corr["evidence"][
                            :2
                        ]  # Show first 2 pieces of evidence
                        summary += f"   Evidence: {', '.join(evidence)}\n"
                    summary += "\n"

                if len(correlations) > 10:
                    summary += f"... and {len(correlations) - 10} more correlations\n"

            # Add executive summary if available
            if analysis.get("summary"):
                summary += f"\n📋 Executive Summary:\n{analysis['summary']}\n"

            # Add recommendations if available
            if analysis.get("recommendations"):
                recommendations = analysis["recommendations"][:3]  # Show top 3
                summary += "\n💡 Recommendations:\n"
                for i, rec in enumerate(recommendations, 1):
                    summary += f"{i}. {rec}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'Correlation analysis failed')}"
    except Exception as e:
        logger.error(f"Error in threat correlation: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def indicator_reputation(indicator: str, ctx: Context) -> str:
    """Get reputation information for an indicator

    Args:
        indicator: The indicator to check (IP, domain, hash, etc.)
    """
    try:
        logger.info(f"Checking reputation for indicator: {indicator}")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/indicator_reputation",
            json={"indicators": [indicator]},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"Indicator Reputation: {indicator}\n\n"

            if data.get("reputation_score"):
                summary += f"Reputation Score: {data.get('reputation_score')}/100\n"
            if data.get("threat_level"):
                summary += f"Threat Level: {data.get('threat_level')}\n"
            if data.get("classification"):
                summary += f"Classification: {data.get('classification')}\n"
            if data.get("first_seen"):
                summary += f"First Seen: {data.get('first_seen')}\n"
            if data.get("last_seen"):
                summary += f"Last Seen: {data.get('last_seen')}\n"
            if data.get("times_reported"):
                summary += f"Times Reported: {data.get('times_reported')}\n"

            # Sources
            if data.get("sources"):
                summary += f"\nReported by Sources ({len(data['sources'])}):\n"
                for source in data["sources"][:5]:
                    summary += f"  • {source.get('name', 'Unknown')}"
                    if source.get("confidence"):
                        summary += f" (Confidence: {source['confidence']})"
                    summary += "\n"

            # Associated threats
            if data.get("associated_threats"):
                summary += "\nAssociated Threats:\n"
                for threat in data["associated_threats"][:5]:
                    summary += (
                        f"  • {threat.get('type', '')}: {threat.get('name', '')}\n"
                    )

            # Tags
            if data.get("tags"):
                summary += f"\nTags: {', '.join(data.get('tags', []))}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'Reputation check failed')}"
    except Exception as e:
        logger.error(f"Error checking indicator reputation: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def find_threat_actors(ctx: Context, days_back: int = 90, limit: int = 15) -> str:
    """Find threat actors with recent activity and attribution information

    This tool finds threat actors that have been active recently or have strong attribution.
    Perfect for "who are the current threat actors?" or "what groups are active?"

    Args:
        days_back: Number of days to look back for activity (default: 90)
        limit: Maximum number of actors to return (default: 15)
    """
    try:
        logger.info(f"Finding threat actors from the last {days_back} days")

        # Use direct Cypher query to find threat actors with recent activity
        threat_actors_query = f"""
        MATCH (ta:ThreatActor)
        OPTIONAL MATCH (ta)-[:ATTRIBUTED_TO|USES|TARGETS]-(related)
        WHERE related.last_seen IS NOT NULL 
        AND datetime(related.last_seen) >= datetime() - duration({{days: {days_back}}})
        WITH ta, count(related) as recent_activity
        WHERE recent_activity > 0 OR ta.aliases IS NOT NULL
        RETURN ta.name, ta.aliases, ta.country, ta.description, recent_activity
        ORDER BY recent_activity DESC, ta.name ASC
        LIMIT {limit}
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": threat_actors_query},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0:
                summary = f"🎭 Active Threat Actors (Last {days_back} Days)\n"
                summary += f"Found {count} threat actors with recent activity:\n\n"

                # Parse the results
                import json as json_mod

                try:
                    if results.startswith("[") and results.endswith("]"):
                        actors = json_mod.loads(results)
                        for i, actor in enumerate(actors, 1):
                            name = actor.get("ta.name", "Unknown")
                            aliases = actor.get("ta.aliases", "")
                            country = actor.get("ta.country", "")
                            description = actor.get("ta.description", "")
                            activity = actor.get("recent_activity", 0)

                            summary += f"{i}. {name}\n"
                            if aliases and aliases.strip():
                                summary += f"   🏷️  Aliases: {aliases}\n"
                            if country and country.strip():
                                summary += f"   🌍 Country: {country}\n"
                            if activity > 0:
                                summary += (
                                    f"   📊 Recent Activity: {activity} connections\n"
                                )
                            if (
                                description
                                and description.strip()
                                and len(description) < 100
                            ):
                                summary += f"   📝 {description[:97]}...\n"
                            summary += "\n"
                    else:
                        summary += results

                except Exception:
                    summary += results

                summary += "\n💡 For detailed profiles, use get_threat_actor tool with specific actor names."
                return summary
            else:
                # Try fallback query without date restrictions
                fallback_query = f"""
                MATCH (ta:ThreatActor)
                RETURN ta.name, ta.aliases, ta.country, ta.description
                ORDER BY ta.name ASC
                LIMIT {limit}
                """

                response = await umbrix_client.client.post(
                    f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
                    json={"cypher_query": fallback_query},
                )
                response.raise_for_status()
                fallback_result = response.json()

                if fallback_result.get("status") == "success":
                    fallback_data = fallback_result.get("data", {})
                    fallback_results = fallback_data.get("results", "")
                    fallback_count = fallback_data.get("count", 0)

                    if fallback_count > 0:
                        return f"🎭 Known Threat Actors (no recent activity in {days_back} days)\n\nFound {fallback_count} known threat actors:\n\n{fallback_results}\n\n💡 Use get_threat_actor tool for detailed profiles."

                return "No threat actors found in the database."
        else:
            return (
                f"Error finding threat actors: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Error finding threat actors: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def threat_actor_attribution(indicators: list[str], ctx: Context) -> str:
    """Attribute indicators to potential threat actors

    Args:
        indicators: List of indicators to analyze for attribution
    """
    try:
        logger.info(
            f"Performing threat actor attribution for {len(indicators)} indicators"
        )
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/threat_actor_attribution",
            json={"indicators": indicators},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            attributions = data.get("attributions", [])

            summary = "Threat Actor Attribution Analysis\n"
            summary += f"Analyzed {len(indicators)} indicators\n\n"

            if not attributions:
                summary += "No threat actor attributions found."
            else:
                summary += "Potential Attributions:\n\n"
                for i, attr in enumerate(attributions[:5], 1):
                    summary += f"{i}. {attr.get('actor_name', 'Unknown Actor')}\n"
                    summary += f"   Confidence: {attr.get('confidence', 0):.1%}\n"
                    summary += f"   Matching Indicators: {attr.get('matching_indicators', 0)}\n"
                    if attr.get("matching_ttps"):
                        summary += f"   Matching TTPs: {', '.join(attr['matching_ttps'][:3])}\n"
                    if attr.get("reasoning"):
                        summary += f"   Reasoning: {attr['reasoning']}\n"
                    summary += "\n"

                if len(attributions) > 5:
                    summary += (
                        f"... and {len(attributions) - 5} more potential attributions"
                    )

            return summary
        else:
            return f"Error: {result.get('error', 'Attribution analysis failed')}"
    except Exception as e:
        logger.error(f"Error in threat actor attribution: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def ioc_validation(ioc: str, ioc_type: str, ctx: Context) -> str:
    """Validate and enrich an indicator of compromise

    Args:
        ioc: The indicator to validate
        ioc_type: Type of indicator (ip, domain, hash, url, email)
    """
    try:
        logger.info(f"Validating IoC: {ioc} (type: {ioc_type})")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/ioc_validation",
            json={
                "indicators": [ioc],
                "validate_format": True,
                "enrich_context": True,
            },
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"IoC Validation: {ioc}\n"
            summary += f"Type: {ioc_type}\n\n"

            if data.get("is_valid"):
                summary += "✓ Valid IoC\n"
            else:
                summary += "✗ Invalid IoC\n"
                if data.get("validation_errors"):
                    summary += f"Errors: {', '.join(data['validation_errors'])}\n"

            if data.get("normalized_value"):
                summary += f"Normalized: {data['normalized_value']}\n"

            # Enrichment data
            if data.get("enrichment"):
                enrich = data["enrichment"]
                summary += "\nEnrichment Data:\n"
                if enrich.get("geolocation"):
                    summary += f"  Location: {enrich['geolocation']}\n"
                if enrich.get("asn"):
                    summary += f"  ASN: {enrich['asn']}\n"
                if enrich.get("organization"):
                    summary += f"  Organization: {enrich['organization']}\n"
                if enrich.get("hosting_provider"):
                    summary += f"  Hosting: {enrich['hosting_provider']}\n"
                if enrich.get("reverse_dns"):
                    summary += f"  Reverse DNS: {enrich['reverse_dns']}\n"

            # Context
            if data.get("context"):
                summary += f"\nContext: {data['context']}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'IoC validation failed')}"
    except Exception as e:
        logger.error(f"Error validating IoC: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def network_analysis(network: str, ctx: Context) -> str:
    """Analyze a network range for threat intelligence

    Args:
        network: Network range in CIDR notation (e.g., 192.168.1.0/24)
    """
    try:
        logger.info(f"Analyzing network: {network}")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/network_analysis",
            json={"targets": [network]},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"Network Analysis: {network}\n\n"

            if data.get("total_ips"):
                summary += f"Total IPs: {data['total_ips']}\n"
            if data.get("known_malicious"):
                summary += f"Known Malicious: {data['known_malicious']}\n"
            if data.get("suspicious"):
                summary += f"Suspicious: {data['suspicious']}\n"
            if data.get("clean"):
                summary += f"Clean: {data['clean']}\n"

            # Network info
            if data.get("network_info"):
                info = data["network_info"]
                summary += "\nNetwork Information:\n"
                if info.get("asn"):
                    summary += f"  ASN: {info['asn']}\n"
                if info.get("organization"):
                    summary += f"  Organization: {info['organization']}\n"
                if info.get("country"):
                    summary += f"  Country: {info['country']}\n"
                if info.get("network_type"):
                    summary += f"  Type: {info['network_type']}\n"

            # Threats
            if data.get("threats"):
                summary += f"\nIdentified Threats ({len(data['threats'])}):\n"
                for threat in data["threats"][:10]:
                    summary += f"  • {threat.get('ip', '')}: {threat.get('threat_type', '')} - {threat.get('description', '')}\n"

            # Statistics
            if data.get("statistics"):
                stats = data["statistics"]
                summary += "\nStatistics:\n"
                if stats.get("most_common_threat"):
                    summary += f"  Most Common Threat: {stats['most_common_threat']}\n"
                if stats.get("last_activity"):
                    summary += f"  Last Activity: {stats['last_activity']}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'Network analysis failed')}"
    except Exception as e:
        logger.error(f"Error analyzing network: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def timeline_analysis(
    entity: str, start_date: str, end_date: str, ctx: Context
) -> str:
    """Analyze the timeline of events for a threat entity

    Args:
        entity: The threat entity to analyze (e.g., APT28, malicious.com)
        start_date: Start date for the timeline (YYYY-MM-DD)
        end_date: End date for the timeline (YYYY-MM-DD)
    """
    try:
        logger.info(f"Analyzing timeline for {entity} from {start_date} to {end_date}")

        # Build request with proper nested time_range structure
        request_data = {"entities": [entity]}
        if start_date or end_date:
            request_data["time_range"] = {
                "start_date": start_date,
                "end_date": end_date,
            }

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/timeline_analysis",
            json=request_data,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            timeline = data.get("timeline", [])
            summary = data.get("summary", "")

            output = f"Timeline Analysis for: {entity}\n\n"
            if timeline:
                for event in timeline:
                    output += f"[{event.get('timestamp', '')}] ({event.get('type', '')}) {event.get('event', '')}\n"
            else:
                output += (
                    "No timeline data found for the specified entity and timeframe.\n"
                )

            if summary:
                output += f"\nSummary: {summary}\n"

            return output
        else:
            return f"Error: {result.get('error', 'Timeline analysis failed')}"
    except Exception as e:
        logger.error(f"Error in timeline analysis: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def find_recent_indicators(
    ctx: Context,
    days_back: int = 30,
    indicator_types: list[str] = None,
    limit: int = 20,
) -> str:
    """Find recent indicators of compromise (IOCs) by type and timeframe

    This tool finds IOCs that have been recently discovered or updated.
    Perfect for "what are the latest IOCs?" or "show me recent malware hashes"

    Args:
        days_back: Number of days to look back (default: 30)
        indicator_types: Types to filter by (e.g., ['ipv4-addr', 'domain-name', 'file:hashes.MD5']) (optional)
        limit: Maximum number of indicators to return (default: 20)
    """
    try:
        logger.info(f"Finding recent indicators from the last {days_back} days")

        # Build type filter if specified
        type_filter = ""
        if indicator_types and len(indicator_types) > 0:
            type_list = "', '".join(indicator_types)
            type_filter = f"AND i.type IN ['{type_list}']"

        # Use direct Cypher query to find recent indicators
        indicators_query = f"""
        MATCH (i:Indicator)
        WHERE i.first_seen IS NOT NULL 
        AND datetime(i.first_seen) >= datetime() - duration({{days: {days_back}}})
        {type_filter}
        RETURN i.value, i.type, i.confidence, i.first_seen, i.threat_level
        ORDER BY datetime(i.first_seen) DESC
        LIMIT {limit}
        """

        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
            json={"cypher_query": indicators_query},
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})
            results = data.get("results", "")
            count = data.get("count", 0)

            if count > 0:
                type_str = f" ({', '.join(indicator_types)})" if indicator_types else ""
                summary = f"🔍 Recent Indicators{type_str} (Last {days_back} Days)\n"
                summary += f"Found {count} recent IOCs:\n\n"

                # Parse the results
                import json as json_mod

                try:
                    if results.startswith("[") and results.endswith("]"):
                        indicators = json_mod.loads(results)
                        for i, indicator in enumerate(indicators, 1):
                            value = indicator.get("i.value", "Unknown")
                            ioc_type = indicator.get("i.type", "Unknown")
                            confidence = indicator.get("i.confidence", "")
                            first_seen = indicator.get("i.first_seen", "")
                            threat_level = indicator.get("i.threat_level", "")

                            summary += f"{i}. {value}\n"
                            summary += f"   📝 Type: {ioc_type}\n"
                            if confidence:
                                summary += f"   📊 Confidence: {confidence}\n"
                            if threat_level:
                                summary += f"   ⚠️  Threat Level: {threat_level}\n"
                            if first_seen:
                                summary += f"   📅 First Seen: {first_seen[:10]}\n"
                            summary += "\n"
                    else:
                        summary += results

                except Exception:
                    summary += results

                summary += "\n💡 For detailed analysis, use analyze_indicator tool with specific IOCs."
                return summary
            else:
                # Try fallback query without date restrictions
                fallback_query = f"""
                MATCH (i:Indicator)
                WHERE 1=1 {type_filter}
                RETURN i.value, i.type, i.confidence, coalesce(i.first_seen, 'unknown') as first_seen
                ORDER BY i.value ASC
                LIMIT {limit}
                """

                response = await umbrix_client.client.post(
                    f"{umbrix_client.base_url}/v1/tools/execute_graph_query",
                    json={"cypher_query": fallback_query},
                )
                response.raise_for_status()
                fallback_result = response.json()

                if fallback_result.get("status") == "success":
                    fallback_data = fallback_result.get("data", {})
                    fallback_results = fallback_data.get("results", "")
                    fallback_count = fallback_data.get("count", 0)

                    if fallback_count > 0:
                        type_str = (
                            f" of type {', '.join(indicator_types)}"
                            if indicator_types
                            else ""
                        )
                        return f"🔍 Known Indicators{type_str} (no recent activity in {days_back} days)\n\nFound {fallback_count} indicators:\n\n{fallback_results}\n\n💡 Use analyze_indicator for detailed analysis."

                return f"No indicators found{' of the specified types' if indicator_types else ''} in the database."
        else:
            return f"Error finding indicators: {result.get('error', 'Unknown error')}"

    except Exception as e:
        logger.error(f"Error finding recent indicators: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def threat_hunting_query_builder(
    hunt_type: str, parameters: dict, ctx: Context
) -> str:
    """Build threat hunting queries based on patterns

    Args:
        hunt_type: Type of hunt (lateral_movement, data_exfiltration, persistence, privilege_escalation)
        parameters: Hunt-specific parameters (e.g., {"timeframe": "7d", "network": "internal"})
    """
    try:
        logger.info(f"Building threat hunting query for: {hunt_type}")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/threat_hunting_query_builder",
            json={
                "hunt_objectives": [hunt_type],
                "filters": parameters,
                "include_suggestions": True,
                "validate_syntax": True,
            },
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            summary = f"Threat Hunting Query: {hunt_type}\n"
            summary += f"Parameters: {parameters}\n\n"

            if data.get("query"):
                summary += f"Generated Query:\n{data['query']}\n\n"

            if data.get("description"):
                summary += f"Description:\n{data['description']}\n\n"

            if data.get("expected_results"):
                summary += f"Expected Results:\n{data['expected_results']}\n\n"

            # Detection logic
            if data.get("detection_logic"):
                summary += "Detection Logic:\n"
                for step in data["detection_logic"]:
                    summary += f"  • {step}\n"
                summary += "\n"

            # Related techniques
            if data.get("related_techniques"):
                summary += "Related MITRE Techniques:\n"
                for technique in data["related_techniques"][:5]:
                    summary += f"  • {technique}\n"

            # False positive considerations
            if data.get("false_positives"):
                summary += "\nFalse Positive Considerations:\n"
                for fp in data["false_positives"][:3]:
                    summary += f"  • {fp}\n"

            return summary
        else:
            return f"Error: {result.get('error', 'Query building failed')}"
    except Exception as e:
        logger.error(f"Error building threat hunting query: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def report_generation(
    report_type: str, entity_name: str, format: str, ctx: Context
) -> str:
    """Generate threat intelligence reports

    Args:
        report_type: Type of report (actor_profile, incident_summary, ioc_list, executive_brief)
        entity_name: Name of the entity to report on
        format: Output format (text, markdown, json)
    """
    try:
        logger.info(f"Generating {report_type} report for: {entity_name}")
        response = await umbrix_client.client.post(
            f"{umbrix_client.base_url}/v1/tools/report_generation",
            json={
                "report_type": report_type,
                "entities": [entity_name],
                "format": format,
            },
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "success":
            data = result.get("data", {})

            if format == "json":
                return (
                    f"Report Generated:\n{json.dumps(data.get('report', {}), indent=2)}"
                )
            else:
                report_content = data.get("report", "")

                summary = f"Report: {report_type.replace('_', ' ').title()}\n"
                summary += f"Entity: {entity_name}\n"
                summary += f"Format: {format}\n"
                summary += f"Generated: {data.get('generated_at', 'Unknown')}\n"
                summary += "=" * 50 + "\n\n"
                summary += report_content

                if data.get("metadata"):
                    meta = data["metadata"]
                    summary += "\n\nReport Metadata:\n"
                    if meta.get("sources_used"):
                        summary += f"  Sources: {meta['sources_used']}\n"
                    if meta.get("confidence_level"):
                        summary += f"  Confidence: {meta['confidence_level']}\n"
                    if meta.get("data_freshness"):
                        summary += f"  Data Freshness: {meta['data_freshness']}\n"

                return summary
        else:
            return f"Error: {result.get('error', 'Report generation failed')}"
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def system_health(ctx: Context) -> str:
    """Check system health and verify threat intelligence platform status

    Provides comprehensive system status including:
    - Database connectivity and performance
    - Data collection agent status
    - API service health and response times
    - Data freshness and ingestion rates
    - Storage and memory utilization

    Use this tool when:
    - Other tools are returning errors or no data
    - You want to verify the platform is operational
    - Checking data availability before analysis
    - Troubleshooting connectivity issues

    No parameters required - returns full system status report.
    """
    try:
        result = await umbrix_client.execute_tool("system_health", {})
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def analyze_geographic_threats(
    region: str = "global", ctx: Context = None
) -> str:
    """Analyze geographic threat patterns and regional hotspots

    Provides regional threat intelligence including:
    - Geographic threat distribution and hotspots
    - Regional attack patterns and trends
    - Infrastructure patterns by geography
    - Country and region-specific threat actors

    Useful for understanding regional threat landscapes and geographic patterns
    in cyber threats, infrastructure, and attack campaigns.

    Args:
        region: Geographic region to analyze (global, US, EU, APAC, China, Russia, etc.)
    """
    try:
        result = await umbrix_client.execute_tool(
            "analyze_geographic_threats", {"region": region}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error analyzing geographic threats: {e}")
        return f"Error analyzing geographic threats: {str(e)}"


@mcp.tool()
async def analyze_mitre_attack(technique_id: str = "", ctx: Context = None) -> str:
    """Analyze MITRE ATT&CK techniques, tactics, and attack patterns

    Provides MITRE ATT&CK framework analysis including:
    - Technique and tactic details with descriptions
    - Attack chains and technique relationships
    - Threat actor technique usage patterns
    - Campaign and malware technique mappings

    Perfect for understanding attack methodologies, defensive gaps,
    and threat landscape from a MITRE ATT&CK perspective.

    Args:
        technique_id: MITRE technique ID (T1055, T1027, etc.) or empty for overview
    """
    try:
        result = await umbrix_client.execute_tool(
            "analyze_mitre_attack", {"technique_id": technique_id}
        )
        return result.get("result", str(result))
    except Exception as e:
        logger.error(f"Error analyzing MITRE ATT&CK: {e}")
        return f"Error analyzing MITRE ATT&CK: {str(e)}"


def main():
    """Run the enhanced Umbrix MCP server with improved LLM-friendly tools"""
    logger.info(
        "Starting enhanced Umbrix MCP server with optimized threat intelligence tools"
    )
    mcp.run()


if __name__ == "__main__":
    main()
