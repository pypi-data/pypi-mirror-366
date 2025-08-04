"""
MCP Git Config Server Implementation

Main server implementation using FastMCP for Git repository operations.

@author: shizeying
@date: 2025-08-04
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

# Global variable to store current working directory
_current_working_dir: Optional[str] = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Git Config Server")


@mcp.tool(
    name="is_git_repository",
    description="Check if the current directory or specified path is a Git repository",
)
def is_git_repository(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if a directory is a Git repository.

    Args:
        path: Optional path to check. If None, uses current working directory.

    Returns:
        Dict containing:
        - is_git_repo: Boolean indicating if it's a Git repository
        - path: The path that was checked
        - git_dir: Path to .git directory if found
        - error: Error message if any
    """
    try:
        # Use current working directory if no path specified
        if path is None:
            path = _current_working_dir or os.getcwd()

        # Convert to Path object for easier handling
        check_path = Path(path).resolve()

        # Check if path exists
        if not check_path.exists():
            return {
                "is_git_repo": False,
                "path": str(check_path),
                "git_dir": None,
                "error": f"Path does not exist: {check_path}",
            }

        # Check if it's a directory
        if not check_path.is_dir():
            return {
                "is_git_repo": False,
                "path": str(check_path),
                "git_dir": None,
                "error": f"Path is not a directory: {check_path}",
            }

        # Look for .git directory
        git_dir = check_path / ".git"

        # .git can be a directory or a file (in case of worktrees)
        if git_dir.exists():
            return {
                "is_git_repo": True,
                "path": str(check_path),
                "git_dir": str(git_dir),
                "error": None,
            }

        # Also check parent directories (in case we're in a subdirectory)
        current = check_path
        while current != current.parent:
            git_dir = current / ".git"
            if git_dir.exists():
                return {
                    "is_git_repo": True,
                    "path": str(check_path),
                    "git_dir": str(git_dir),
                    "error": None,
                }
            current = current.parent

        return {
            "is_git_repo": False,
            "path": str(check_path),
            "git_dir": None,
            "error": None,
        }

    except Exception as e:
        logger.error(f"Error checking Git repository: {e}")
        return {
            "is_git_repo": False,
            "path": path or _current_working_dir or os.getcwd(),
            "git_dir": None,
            "error": str(e),
        }


@mcp.tool(
    name="get_git_username",
    description="Get Git username from local or global Git configuration",
)
def get_git_username(
    path: Optional[str] = None, config_type: str = "auto"
) -> Dict[str, Any]:
    """
    Get Git username from configuration.

    Args:
        path: Optional path to Git repository. If None, uses current working directory.
        config_type: Type of config to check - "local", "global", or "auto" (default)

    Returns:
        Dict containing:
        - username: Git username if found
        - email: Git email if found
        - config_type: Which config was used ("local" or "global")
        - path: The path that was checked
        - is_git_repo: Whether the path is a Git repository
        - error: Error message if any
    """
    try:
        # Use current working directory if no path specified
        if path is None:
            path = _current_working_dir or os.getcwd()

        check_path = Path(path).resolve()

        # First check if it's a Git repository
        repo_check = is_git_repository(str(check_path))
        is_git_repo = repo_check["is_git_repo"]

        username = None
        email = None
        used_config_type = None
        error = None

        # Try to get Git configuration
        if config_type == "auto" or config_type == "local":
            if is_git_repo:
                # Try local config first
                try:
                    result = subprocess.run(
                        ["git", "config", "--local", "--get", "user.name"],
                        cwd=str(check_path),
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        username = result.stdout.strip()
                        used_config_type = "local"

                        # Also get email
                        email_result = subprocess.run(
                            ["git", "config", "--local", "--get", "user.email"],
                            cwd=str(check_path),
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if email_result.returncode == 0 and email_result.stdout.strip():
                            email = email_result.stdout.strip()

                except (
                    subprocess.TimeoutExpired,
                    subprocess.CalledProcessError,
                    FileNotFoundError,
                ) as e:
                    logger.debug(f"Failed to get local Git config: {e}")

        # If no local config found and we should check global, or if explicitly requested
        if (
            username is None and config_type in ["auto", "global"]
        ) or config_type == "global":
            try:
                result = subprocess.run(
                    ["git", "config", "--global", "--get", "user.name"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    username = result.stdout.strip()
                    used_config_type = "global"

                    # Also get email
                    email_result = subprocess.run(
                        ["git", "config", "--global", "--get", "user.email"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if email_result.returncode == 0 and email_result.stdout.strip():
                        email = email_result.stdout.strip()

            except (
                subprocess.TimeoutExpired,
                subprocess.CalledProcessError,
                FileNotFoundError,
            ) as e:
                error = f"Failed to get Git config: {e}"
                logger.error(error)

        if username is None and error is None:
            error = "No Git username found in configuration"

        return {
            "username": username,
            "email": email,
            "config_type": used_config_type,
            "path": str(check_path),
            "is_git_repo": is_git_repo,
            "error": error,
        }

    except Exception as e:
        logger.error(f"Error getting Git username: {e}")
        return {
            "username": None,
            "email": None,
            "config_type": None,
            "path": path or _current_working_dir or os.getcwd(),
            "is_git_repo": False,
            "error": str(e),
        }


@mcp.tool(
    name="set_working_dir",
    description="Set the working directory for Git operations",
)
def set_working_dir(path: str) -> Dict[str, Any]:
    """
    Set the working directory for subsequent Git operations.
    
    Args:
        path: Path to set as the working directory
        
    Returns:
        Dict containing:
        - success: Boolean indicating if the operation was successful
        - old_dir: Previous working directory
        - new_dir: New working directory
        - error: Error message if any
    """
    global _current_working_dir
    
    try:
        # Store old directory
        old_dir = _current_working_dir or os.getcwd()
        
        # Convert to Path object for validation
        new_path = Path(path).resolve()
        
        # Check if path exists
        if not new_path.exists():
            return {
                "success": False,
                "old_dir": old_dir,
                "new_dir": None,
                "error": f"Path does not exist: {new_path}",
            }
        
        # Check if it's a directory
        if not new_path.is_dir():
            return {
                "success": False,
                "old_dir": old_dir,
                "new_dir": None,
                "error": f"Path is not a directory: {new_path}",
            }
        
        # Set the new working directory
        _current_working_dir = str(new_path)
        
        return {
            "success": True,
            "old_dir": old_dir,
            "new_dir": str(new_path),
            "error": None,
        }
        
    except Exception as e:
        logger.error(f"Error setting working directory: {e}")
        return {
            "success": False,
            "old_dir": _current_working_dir or os.getcwd(),
            "new_dir": None,
            "error": str(e),
        }


@mcp.tool(
    name="get_working_dir", 
    description="Get the currently set working directory for Git operations"
)
def get_working_dir() -> Dict[str, Any]:
    """
    Get the currently set working directory.
    
    Returns:
        Dict containing:
        - current_dir: Currently set working directory (or system CWD if not set)
        - is_custom: Boolean indicating if custom directory is set
        - error: Error message if any
    """
    try:
        current_dir = _current_working_dir or os.getcwd()
        is_custom = _current_working_dir is not None
        
        return {
            "current_dir": current_dir,
            "is_custom": is_custom,
            "error": None,
        }
        
    except Exception as e:
        logger.error(f"Error getting working directory: {e}")
        return {
            "current_dir": None,
            "is_custom": False,
            "error": str(e),
        }


def create_server() -> FastMCP:
    """Create and return the MCP server instance."""
    return mcp


if __name__ == "__main__":
    # This allows the server to be run directly for testing
    mcp.run()
