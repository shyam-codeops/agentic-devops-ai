"""
Autonomous Remediation Agent.
Synthesizes safe remediation actions, runs guardrail validation, and proposes rollback plans.
"""

import json
from .base_agent import BaseAgent
from ..core.models import TriageDiagnosis, RemediationPlan, RemediationAction
from ..tools.guardrails import GuardrailValidator


class AutonomousRemediationAgent(BaseAgent):
    """Proposes and executes safe infrastructure remediation steps."""

    def __init__(self, llm=None):
        super().__init__(name="RemediationAgent", role="Autonomous Systems Engineer", llm=llm)
        self.guardrails = GuardrailValidator(self.settings)

    def run(self, diagnosis: TriageDiagnosis, namespace: str = "default") -> RemediationPlan:
        """Create a validated remediation plan for an incident diagnosis."""
        prompt = f"""
        Act as a Senior Infrastructure Automation Engineer.
        Formulate a step-by-step remediation plan for this incident:
        Incident ID: {diagnosis.incident_id}
        Root Cause: {diagnosis.root_cause}
        Affected Components: {diagnosis.affected_components}
        Telemetry Findings: {diagnosis.telemetry_findings}

        Generate a valid JSON object with:
        - actions: list of objects with [action_type, target_resource, command_preview, is_safe, requires_approval, rationale]
        - rollback_plan: string rollback command
        """

        raw_resp = self.llm.generate(prompt)

        try:
            cleaned = raw_resp.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            parsed = json.loads(cleaned)

            actions = []
            for act in parsed.get("actions", []):
                cmd = act.get("command_preview", "")
                is_safe, reason = self.guardrails.validate_command(cmd, namespace)
                actions.append(RemediationAction(
                    action_type=act.get("action_type", "config_patch"),
                    target_resource=act.get("target_resource", diagnosis.affected_components[0]),
                    command_preview=cmd,
                    is_safe=is_safe,
                    requires_approval=act.get("requires_approval", False) or not is_safe,
                    rationale=act.get("rationale", reason)
                ))

            rollback = parsed.get("rollback_plan", "kubectl rollout undo deployment")
        except Exception:
            actions = [
                RemediationAction(
                    action_type="k8s_restart",
                    target_resource=diagnosis.affected_components[0],
                    command_preview=f"kubectl rollout restart deployment/{diagnosis.affected_components[0]} -n {namespace}",
                    is_safe=True,
                    requires_approval=False,
                    rationale="Perform controlled rolling restart to restore pod health."
                )
            ]
            rollback = f"kubectl rollout undo deployment/{diagnosis.affected_components[0]} -n {namespace}"

        return RemediationPlan(
            plan_id=f"PLAN-{diagnosis.incident_id}",
            incident_id=diagnosis.incident_id,
            diagnosis=diagnosis,
            actions=actions,
            estimated_downtime_sec=0,
            rollback_plan=rollback,
            status="prepared"
        )
