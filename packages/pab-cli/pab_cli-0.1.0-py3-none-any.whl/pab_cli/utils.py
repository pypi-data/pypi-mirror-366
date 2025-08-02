"""
Utility functions for PAB
"""

import sys
from colorama import Fore, Style, init

# Initialize colorama for Windows support
init()


def print_success(message):
    """Print success message in green"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print error message in red"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", file=sys.stderr)


def print_info(message):
    """Print info message in blue"""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def print_warning(message):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW} {message}{Style.RESET_ALL}")


def print_cyan(message):
    """Print normal message in cyan"""
    print(f"{Fore.CYAN} {message}{Style.RESET_ALL}")
