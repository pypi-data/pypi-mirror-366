"""
Tests for MCP Git Config Server

@author: shizeying
@date: 2025-08-04
"""

import asyncio
import tempfile
import os
from pathlib import Path
import subprocess
import pytest

from mcp_git_config.server import is_git_repository, get_git_username, set_working_dir, get_working_dir


class TestIsGitRepository:
    """Test cases for is_git_repository tool."""

    def test_current_directory_is_git_repo(self):
        """Test checking current directory if it's a git repo."""
        result = is_git_repository()

        # Should return a valid result structure
        assert isinstance(result, dict)
        assert "is_git_repo" in result
        assert "path" in result
        assert "git_dir" in result
        assert "error" in result

    def test_non_existent_path(self):
        """Test checking a non-existent path."""
        result = is_git_repository("/path/that/does/not/exist")

        assert result["is_git_repo"] is False
        assert "does not exist" in result["error"]

    def test_temporary_directory_not_git(self):
        """Test checking a temporary directory (not a git repo)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = is_git_repository(tmpdir)

            assert result["is_git_repo"] is False
            assert result["error"] is None
            assert result["path"] == str(Path(tmpdir).resolve())

    def test_temporary_git_repository(self):
        """Test checking a temporary git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a git repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)

            result = is_git_repository(tmpdir)

            assert result["is_git_repo"] is True
            assert result["error"] is None
            assert Path(tmpdir, ".git").resolve() == Path(result["git_dir"]).resolve()


class TestGetGitUsername:
    """Test cases for get_git_username tool."""

    def test_get_username_structure(self):
        """Test that get_git_username returns proper structure."""
        result = get_git_username()

        # Should return a valid result structure
        assert isinstance(result, dict)
        assert "username" in result
        assert "email" in result
        assert "config_type" in result
        assert "path" in result
        assert "is_git_repo" in result
        assert "error" in result

    def test_get_username_from_temporary_repo(self):
        """Test getting username from a temporary git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a git repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True)

            # Set local git config
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
            )

            result = get_git_username(tmpdir)

            assert result["is_git_repo"] is True
            assert result["username"] == "Test User"
            assert result["email"] == "test@example.com"
            assert result["config_type"] == "local"
            assert result["error"] is None

    def test_non_git_directory(self):
        """Test getting username from a non-git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_git_username(tmpdir)

            assert result["is_git_repo"] is False
            # May still get global config, so we don't assert on username


class TestWorkingDirectory:
    """Test cases for working directory tools."""

    def test_get_working_dir_default(self):
        """Test getting working directory when not set."""
        result = get_working_dir()
        
        assert result["error"] is None
        assert result["is_custom"] is False
        assert result["current_dir"] is not None

    def test_set_working_dir_valid(self):
        """Test setting a valid working directory."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = set_working_dir(tmpdir)
            
            assert result["success"] is True
            assert result["error"] is None
            assert result["new_dir"] == str(Path(tmpdir).resolve())
            
            # Verify it was set
            get_result = get_working_dir()
            assert get_result["is_custom"] is True
            assert get_result["current_dir"] == str(Path(tmpdir).resolve())

    def test_set_working_dir_invalid_path(self):
        """Test setting an invalid working directory."""
        result = set_working_dir("/path/that/does/not/exist")
        
        assert result["success"] is False
        assert "does not exist" in result["error"]
        assert result["new_dir"] is None

    def test_set_working_dir_file_not_directory(self):
        """Test setting working directory to a file."""
        import tempfile
        
        with tempfile.NamedTemporaryFile() as tmp_file:
            result = set_working_dir(tmp_file.name)
            
            assert result["success"] is False
            assert "not a directory" in result["error"]
            assert result["new_dir"] is None


# Integration tests that require pytest-asyncio
@pytest.mark.asyncio
async def test_server_creation():
    """Test that server can be created without errors."""
    from mcp_git_config.server import create_server

    server = create_server()
    assert server is not None

    # Test that tools are registered
    tools = await server.list_tools()
    if hasattr(tools, 'tools'):
        tool_names = [tool.name for tool in tools.tools]
    else:
        tool_names = [tool.name for tool in tools]

    assert "is_git_repository" in tool_names
    assert "get_git_username" in tool_names
    assert "set_working_dir" in tool_names
    assert "get_working_dir" in tool_names
