"""Configuration settings for SwitchGuard + Laya + Ralph collaborative agent.
"""
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class AgentConfig:
    # Server configuration
    host: str = os.getenv("SWITCH_AGENT_HOST", "0.0.0.0")
    port: int = int(os.getenv("SWITCH_AGENT_PORT", "8080"))
    debug: bool = os.getenv("SWITCH_AGENT_DEBUG", "true").lower() in ("true", "1", "yes")

    # Switch AI Bot Identity
    bot_name: str = "SwitchGuard"
    bot_avatar: str = "https://api.dicebear.com/7.x/bottts/svg?seed=SwitchGuard"
    bot_description: str = "Team-first collaborative AI agent powered by Laya sub-millisecond triage and Ralph autonomous execution."

    # Laya Confidence & Safety Thresholds
    confidence_threshold: float = float(os.getenv("LAYA_CONFIDENCE_THRESHOLD", "0.75"))
    require_human_signoff_below_conf: bool = True
    block_destructive_shell: bool = True

    # Ralph execution limits
    ralph_max_iterations: int = int(os.getenv("RALPH_MAX_ITERATIONS", "10"))
    workspace_root: str = os.getenv(
        "SWITCH_WORKSPACE_ROOT",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

CONFIG = AgentConfig()
