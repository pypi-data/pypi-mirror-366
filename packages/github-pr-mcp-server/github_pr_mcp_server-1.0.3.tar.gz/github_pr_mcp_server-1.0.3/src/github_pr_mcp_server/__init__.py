"""
GitHub PR MCP Server - MCP&Agent Challenge

一个基于 Gradio 和 Flask 的 MCP 服务器，支持 GitHub Webhook 处理和 AI 分析。
"""

__version__ = "1.0.0"
__author__ = "MCP&Agent Challenge"
__description__ = "GitHub PR MCP Server - MCP&Agent Challenge"

from .server import GradioMCPServer, FlaskMCPServer
from .core import analyze_code_changes, process_github_pr

__all__ = [
    "GradioMCPServer",
    "FlaskMCPServer", 
    "analyze_code_changes",
    "process_github_pr",
    "__version__",
    "__author__",
    "__description__"
] 