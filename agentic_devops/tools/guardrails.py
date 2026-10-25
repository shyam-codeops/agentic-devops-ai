"""
Safety Guardrails for Agentic DevOps execution.
Enforces command sanitization, blast-radius limits, and policy compliance.
"""

import re
from typing import Tuple, List
from ..core.config import get_settings


class GuardrailViolationError(Exception):
    """Raised when an autonomous agent proposes an unsafe operation."""
    pass


class GuardrailValidator:
    """Validates remediation actions against enterprise security policies."""

    BLOCKED_SHELL_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"mkfs",
        r":\(\)\{.*:\|:&\};:",  # fork bomb
        r"dd\s+if=",
        r"chmod\s+-R\s+777\s+/",
        r">\s*/dev/sd[a-z]",
        r"drop\s+database",
        r"drop\s+table",
    ]

    BLOCKED_K8S_PATTERNS = [
        r"kubectl\s+delete\s+namespace",
        r"kubectl\s+delete\s+nodes?",
        r"kubectl\s+delete\s+all\s+--all",
        r"--force\s+--grace-period=0",
    ]

    def __init__(self, settings=None):
        self.settings = settings or get_settings()

    def validate_command(self, command: str, namespace: str = "default") -> Tuple[bool, str]:
        """
        Validates if a command is safe for execution.
        Returns (is_valid, reason).
        """
        if not command or not command.strip():
            return False, "Command cannot be empty."

        # Check blocked shell commands
        for pattern in self.BLOCKED_SHELL_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Prohibited dangerous command pattern detected: '{pattern}'"

        # Check blocked k8s commands
        for pattern in self.BLOCKED_K8S_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"Prohibited destructive Kubernetes action detected: '{pattern}'"

        # Check protected namespaces
        for protected in self.settings.prohibited_namespaces:
            if f"-n {protected}" in command or f"--namespace={protected}" in command or f"--namespace {protected}" in command:
                return False, f"Direct autonomous modification to protected namespace '{protected}' is strictly forbidden."

        return True, "Validation passed: command is safe."

    def enforce(self, command: str, namespace: str = "default") -> None:
        """Enforce validation or raise GuardrailViolationError."""
        is_safe, reason = self.validate_command(command, namespace)
        if not is_safe:
            raise GuardrailViolationError(reason)
