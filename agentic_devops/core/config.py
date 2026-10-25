"""
Configuration and settings management for Agentic DevOps framework.
Zero external dependency implementation using dataclasses.
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class Settings:
    # LLM Settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    azure_openai_endpoint: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    azure_openai_api_key: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", ""))
    azure_openai_deployment: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"))
    model_name: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o"))
    temperature: float = 0.2

    # Safety Guardrails
    dry_run_mode: bool = field(default_factory=lambda: os.getenv("DEV_AGENT_DRY_RUN", "true").lower() == "true")
    require_human_approval: bool = True
    prohibited_namespaces: List[str] = field(default_factory=lambda: ["kube-system", "kube-public", "cert-manager"])
    allowed_actions: List[str] = field(default_factory=lambda: ["k8s_restart", "k8s_scale", "rollback", "config_patch"])

    # Integrations
    k8s_in_cluster: bool = False
    github_token: str = field(default_factory=lambda: os.getenv("GITHUB_TOKEN", ""))
    prometheus_url: str = field(default_factory=lambda: os.getenv("PROMETHEUS_URL", "http://localhost:9090"))


_settings_instance = None


def get_settings() -> Settings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
