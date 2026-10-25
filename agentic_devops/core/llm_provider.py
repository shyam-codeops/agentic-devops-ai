"""
Pluggable LLM Provider with OpenAI, Azure OpenAI, and offline Mock fallback.
"""

import json
import importlib
from typing import Dict, Any, Optional
from .config import get_settings


class LLMProvider:
    """Base class and factory for LLM generation."""

    def __init__(self, settings=None):
        self.settings = settings or get_settings()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate response from configured LLM.
        Falls back to MockLLM if no API key is provided.
        """
        if self.settings.openai_api_key:
            return self._call_openai(prompt, system_prompt)
        elif self.settings.azure_openai_endpoint and self.settings.azure_openai_api_key:
            return self._call_azure_openai(prompt, system_prompt)
        else:
            return self._call_mock_engine(prompt, system_prompt)

    def _call_openai(self, prompt: str, system_prompt: Optional[str]) -> str:
        try:
            openai_module = importlib.import_module("openai")
            client = openai_module.OpenAI(api_key=self.settings.openai_api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=self.settings.model_name,
                messages=messages,
                temperature=self.settings.temperature,
            )
            return resp.choices[0].message.content or ""
        except ImportError:
            return "OpenAI package is not installed. Please run: pip install openai"
        except Exception as e:
            return f"Error calling OpenAI API: {e}. Falling back to internal engine."

    def _call_azure_openai(self, prompt: str, system_prompt: Optional[str]) -> str:
        try:
            openai_module = importlib.import_module("openai")
            client = openai_module.AzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                api_key=self.settings.azure_openai_api_key,
                api_version="2024-02-15-preview"
            )
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=messages,
                temperature=self.settings.temperature,
            )
            return resp.choices[0].message.content or ""
        except ImportError:
            return "Azure OpenAI package is not installed. Please run: pip install openai"
        except Exception as e:
            return f"Error calling Azure OpenAI: {e}"

    def _call_mock_engine(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Deterministic, rule-based Mock engine for offline execution,
        automated tests, and CI/CD without billable tokens.
        """
        lower = prompt.lower()
        if "remediat" in lower or "remediation plan" in lower:
            return json.dumps({
                "actions": [
                    {
                        "action_type": "config_patch",
                        "target_resource": "deployment/payment-service",
                        "command_preview": "kubectl patch deployment payment-service -n default --patch '{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"payment\",\"resources\":{\"limits\":{\"memory\":\"1Gi\"},\"requests\":{\"memory\":\"512Mi\"}}}]}}}}'",
                        "is_safe": True,
                        "requires_approval": False,
                        "rationale": "Increase memory limit from 512Mi to 1Gi to accommodate peak GC overhead and prevent OOM restarts."
                    },
                    {
                        "action_type": "k8s_restart",
                        "target_resource": "deployment/payment-service",
                        "command_preview": "kubectl rollout restart deployment/payment-service -n default",
                        "is_safe": True,
                        "requires_approval": False,
                        "rationale": "Trigger rolling restart of pods with updated resource boundaries."
                    }
                ],
                "rollback_plan": "kubectl rollout undo deployment/payment-service -n default"
            })
        elif "triage" in lower or "oomkilled" in lower or "crashloopbackoff" in lower:
            return json.dumps({
                "root_cause": "Container memory limit exceeded (OOMKilled) during high-throughput traffic spike.",
                "affected_components": ["deployment/payment-service", "pod/payment-service-7f98c-x89p"],
                "confidence_score": 0.96,
                "suggested_runbook": "https://runbooks.corp/k8s/oom-troubleshooting.html",
                "telemetry_findings": [
                    "Memory usage spiked from 420Mi to 512Mi limit in 90 seconds.",
                    "Exit code 137 detected in container status.",
                    "No CPU throttling observed prior to crash."
                ]
            })
        elif "review" in lower or "diff" in lower:
            return json.dumps({
                "status": "changes_requested",
                "security_findings": [
                    {
                        "rule_id": "SEC-001",
                        "severity": "critical",
                        "file_path": "terraform/modules/aks/main.tf",
                        "line_number": 42,
                        "description": "Hardcoded database password or access token detected in plain text.",
                        "remediation_advice": "Store the secret in Azure Key Vault and reference via data source or Key Vault provider."
                    }
                ],
                "performance_findings": [
                    "Resource requests/limits are missing for worker deployment."
                ],
                "cost_impact_estimate": "+$180/month due to addition of Premium SSD data disks.",
                "summary_comment": "DevSecOps Bot detected 1 critical secret finding and missing resource quotas. Please address before merge."
            })
        elif "finops" in lower or "cost" in lower:
            return json.dumps([
                {
                    "resource_id": "aks-nodepool-spot-dev",
                    "resource_type": "aks_nodepool",
                    "current_cost_per_month": 420.0,
                    "recommended_action": "Migrate dev nodepool to Azure Spot Instances with auto-shutdown schedule (19:00 - 07:00 UTC).",
                    "estimated_savings_per_month": 280.0,
                    "confidence": 0.95
                },
                {
                    "resource_id": "unattached-disk-vol-9812",
                    "resource_type": "disk",
                    "current_cost_per_month": 65.0,
                    "recommended_action": "Snapshot and delete orphaned 512GB Premium SSD managed disk idle for > 45 days.",
                    "estimated_savings_per_month": 65.0,
                    "confidence": 0.99
                }
            ])
        else:
            return json.dumps({"status": "acknowledged", "message": "DevOps Agent processed request successfully."})
