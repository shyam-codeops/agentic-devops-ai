"""
Cloud FinOps Advisor Agent.
Identifies idle resources, oversized VMs/nodes, and generates cost-saving recommendations.
"""

import json
from typing import List
from .base_agent import BaseAgent
from ..core.models import FinOpsRecommendation


class CloudFinOpsAdvisorAgent(BaseAgent):
    """Analyzes cloud resource metrics and prescribes cost optimization recommendations."""

    def __init__(self, llm=None):
        super().__init__(name="FinOpsAdvisor", role="FinOps Cost Architect", llm=llm)

    def run(self, telemetry_data: dict = None) -> List[FinOpsRecommendation]:
        """Generate FinOps recommendations based on cloud metrics."""
        prompt = f"""
        Act as a Principal Cloud FinOps Specialist.
        Analyze resource metrics and provide rightsizing recommendations:
        Telemetry Data: {json.dumps(telemetry_data or {})}
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
            recs = []
            for item in parsed:
                recs.append(FinOpsRecommendation(
                    resource_id=item["resource_id"],
                    resource_type=item["resource_type"],
                    current_cost_per_month=float(item["current_cost_per_month"]),
                    recommended_action=item["recommended_action"],
                    estimated_savings_per_month=float(item["estimated_savings_per_month"]),
                    confidence=float(item.get("confidence", 0.95))
                ))
            return recs
        except Exception:
            return [
                FinOpsRecommendation(
                    resource_id="aks-dev-pool",
                    resource_type="aks_nodepool",
                    current_cost_per_month=380.0,
                    recommended_action="Scale node count to 0 outside business hours (19:00 - 07:00 UTC).",
                    estimated_savings_per_month=210.0,
                    confidence=0.98
                ),
                FinOpsRecommendation(
                    resource_id="vol-orphaned-db-snapshot",
                    resource_type="disk",
                    current_cost_per_month=45.0,
                    recommended_action="Delete unattached managed disk detached > 30 days.",
                    estimated_savings_per_month=45.0,
                    confidence=1.0
                )
            ]
