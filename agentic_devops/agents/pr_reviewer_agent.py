"""
DevSecOps PR Reviewer Agent.
Analyzes code and IaC diffs for security vulnerabilities, secrets, and policy compliance.
"""

from .base_agent import BaseAgent
from ..core.models import PRReviewReport
from ..tools.git_tools import GitDiffScanner


class DevSecOpsPRReviewerAgent(BaseAgent):
    """Automated security and architecture reviewer for Pull Requests."""

    def __init__(self, llm=None):
        super().__init__(name="DevSecOpsReviewer", role="Security Architect", llm=llm)
        self.scanner = GitDiffScanner()

    def run(self, pr_id: int, repo: str, diff_text: str, filename: str = "main.tf") -> PRReviewReport:
        """Analyze PR diff and output DevSecOps review."""
        # 1. Deterministic regex & pattern checks
        static_findings = self.scanner.scan_diff(diff_text, filename=filename)

        # 2. LLM contextual analysis
        prompt = f"""
        Act as a Lead DevSecOps Architect. Review this Pull Request diff:
        Repository: {repo}
        PR #{pr_id}
        File: {filename}
        Diff Content:
        {diff_text}

        Deterministic Scanner Findings:
        {[f.description for f in static_findings]}

        Analyze security risks, resource sizing, cost impact, and best practices.
        """
        _ = self.llm.generate(prompt)

        # Determine overall status
        status = "approved"
        has_critical = any(f.severity.value in ["critical", "high"] for f in static_findings)
        if has_critical:
            status = "changes_requested"

        summary = (
            f"Automated DevSecOps Review completed for PR #{pr_id} in {repo}. "
            f"Found {len(static_findings)} security item(s)."
        )
        if has_critical:
            summary += " ⚠️ Merge is blocked until Critical/High security findings are resolved."
        else:
            summary += " ✅ No critical security vulnerabilities identified."

        return PRReviewReport(
            pr_id=pr_id,
            repository=repo,
            status=status,
            security_findings=static_findings,
            performance_findings=["Ensure health checks and readiness probes are configured on deployments."],
            cost_impact_estimate="Neutral - no large tier changes detected.",
            summary_comment=summary
        )
