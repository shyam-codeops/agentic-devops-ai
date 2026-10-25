"""
Git diff scanner and DevSecOps static security rules engine.
"""

import re
from typing import List
from ..core.models import SecurityFinding, Severity


class GitDiffScanner:
    """Scans git diffs or file content for secrets, tokens, and misconfigurations."""

    SECRET_PATTERNS = [
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID detected", Severity.CRITICAL, "Use IAM roles or OpenID Connect."),
        (r"(?i)password\s*[:=]\s*['\"][^'\"]+['\"]", "Plaintext password detected in code", Severity.CRITICAL, "Store secrets in Azure Key Vault or AWS Secrets Manager."),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token detected", Severity.CRITICAL, "Revoke token and use GitHub Actions Secrets."),
        (r"(?i)api[_-]?key\s*[:=]\s*['\"][0-9a-zA-Z\-_]{16,}['\"]", "API Key exposed in code", Severity.HIGH, "Inject credentials via environment variables."),
        (r"(?i)client_secret\s*[:=]\s*['\"][^'\"]+['\"]", "Azure Client Secret exposed", Severity.CRITICAL, "Use Managed Identity or federated credentials.")
    ]

    IAC_SECURITY_CHECKS = [
        (r"0\.0\.0\.0/0", "Ingress open to 0.0.0.0/0 (Internet)", Severity.HIGH, "Restrict CIDR blocks to corporate VPN or private subnets."),
        (r"(?i)enable_public_access\s*=\s*true", "Public access enabled on data resource", Severity.HIGH, "Disable public network access and use Private Endpoints."),
        (r"(?i)privileged\s*:\s*true", "Kubernetes container running with privileged: true", Severity.HIGH, "Drop all capabilities and run as unprivileged non-root user.")
    ]

    def scan_diff(self, diff_text: str, filename: str = "patch.diff") -> List[SecurityFinding]:
        """Scans unified diff text for security violations."""
        findings: List[SecurityFinding] = []
        lines = diff_text.splitlines()

        for idx, line in enumerate(lines, start=1):
            if not line.startswith("+") or line.startswith("+++"):
                continue  # Only check additions in diff

            code = line[1:].strip()

            # Check for secrets
            for pattern, desc, severity, remediation in self.SECRET_PATTERNS:
                if re.search(pattern, code):
                    findings.append(SecurityFinding(
                        rule_id="SEC-SECRET",
                        severity=severity,
                        file_path=filename,
                        line_number=idx,
                        description=desc,
                        remediation_advice=remediation
                    ))

            # Check for IaC security violations
            for pattern, desc, severity, remediation in self.IAC_SECURITY_CHECKS:
                if re.search(pattern, code):
                    findings.append(SecurityFinding(
                        rule_id="IAC-SEC",
                        severity=severity,
                        file_path=filename,
                        line_number=idx,
                        description=desc,
                        remediation_advice=remediation
                    ))

        return findings
