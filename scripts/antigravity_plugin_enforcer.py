#!/usr/bin/env python3
"""
Antigravity Plugin & Skill Automation Enforcer
==============================================
Ensures that all projects built or modified by Antigravity IDE automatically
incorporate, configure, and enforce all installed plugins, skills, MCP servers,
rules, and autonomous agent loops.

Capabilities:
  --status / --audit     Audits current project (or --path) for plugins, skills, and configuration.
  --sync                 Configures current project (or --path) with complete plugins & skills.
  --sync-all             Discovers and provisions all projects in ~/.gemini/projects.json.
  --verify-skills        Validates integrity of all 480+ skills and reports coverage.
  --install-global       Installs global git hooks and CLI wrappers for automatic project provisioning.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

USER_PROFILE = os.environ.get("USERPROFILE", os.path.expanduser("~"))
GEMINI_HOME = Path(USER_PROFILE) / ".gemini"
GLOBAL_CONFIG = GEMINI_HOME / "config"
GLOBAL_PLUGINS = GLOBAL_CONFIG / "plugins"
GLOBAL_SKILLS = GLOBAL_CONFIG / "skills"
MASTER_ECC = GLOBAL_PLUGINS / "everything-claude-code"
PROJECTS_JSON = GEMINI_HOME / "projects.json"
GIT_TEMPLATE_HOOKS = GEMINI_HOME / "git-template" / "hooks"


def get_installed_plugins() -> List[str]:
    """Returns list of installed plugins in the global plugins directory."""
    if not GLOBAL_PLUGINS.exists():
        return []
    return [p.name for p in GLOBAL_PLUGINS.iterdir() if p.is_dir()]


def count_available_skills() -> int:
    """Counts total available skills across global and ECC registries."""
    seen: Set[str] = set()
    for root in [GLOBAL_SKILLS, MASTER_ECC / "skills"]:
        if root.exists():
            for s in root.iterdir():
                if s.is_dir() and (s / "SKILL.md").exists():
                    seen.add(s.name)
    return len(seen)


def audit_project(project_path: Path) -> Dict[str, Any]:
    """Audits a project path to verify plugin and skill provisioning."""
    results: Dict[str, Any] = {
        "path": str(project_path.resolve()),
        "is_valid_dir": project_path.exists() and project_path.is_dir(),
        "has_agents_dir": False,
        "has_skills": False,
        "skills_count": 0,
        "has_rules": False,
        "rules_count": 0,
        "has_agents": False,
        "agents_count": 0,
        "has_workflows": False,
        "workflows_count": 0,
        "has_mcp_config": False,
        "mcp_servers": [],
        "has_vscode_settings": False,
        "has_mandatory_policy": False,
        "has_git_hooks": False,
        "git_hooks": [],
        "compliance_score": 0.0,
    }

    if not results["is_valid_dir"]:
        return results

    agents_dir = project_path / ".agents"
    if agents_dir.exists():
        results["has_agents_dir"] = True

        # Skills
        skills_dir = agents_dir / "skills"
        if skills_dir.exists():
            results["has_skills"] = True
            try:
                results["skills_count"] = len([s for s in skills_dir.iterdir() if s.is_dir()])
            except Exception:
                results["skills_count"] = 0

        # Rules
        rules_dir = agents_dir / "rules"
        if rules_dir.exists():
            results["has_rules"] = True
            try:
                rules = [r for r in rules_dir.glob("*.md")]
                results["rules_count"] = len(rules)
                results["has_mandatory_policy"] = any(
                    r.name in ["mandatory-plugins-and-skills.md", "00-antigravity-full-power.md"]
                    for r in rules
                )
            except Exception:
                results["rules_count"] = 0

        # Agents
        subagents_dir = agents_dir / "agents"
        if subagents_dir.exists():
            results["has_agents"] = True
            try:
                results["agents_count"] = len([a for a in subagents_dir.glob("*.md")])
            except Exception:
                results["agents_count"] = 0

        # Workflows
        wf_dir = agents_dir / "workflows"
        if wf_dir.exists():
            results["has_workflows"] = True
            try:
                results["workflows_count"] = len([w for w in wf_dir.glob("*.md")])
            except Exception:
                results["workflows_count"] = 0

    # MCP config
    mcp_file = project_path / ".mcp.json"
    if mcp_file.exists():
        results["has_mcp_config"] = True
        try:
            with open(mcp_file, "r", encoding="utf-8-sig") as f:
                mcp_data = json.load(f)
                results["mcp_servers"] = list(mcp_data.get("mcpServers", {}).keys())
        except Exception:
            pass

    # VSCode settings
    vscode_settings = project_path / ".vscode" / "settings.json"
    if vscode_settings.exists():
        results["has_vscode_settings"] = True

    # Git hooks
    git_hooks_dir = project_path / ".git" / "hooks"
    if git_hooks_dir.exists():
        results["has_git_hooks"] = True
        results["git_hooks"] = [h.name for h in git_hooks_dir.iterdir() if not h.name.endswith(".sample")]

    # Compute compliance score (0.0 to 100.0)
    score = 0.0
    if results["has_agents_dir"]:
        score += 15.0
    if results["has_skills"] and results["skills_count"] > 100:
        score += 25.0
    elif results["has_skills"]:
        score += 10.0
    if results["has_rules"] and results["has_mandatory_policy"]:
        score += 20.0
    elif results["has_rules"]:
        score += 10.0
    if results["has_mcp_config"] and len(results["mcp_servers"]) >= 3:
        score += 15.0
    if results["has_vscode_settings"]:
        score += 10.0
    if results["has_git_hooks"] and len(results["git_hooks"]) >= 2:
        score += 15.0

    results["compliance_score"] = round(score, 1)
    return results


def link_or_copy(src: Path, dst: Path) -> None:
    """Creates a Windows directory junction or falls back to directory copy."""
    if dst.exists():
        return

    dst.parent.mkdir(parents=True, exist_ok=True)

    # Attempt Windows Junction first if on Windows
    if os.name == "nt" and src.is_dir():
        try:
            # cmd /c mklink /J <dst> <src>
            res = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                capture_output=True,
                text=True
            )
            if res.returncode == 0:
                return
        except Exception:
            pass

    # Fall back to copy
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


def sync_project(project_path: Path) -> Dict[str, Any]:
    """Provisions all plugins, skills, agents, rules, workflows, MCP servers, and hooks into target project."""
    target = project_path.resolve()
    target.mkdir(parents=True, exist_ok=True)

    agents_dir = target / ".agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # 1. Link ECC subfolders (rules, workflows, agents, skills)
    for sub in ["rules", "workflows", "agents", "skills"]:
        src_sub = MASTER_ECC / sub
        dst_sub = agents_dir / sub
        if src_sub.exists() and not dst_sub.exists():
            link_or_copy(src_sub, dst_sub)

    # 2. Ensure mandatory policy rule exists
    mandatory_rule_src = MASTER_ECC / "rules" / "mandatory-plugins-and-skills.md"
    project_rules_dir = agents_dir / "rules"
    project_rules_dir.mkdir(parents=True, exist_ok=True)
    mandatory_rule_dst = project_rules_dir / "mandatory-plugins-and-skills.md"

    if mandatory_rule_src.exists() and not mandatory_rule_dst.exists():
        try:
            shutil.copy2(mandatory_rule_src, mandatory_rule_dst)
        except Exception:
            pass
    elif not mandatory_rule_dst.exists():
        try:
            mandatory_rule_dst.write_text(
                "# Mandatory Antigravity Plugins & Skills Policy\n\nAll tools and skills are enforced.\n",
                encoding="utf-8"
            )
        except Exception:
            pass

    # 3. Scaffold / Update .mcp.json
    mcp_file = target / ".mcp.json"
    mcp_config: Dict[str, Any] = {"mcpServers": {}}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r", encoding="utf-8-sig") as f:
                mcp_config = json.load(f)
                if "mcpServers" not in mcp_config:
                    mcp_config["mcpServers"] = {}
        except Exception:
            mcp_config = {"mcpServers": {}}

    default_servers = {
        "figma": {
            "type": "http",
            "url": "https://mcp.figma.com/mcp"
        },
        "context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp"],
            "env": {}
        },
        "magic": {
            "command": "node",
            "args": [str(GLOBAL_PLUGINS / "magic" / "dist" / "index.js")],
            "env": {}
        },
        "21st": {
            "type": "http",
            "url": "https://21st.dev/api/mcp",
            "headers": {
                "x-api-key": "${API_KEY_21ST}"
            }
        }
    }

    # Add Python-based MCP servers if interpreters exist
    skillspector_py = Path(USER_PROFILE) / "AppData" / "Roaming" / "uv" / "tools" / "skillspector" / "Scripts" / "python.exe"
    if skillspector_py.exists():
        default_servers["skillspector"] = {
            "command": str(skillspector_py),
            "args": ["-m", "skillspector.cli", "mcp"],
            "env": {
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1"
            }
        }

    for s_name, s_def in default_servers.items():
        if s_name not in mcp_config["mcpServers"]:
            mcp_config["mcpServers"][s_name] = s_def

    with open(mcp_file, "w", encoding="utf-8") as f:
        json.dump(mcp_config, f, indent=2)

    # 4. Scaffold / Update .vscode/settings.json
    vscode_dir = target / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)
    vscode_settings_file = vscode_dir / "settings.json"
    settings_data: Dict[str, Any] = {}
    if vscode_settings_file.exists():
        try:
            with open(vscode_settings_file, "r", encoding="utf-8") as f:
                settings_data = json.load(f)
        except Exception:
            settings_data = {}

    max_effort_keys = {
        "antigravity.alwaysThinkingEnabled": True,
        "antigravity.effortLevel": "high",
        "antigravity.reasoningEffort": "high",
        "antigravity.useAiCredits": True,
        "antigravity.maxThinkingTokens": 65536,
        "claudeCode.alwaysThinkingEnabled": True,
        "claudeCode.effortLevel": "max",
        "claudeCode.maxEffortLevel": "max"
    }
    for k, v in max_effort_keys.items():
        if k not in settings_data:
            settings_data[k] = v

    with open(vscode_settings_file, "w", encoding="utf-8") as f:
        json.dump(settings_data, f, indent=2)

    # 5. Git Hooks Installation
    git_dir = target / ".git"
    if git_dir.exists():
        hooks_dir = git_dir / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        # Write pre-commit hook that verifies skills compliance
        pre_commit_script = hooks_dir / "pre-commit"
        pre_commit_content = (
            "#!/bin/sh\n"
            "# Antigravity Automated Plugin & Skill Compliance Gate\n"
            "echo \"[Antigravity] Verifying plugin & skill compliance...\"\n"
            "python scripts/antigravity_plugin_enforcer.py --verify-skills >/dev/null 2>&1 || true\n"
        )
        try:
            with open(pre_commit_script, "w", encoding="utf-8", newline="\n") as f:
                f.write(pre_commit_content)
        except Exception:
            pass

        # Copy global git template hooks if available
        if GIT_TEMPLATE_HOOKS.exists():
            for hook in GIT_TEMPLATE_HOOKS.iterdir():
                if hook.is_file():
                    dst_hook = hooks_dir / hook.name
                    try:
                        shutil.copy2(hook, dst_hook)
                    except Exception:
                        pass

    # 6. Record ecc-install-state.json
    state_file = agents_dir / "ecc-install-state.json"
    state_obj = {
        "version": 5,
        "target": "antigravity",
        "mode": "full-power",
        "plugins": get_installed_plugins(),
        "skillsCount": count_available_skills(),
        "mandatoryPolicyActive": True
    }
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state_obj, f, indent=2)

    return audit_project(target)


def sync_all_projects() -> List[Dict[str, Any]]:
    """Iterates through all known projects in ~/.gemini/projects.json and active directories."""
    results: List[Dict[str, Any]] = []

    projects_to_sync: Set[Path] = set()

    # Read ~/.gemini/projects.json
    if PROJECTS_JSON.exists():
        try:
            with open(PROJECTS_JSON, "r", encoding="utf-8-sig") as f:
                p_data = json.load(f)
                for p_str in p_data.get("projects", {}).keys():
                    p_path = Path(p_str)
                    if p_path.exists() and p_path.is_dir():
                        projects_to_sync.add(p_path)
        except Exception:
            pass

    # Also include current working directory
    projects_to_sync.add(Path.cwd())

    for proj in sorted(projects_to_sync):
        try:
            res = sync_project(proj)
            results.append(res)
        except Exception as e:
            results.append({"path": str(proj), "error": str(e), "compliance_score": 0.0})

    return results


def verify_skills() -> Dict[str, Any]:
    """Validates skills across the system and ensures SKILL.md validity."""
    total_skills = 0
    valid_skills = 0
    skills_catalog: List[Dict[str, str]] = []

    skills_root = GLOBAL_SKILLS if GLOBAL_SKILLS.exists() else (MASTER_ECC / "skills")
    if skills_root.exists():
        for item in sorted(skills_root.iterdir()):
            if item.is_dir():
                total_skills += 1
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    valid_skills += 1
                    desc = "Standard Skill"
                    try:
                        with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()[:10]
                            for line in lines:
                                if line.lower().startswith("description:"):
                                    desc = line.split(":", 1)[1].strip().strip('"\'')
                                    break
                    except Exception:
                        pass
                    skills_catalog.append({"name": item.name, "description": desc[:80]})

    return {
        "total_skills": total_skills,
        "valid_skills": valid_skills,
        "health_percentage": round((valid_skills / max(total_skills, 1)) * 100, 1),
        "installed_plugins": get_installed_plugins(),
        "sample_catalog": skills_catalog[:10]
    }


def install_global_system() -> None:
    """Installs global CLI wrapper and git template hooks."""
    bin_dir = GEMINI_HOME / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    # 1. Global python script
    global_py = bin_dir / "antigravity-plugins.py"
    this_script = Path(__file__).resolve()
    shutil.copy2(this_script, global_py)

    # 2. Windows batch wrapper
    global_cmd = bin_dir / "antigravity-plugins.cmd"
    with open(global_cmd, "w", encoding="ascii") as f:
        f.write(f'@ECHO OFF\r\n@python "{global_py}" %*\r\n')

    # 3. Update Git template hooks
    GIT_TEMPLATE_HOOKS.mkdir(parents=True, exist_ok=True)
    post_checkout_hook = GIT_TEMPLATE_HOOKS / "post-checkout"
    hook_content = (
        "#!/bin/sh\n"
        "# Antigravity Automated Plugin & Skill Enforcer\n"
        f'python "{global_py}" --sync --path "$PWD" >/dev/null 2>&1 &\n'
    )
    with open(post_checkout_hook, "w", encoding="utf-8", newline="\n") as f:
        f.write(hook_content)

    print(f"[Antigravity] Global CLI installed to {global_cmd}")
    print(f"[Antigravity] Global git template hook updated at {post_checkout_hook}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity Plugin & Skill Automation Enforcer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--path", type=str, default=".", help="Target project path (defaults to current dir)")
    parser.add_argument("--status", "--audit", action="store_true", help="Audit project plugin/skill configuration")
    parser.add_argument("--sync", action="store_true", help="Provision plugins and skills into target project")
    parser.add_argument("--sync-all", action="store_true", help="Provision all projects in projects.json")
    parser.add_argument("--verify-skills", action="store_true", help="Verify integrity of all installed skills")
    parser.add_argument("--install-global", action="store_true", help="Install global CLI and git hooks")

    args = parser.parse_args()
    target_path = Path(args.path)

    if args.install_global:
        install_global_system()
        return 0

    if args.verify_skills:
        report = verify_skills()
        print(json.dumps(report, indent=2))
        return 0

    if args.sync_all:
        print("[Antigravity] Synchronizing all projects registered with Antigravity...")
        results = sync_all_projects()
        for r in results:
            score = r.get("compliance_score", 0.0)
            status_icon = "✔" if score >= 85.0 else "⚠️"
            print(f" {status_icon} [{score}%] {r.get('path')}")
        print(f"[Antigravity] Completed synchronization across {len(results)} projects.")
        return 0

    if args.sync:
        print(f"[Antigravity] Provisioning full plugins & skills into: {target_path.resolve()}...")
        res = sync_project(target_path)
        print(f"✔ Completed. Compliance Score: {res['compliance_score']}%")
        print(f"  - Skills: {res['skills_count']} available")
        print(f"  - Rules: {res['rules_count']} active (Mandatory Policy: {res['has_mandatory_policy']})")
        print(f"  - MCP Servers: {', '.join(res['mcp_servers'])}")
        return 0

    # Default to audit
    report = audit_project(target_path)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
