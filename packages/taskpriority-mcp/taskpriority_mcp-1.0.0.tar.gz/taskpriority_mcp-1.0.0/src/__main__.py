#!/usr/bin/env python3
"""
TaskPriority MCP Server - Command line entry point.

This module provides the main entry point for the TaskPriority MCP Server
when run as a module with `python -m src` or `python -m taskpriority_mcp`.
"""

import sys
import argparse
from . import __version__
from .server import main as server_main


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="taskpriority-mcp",
        description="TaskPriority MCP Server - AI-powered task prioritization for Claude Desktop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  TASKPRIORITY_API_KEY      Required. Your TaskPriority API key (must start with tp_live_)
  TASKPRIORITY_API_URL      Optional. API base URL (default: http://localhost:3000)
  LOG_LEVEL                 Optional. Logging level (default: INFO)
  LOG_FORMAT                Optional. Log format: json or text (default: json)

Examples:
  # Run the server
  export TASKPRIORITY_API_KEY=tp_live_your_key_here
  taskpriority-mcp
  
  # Run with custom API URL
  TASKPRIORITY_API_URL=https://api.taskpriority.ai taskpriority-mcp
  
  # Run with debug logging
  LOG_LEVEL=DEBUG taskpriority-mcp

For more information, visit: https://github.com/yourusername/mcp-priority
"""
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"taskpriority-mcp {__version__}",
        help="Show version information and exit"
    )
    
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    return parser


def check_config():
    """Check configuration and exit."""
    try:
        from .config import get_settings
        settings = get_settings()
        print("✅ Configuration is valid!")
        print(f"   API URL: {settings.api_base_url}")
        print(f"   Log Level: {settings.log_level}")
        print(f"   Log Format: {settings.log_format}")
        return 0
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1


def main():
    """Main entry point with argument parsing."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.check_config:
        sys.exit(check_config())
    
    # Run the server
    try:
        server_main()
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()