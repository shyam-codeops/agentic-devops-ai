"""
Data models for Agentic DevOps AI framework using Python standard library dataclasses.
Works out of the box with zero external dependencies.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    REMEDIATING = "remediating"
    RESOLVED = "resolved"
    FAILED = "failed"


@dataclass
class Alert:
    alert_id: str
    title: str
    severity: Severity
    service: str
    message: str
    source: str = "prometheus"
    namespace: str = "default"
    cluster: str = "aks-production"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: Dict[str, str] = field(default_factory=dict)

    def model_dump(self) -> Dict[str, Any]:
        res = asdict(self)
        res["severity"] = self.severity.value
        res["timestamp"] = self.timestamp.isoformat()
        return res


@dataclass
class TriageDiagnosis:
    incident_id: str
    root_cause: str
    affected_components: List[str]
    confidence_score: float
    suggested_runbook: Optional[str] = None
    telemetry_findings: List[str] = field(default_factory=list)

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemediationAction:
    action_type: str  # k8s_restart, k8s_scale, rollback, config_patch
    target_resource: str
    command_preview: str
    is_safe: bool = True
    requires_approval: bool = False
    rationale: str = ""

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RemediationPlan:
    plan_id: str
    incident_id: str
    diagnosis: TriageDiagnosis
    actions: List[RemediationAction]
    estimated_downtime_sec: int = 0
    rollback_plan: str = ""
    status: str = "pending"
    execution_result: Optional[str] = None

    def model_dump(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "incident_id": self.incident_id,
            "diagnosis": self.diagnosis.model_dump(),
            "actions": [a.model_dump() for a in self.actions],
            "estimated_downtime_sec": self.estimated_downtime_sec,
            "rollback_plan": self.rollback_plan,
            "status": self.status,
            "execution_result": self.execution_result
        }


@dataclass
class SecurityFinding:
    rule_id: str
    severity: Severity
    file_path: str
    description: str
    remediation_advice: str
    line_number: Optional[int] = None

    def model_dump(self) -> Dict[str, Any]:
        res = asdict(self)
        res["severity"] = self.severity.value
        return res


@dataclass
class PRReviewReport:
    pr_id: int
    repository: str
    status: str = "approved"  # approved, changes_requested, blocked
    security_findings: List[SecurityFinding] = field(default_factory=list)
    performance_findings: List[str] = field(default_factory=list)
    cost_impact_estimate: str = "Neutral"
    summary_comment: str = ""

    def model_dump(self) -> Dict[str, Any]:
        return {
            "pr_id": self.pr_id,
            "repository": self.repository,
            "status": self.status,
            "security_findings": [f.model_dump() for f in self.security_findings],
            "performance_findings": self.performance_findings,
            "cost_impact_estimate": self.cost_impact_estimate,
            "summary_comment": self.summary_comment
        }


@dataclass
class FinOpsRecommendation:
    resource_id: str
    resource_type: str  # vm, aks_nodepool, disk, ip
    current_cost_per_month: float
    recommended_action: str
    estimated_savings_per_month: float
    confidence: float = 0.95

    def model_dump(self) -> Dict[str, Any]:
        return asdict(self)
