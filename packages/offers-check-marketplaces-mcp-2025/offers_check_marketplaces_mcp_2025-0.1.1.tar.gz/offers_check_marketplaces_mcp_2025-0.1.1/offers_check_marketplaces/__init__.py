"""
Offers Check Marketplaces MCP package.

This package provides an MCP (Model Context Protocol) server for automated 
product search and price comparison across multiple marketplaces.
It integrates with MCP Playwright for web scraping capabilities and processes 
Excel data to generate comprehensive price comparison reports.
"""

from offers_check_marketplaces.server import mcp, main, run_stdio, run_sse

__version__ = "0.1.0"
__all__ = ["mcp", "main", "run_stdio", "run_sse"]