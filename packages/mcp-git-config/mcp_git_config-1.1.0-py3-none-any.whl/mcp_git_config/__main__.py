"""
MCP Git Config Server Entry Point

Command line entry point for the MCP Git Config Server.

@author: shizeying
@date: 2025-08-04
"""

import argparse
import logging
import sys
from typing import Optional

from .server import create_server


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def run_server() -> None:
    """Run the MCP server."""
    server = create_server()
    
    # FastMCP has its own run method that handles stdio automatically
    try:
        server.run()
    except Exception as e:
        logging.error(f"FastMCP server error: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise


def main(argv: Optional[list] = None) -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="MCP Git Config Server", prog="mcp-git-config"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.1.0")

    args = parser.parse_args(argv)

    # Setup logging
    setup_logging(args.log_level)

    # Run the server
    try:
        run_server()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
