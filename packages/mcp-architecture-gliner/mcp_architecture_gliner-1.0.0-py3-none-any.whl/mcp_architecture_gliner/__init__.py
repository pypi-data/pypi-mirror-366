"""
MCP Architecture GLiNER - Architecture-specific entity extraction using GLiNER.

This package provides an MCP (Model Context Protocol) server that performs
intelligent entity extraction from software architecture documents with
TOGAF ADM phase awareness and role-based contextual processing.
"""

__version__ = "1.0.0"
__author__ = "Architecture Team"
__email__ = "architecture@example.com"

from .server import main

__all__ = ["main"]