"""
Unit tests for DevOps Agents.
"""

import unittest
from agentic_devops.core.models import Alert, Severity
from agentic_devops.agents.triage_agent import IncidentTriageAgent
from agentic_devops.agents.remediation_agent import AutonomousRemediationAgent
from agentic_devops.agents.pr_reviewer_agent import DevSecOpsPRReviewerAgent
from agentic_devops.agents.finops_agent import CloudFinOpsAdvisorAgent


class TestDevOpsAgents(unittest.TestCase):

    def test_incident_triage_agent(self):
        agent = IncidentTriageAgent()
        alert = Alert(
            alert_id="ALT-101",
            title="Pod CrashLoopBackOff",
            severity=Severity.HIGH,
            service="order-service",
            namespace="production",
            message="Exit code 137 OOMKilled"
        )
        diag = agent.run(alert)
        self.assertEqual(diag.incident_id, "INC-ALT-101")
        self.assertTrue(len(diag.root_cause) > 0)
        self.assertGreater(diag.confidence_score, 0.5)

    def test_remediation_agent(self):
        triage_agent = IncidentTriageAgent()
        alert = Alert(
            alert_id="ALT-102",
            title="Pod OOMKilled",
            severity=Severity.CRITICAL,
            service="payment-service",
            namespace="default",
            message="Memory limit exceeded"
        )
        diag = triage_agent.run(alert)
        rem_agent = AutonomousRemediationAgent()
        plan = rem_agent.run(diag, namespace="default")
        self.assertEqual(plan.incident_id, "INC-ALT-102")
        self.assertGreater(len(plan.actions), 0)
        self.assertTrue(plan.actions[0].is_safe)

    def test_pr_reviewer_agent_detects_secrets(self):
        reviewer = DevSecOpsPRReviewerAgent()
        diff = """
+ resource "azurerm_key_vault" "kv" {
+   password = "SecretPassword123!"
+   client_secret = "my-hardcoded-secret"
+ }
        """
        report = reviewer.run(pr_id=50, repo="org/infra", diff_text=diff)
        self.assertEqual(report.status, "changes_requested")
        self.assertGreater(len(report.security_findings), 0)

    def test_finops_advisor_agent(self):
        finops = CloudFinOpsAdvisorAgent()
        recs = finops.run()
        self.assertGreater(len(recs), 0)
        self.assertGreater(recs[0].estimated_savings_per_month, 0)


if __name__ == "__main__":
    unittest.main()
