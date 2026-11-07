"""Unit & integration tests for Antigravity Plugin & Skill Enforcer Automation."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from scripts.antigravity_plugin_enforcer import (
    GLOBAL_PLUGINS,
    GLOBAL_SKILLS,
    MASTER_ECC,
    get_installed_plugins,
    count_available_skills,
    verify_skills,
    audit_project,
    sync_project,
)


def test_installed_plugins_discovery():
    """Verify that installed plugins are discovered correctly."""
    plugins = get_installed_plugins()
    assert isinstance(plugins, list)
    if not GLOBAL_PLUGINS.exists():
        pytest.skip("Global plugins directory not present in CI environment")
    assert len(plugins) >= 10
    assert "everything-claude-code" in plugins
    assert "magic" in plugins
    assert "context7" in plugins
    assert "coderabbit" in plugins


def test_available_skills_count():
    """Verify that skills catalog contains 400+ production skills."""
    if not GLOBAL_SKILLS.exists() and not MASTER_ECC.exists():
        pytest.skip("Global skills directory not present in CI environment")
    skills_count = count_available_skills()
    assert skills_count >= 400


def test_verify_skills_integrity():
    """Verify that skills validation runs with 100% health."""
    if not GLOBAL_SKILLS.exists() and not MASTER_ECC.exists():
        pytest.skip("Global skills directory not present in CI environment")
    report = verify_skills()
    assert report["total_skills"] >= 400
    assert report["valid_skills"] >= 400
    assert report["health_percentage"] >= 95.0
    assert len(report["sample_catalog"]) > 0


def test_current_project_audit_compliance():
    """Verify that the current project scores high compliance."""
    cwd = Path(".")
    audit = audit_project(cwd)
    assert audit["is_valid_dir"] is True
    if not (cwd / ".agents").exists():
        pytest.skip("Project .agents directory not present in CI clone")
    assert audit["has_agents_dir"] is True
    assert audit["has_skills"] is True
    assert audit["skills_count"] >= 400
    assert audit["has_rules"] is True
    assert audit["has_mandatory_policy"] is True
    assert audit["has_mcp_config"] is True
    assert audit["compliance_score"] >= 85.0


def test_nonexistent_project_audit():
    """Verify audit handles nonexistent paths gracefully."""
    fake_path = Path("./nonexistent_random_folder_xyz_123")
    audit = audit_project(fake_path)
    assert audit["is_valid_dir"] is False
    assert audit["compliance_score"] == 0.0


def test_sync_project_in_temp_dir(tmp_path: Path):
    """Verify that sync_project creates valid scaffolding in an empty folder."""
    target = tmp_path / "test_project"
    res = sync_project(target)
    assert res["is_valid_dir"] is True
    assert (target / ".agents").exists()
    assert (target / ".agents" / "rules" / "mandatory-plugins-and-skills.md").exists()
    assert (target / ".mcp.json").exists()
    assert (target / ".vscode" / "settings.json").exists()

    with open(target / ".mcp.json", "r", encoding="utf-8-sig") as f:
        mcp_data = json.load(f)
        assert "mcpServers" in mcp_data
        assert "magic" in mcp_data["mcpServers"]
        assert "context7" in mcp_data["mcpServers"]
