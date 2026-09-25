"""
DuckDuckGo Search MCP Server
Provides web, news, and image search tools via the MCP protocol.

Transports:
  - Local dev / stdio MCP client : python server.py
  - Render / HTTP deployment     : PORT env var is set automatically by Render,
                                   uses streamable-http transport on 0.0.0.0
"""

import os
from fastmcp import FastMCP
from duckduckgo_search import DDGS
from typing import Optional

# Initialize the MCP server
mcp = FastMCP(
    name="duckduckgo-search",
    instructions="Search the web using DuckDuckGo. Use search_web for general queries, search_news for latest news, and search_images for image results.",
)


def _run_ddg_search(ddg_callable):
    """Helper to execute a DDGS search and handle errors uniformly."""
    try:
        return ddg_callable()
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def search_web(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    safe_search: str = "moderate",
) -> list[dict]:
    """
    Search the web using DuckDuckGo.

    Args:
        query:        The search query string.
        max_results:  Number of results to return (1–20). Default is 5.
        region:       Region code for results, e.g. 'us-en', 'in-en'. Default is worldwide.
        safe_search:  'on', 'moderate', or 'off'. Default is 'moderate'.

    Returns:
        A list of results, each containing: title, href (URL), body (snippet).
    """
    if not query.strip():
        return [{"error": "Query cannot be empty"}]

    max_results = max(1, min(max_results, 20))

    def _search():
        with DDGS() as ddgs:
            return list(
                ddgs.text(
                    query,
                    region=region,
                    safesearch=safe_search,
                    max_results=max_results,
                )
            )

    result = _run_ddg_search(_search)
    if isinstance(result, dict) and "error" in result:
        return [result]
    return result if result else [{"message": "No results found"}]


@mcp.tool()
def search_news(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    time_filter: Optional[str] = None,
) -> list[dict]:
    """
    Search for latest news articles using DuckDuckGo.

    Args:
        query:        The news search query.
        max_results:  Number of articles to return (1–20). Default is 5.
        region:       Region code, e.g. 'us-en', 'in-en'. Default is worldwide.
        time_filter:  Time range — 'd' (day), 'w' (week), 'm' (month). None for any time.

    Returns:
        A list of news articles, each with: title, url, source, date, body.
    """
    if not query.strip():
        return [{"error": "Query cannot be empty"}]

    max_results = max(1, min(max_results, 20))

    def _search():
        with DDGS() as ddgs:
            return list(
                ddgs.news(
                    query,
                    region=region,
                    safesearch="moderate",
                    timelimit=time_filter,
                    max_results=max_results,
                )
            )

    result = _run_ddg_search(_search)
    if isinstance(result, dict) and "error" in result:
        return [result]
    return result if result else [{"message": "No news articles found"}]


@mcp.tool()
def search_images(
    query: str,
    max_results: int = 5,
    size: Optional[str] = None,
    color: Optional[str] = None,
) -> list[dict]:
    """
    Search for images using DuckDuckGo.

    Args:
        query:        The image search query.
        max_results:  Number of image results (1–20). Default is 5.
        size:         Filter by size — 'Small', 'Medium', 'Large', 'Wallpaper'. None for any.
        color:        Filter by color — 'color', 'Monochrome', 'Red', 'Blue', etc. None for any.

    Returns:
        A list of image results, each with: title, image (URL), thumbnail, source, url.
    """
    if not query.strip():
        return [{"error": "Query cannot be empty"}]

    max_results = max(1, min(max_results, 20))

    def _search():
        with DDGS() as ddgs:
            return list(
                ddgs.images(
                    query,
                    size=size,
                    color=color,
                    max_results=max_results,
                )
            )

    result = _run_ddg_search(_search)
    if isinstance(result, dict) and "error" in result:
        return [result]
    return result if result else [{"message": "No images found"}]


@mcp.tool()
def search_videos(
    query: str,
    max_results: int = 5,
    duration: Optional[str] = None,
) -> list[dict]:
    """
    Search for videos using DuckDuckGo.

    Args:
        query:        The video search query.
        max_results:  Number of video results (1–20). Default is 5.
        duration:     Filter — 'short' (<5min), 'medium' (5-20min), 'long' (>20min). None for any.

    Returns:
        A list of video results with: title, content (URL), description, publisher, duration, embed_url.
    """
    if not query.strip():
        return [{"error": "Query cannot be empty"}]

    max_results = max(1, min(max_results, 20))

    def _search():
        with DDGS() as ddgs:
            return list(
                ddgs.videos(
                    query,
                    duration=duration,
                    max_results=max_results,
                )
            )

    result = _run_ddg_search(_search)
    if isinstance(result, dict) and "error" in result:
        return [result]
    return result if result else [{"message": "No videos found"}]


if __name__ == "__main__":
    port = os.environ.get("PORT")
    if port:
        # Running on Render (or any cloud): use HTTP transport
        mcp.run(transport="streamable-http", host="0.0.0.0", port=int(port))
    else:
        # Running locally: use stdio (standard MCP client mode)
        mcp.run(transport="stdio")
