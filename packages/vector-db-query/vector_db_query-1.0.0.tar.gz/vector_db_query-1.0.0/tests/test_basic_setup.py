"""Basic tests to verify project setup."""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all main modules can be imported."""
    import vector_db_query
    import vector_db_query.cli.main
    import vector_db_query.utils.config
    import vector_db_query.utils.logger
    
    assert vector_db_query.VERSION == "1.0.0"


def test_config_loading():
    """Test configuration loading."""
    from vector_db_query.utils.config import get_config
    
    config = get_config()
    assert config is not None
    assert config.app.name == "Vector DB Query System"
    assert config.embedding.model == "gemini-embedding-001"


def test_project_structure():
    """Test that project structure is correct."""
    project_root = Path(__file__).parent.parent
    
    # Check main directories exist
    assert (project_root / "src" / "vector_db_query").exists()
    assert (project_root / "config").exists()
    assert (project_root / "docker").exists()
    assert (project_root / "scripts").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "docs").exists()
    
    # Check key files exist
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "requirements.txt").exists()
    assert (project_root / "README.md").exists()
    assert (project_root / "LICENSE").exists()
    
    # Check scripts are executable
    for script in ["setup.sh", "run.sh", "test.sh", "start-qdrant.sh"]:
        script_path = project_root / "scripts" / script
        assert script_path.exists()
        # Check if executable (Unix only)
        if sys.platform != "win32":
            assert script_path.stat().st_mode & 0o111


def test_cli_help():
    """Test CLI help command."""
    from click.testing import CliRunner
    from vector_db_query.cli.main import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Vector DB Query System" in result.output
    

def test_version_command():
    """Test version command."""
    from click.testing import CliRunner
    from vector_db_query.cli.main import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output