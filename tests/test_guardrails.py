"""
Unit tests for Safety Guardrails.
"""

import unittest
from agentic_devops.tools.guardrails import GuardrailValidator, GuardrailViolationError


class TestGuardrailValidator(unittest.TestCase):

    def setUp(self):
        self.validator = GuardrailValidator()

    def test_safe_restart_command(self):
        cmd = "kubectl rollout restart deployment/payment-service -n default"
        is_safe, reason = self.validator.validate_command(cmd, "default")
        self.assertTrue(is_safe)
        self.assertIn("safe", reason.lower())

    def test_safe_scale_command(self):
        cmd = "kubectl scale deployment/web --replicas=5 -n app"
        is_safe, _ = self.validator.validate_command(cmd, "app")
        self.assertTrue(is_safe)

    def test_block_rm_rf(self):
        cmd = "rm -rf /var/lib/docker"
        is_safe, reason = self.validator.validate_command(cmd)
        self.assertFalse(is_safe)
        self.assertIn("Prohibited", reason)

    def test_block_delete_namespace(self):
        cmd = "kubectl delete namespace production"
        is_safe, reason = self.validator.validate_command(cmd)
        self.assertFalse(is_safe)
        self.assertIn("Prohibited destructive", reason)

    def test_block_protected_namespace_modification(self):
        cmd = "kubectl delete pod my-pod -n kube-system"
        is_safe, reason = self.validator.validate_command(cmd)
        self.assertFalse(is_safe)
        self.assertIn("kube-system", reason)

    def test_enforce_raises_exception(self):
        cmd = "rm -rf /"
        with self.assertRaises(GuardrailViolationError):
            self.validator.enforce(cmd)


if __name__ == "__main__":
    unittest.main()
