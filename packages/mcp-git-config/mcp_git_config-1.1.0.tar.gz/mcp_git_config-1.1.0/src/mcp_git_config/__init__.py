"""
MCP Git Config Server

A Model Context Protocol server for Git repository detection and username retrieval.

@author: shizeying
@date: 2025-08-04
"""

__version__ = "1.1.0"
__author__ = "shizeying"
__email__ = "w741069229@163.com"

from .server import create_server

__all__ = ["create_server"]
