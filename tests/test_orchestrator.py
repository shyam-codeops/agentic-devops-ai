import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agentic_devops.core.models import Alert, Severity
from agentic_devops.core.orchestrator import DevOpsAgentOrchestrator


class TestOrchestrator(unittest.TestCase):

    def test_full_incident_orchestration(self):
        orch = DevOpsAgentOrchestrator()
        alert = Alert(
            alert_id="ALT-ORCH-01",
            title="High Latency Spike",
            severity=Severity.HIGH,
            service="checkout-api",
            namespace="default",
            message="p99 response time > 2500ms"
        )
        res = orch.handle_incident(alert, auto_execute_safe=True)
        self.assertEqual(res["status"], "success")
        self.assertIn("diagnosis", res)
        self.assertIn("remediation_plan", res)
        self.assertTrue(res["all_actions_safe"])


if __name__ == "__main__":
    unittest.main()
