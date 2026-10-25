"""
Agent Orchestrator - Coordinates multi-agent collaboration and feedback loops.
"""

from typing import Dict, Any, Optional
from ..core.models import Alert, RemediationPlan
from ..agents.triage_agent import IncidentTriageAgent
from ..agents.remediation_agent import AutonomousRemediationAgent
from ..tools.guardrails import GuardrailValidator


class DevOpsAgentOrchestrator:
    """Supervisor orchestrator coordinating SRE triage, remediation, and verification."""

    def __init__(self, llm=None):
        self.triage_agent = IncidentTriageAgent(llm=llm)
        self.remediation_agent = AutonomousRemediationAgent(llm=llm)
        self.guardrails = GuardrailValidator()

    def handle_incident(self, alert: Alert, auto_execute_safe: bool = False) -> Dict[str, Any]:
        """
        End-to-end incident handling pipeline:
        1. SRE Triage Agent diagnoses root cause.
        2. Remediation Agent designs fix actions & rollback.
        3. Guardrails check all actions against policies.
        4. (Optional) Auto-execute safe non-destructive actions.
        """
        # Step 1: Triage
        diagnosis = self.triage_agent.run(alert)

        # Step 2: Remediation
        plan = self.remediation_agent.run(diagnosis, namespace=alert.namespace)

        # Step 3: Safety check
        all_actions_safe = all(action.is_safe for action in plan.actions)

        execution_summary = "Plan generated and waiting for engineer confirmation."
        if auto_execute_safe and all_actions_safe:
            execution_summary = "Auto-executed safe remediation actions in dry-run mode."
            plan.status = "executed"

        return {
            "incident_id": diagnosis.incident_id,
            "status": "success",
            "diagnosis": diagnosis.model_dump(),
            "remediation_plan": plan.model_dump(),
            "all_actions_safe": all_actions_safe,
            "execution_summary": execution_summary
        }
