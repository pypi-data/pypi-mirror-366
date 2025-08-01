#!/usr/bin/env python3
"""
NeuraX AI Tool - A powerful CLI and Telegram bot interface for Perplexity AI
Author: Alex Butler [Vritra Security Organization]
Version: 1.0.0
NeuraX is prepared with well-structured comments by Alex for future contributors.
"""

__version__ = "1.0.0"
__author__ = "Alex Butler"
__email__ = "alex@vritrasec.com"
__description__ = "A powerful CLI and Telegram bot interface for Perplexity AI"
__url__ = "https://github.com/VritraSecz/NeuraX"

from .colors import Colors, print_banner
from .config import ConfigManager
from .ai_client import PerplexityAI
from .utils import clear_screen, get_input_with_prompt, print_about, print_connect, print_help, setup_signal_handler

__all__ = [
    'Colors',
    'print_banner',
    'ConfigManager',
    'PerplexityAI',
    'clear_screen',
    'get_input_with_prompt',
    'print_about',
    'print_connect',
    'print_help',
    'setup_signal_handler',
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    '__url__'
]
