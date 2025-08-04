"""
CmdRx - AI-powered command line troubleshooting tool.

A command line utility that analyzes CLI command outputs and provides
troubleshooting steps and suggested fixes using AI/LLM services.
"""

__version__ = "0.1.0"
__author__ = "CmdRx Team"
__email__ = "team@cmdrx.dev"

from .core import CmdRxCore
from .config import ConfigManager
from .llm import LLMProvider

__all__ = ["CmdRxCore", "ConfigManager", "LLMProvider"]