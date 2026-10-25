import sys
import json
import argparse
from datetime import datetime, timezone
from .core.models import Alert, Severity
from .core.orchestrator import DevOpsAgentOrchestrator
from .agents.pr_reviewer_agent import DevSecOpsPRReviewerAgent
from .agents.finops_agent import CloudFinOpsAdvisorAgent

# Ensure stdout handles UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_banner():
    banner = """
===============================================================
   [AI] AGENTIC DEVOPS AI - Autonomous Multi-Agent Platform
         DevOps | DevSecOps | Kubernetes | Cloud FinOps
===============================================================
    """
    print(banner)


def cmd_triage(args):
    print(f"\n[*] Triaging alert for service: {args.service} (Severity: {args.severity})")
    alert = Alert(
        alert_id=args.alert_id or "ALT-1042",
        source="azure-monitor",
        title=args.title or f"Pod Failure in {args.service}",
        severity=Severity(args.severity),
        service=args.service,
        namespace=args.namespace,
        message=args.message or "CrashLoopBackOff detected with exit code 137"
    )
    orch = DevOpsAgentOrchestrator()
    result = orch.handle_incident(alert, auto_execute_safe=args.auto_execute)

    print("\n--- [TRIAGE] SRE ROOT CAUSE DIAGNOSIS ---")
    diag = result["diagnosis"]
    print(f"Incident ID   : {diag['incident_id']}")
    print(f"Root Cause    : {diag['root_cause']}")
    print(f"Confidence    : {diag['confidence_score'] * 100:.1f}%")
    print(f"Components    : {', '.join(diag['affected_components'])}")
    print("Telemetry Findings:")
    for f in diag["telemetry_findings"]:
        print(f"  * {f}")

    print("\n--- [REMEDIATION] AUTONOMOUS MITIGATION PLAN ---")
    plan = result["remediation_plan"]
    print(f"Plan ID       : {plan['plan_id']}")
    print(f"Rollback Cmd  : {plan['rollback_plan']}")
    print("Proposed Actions:")
    for idx, act in enumerate(plan["actions"], 1):
        safe_str = "SAFE" if act["is_safe"] else "REQUIRES APPROVAL"
        print(f"  [{idx}] [{safe_str}] {act['action_type']} -> {act['target_resource']}")
        print(f"      Command: {act['command_preview']}")
        print(f"      Reason : {act['rationale']}")

    print(f"\nExecution Status: {result['execution_summary']}")


def cmd_review_pr(args):
    print(f"\n[*] Running DevSecOps PR Review for Repo: {args.repo} PR #{args.pr_id}")
    sample_diff = """
+ resource "azurerm_storage_account" "storage" {
+   name                     = "storageprod01"
+   resource_group_name      = "rg-prod"
+   location                 = "eastus"
+   account_tier             = "Standard"
+   account_replication_type = "LRS"
+   enable_public_access     = true
+   password                 = "SuperSecretPassword123!"
+ }
    """
    diff_content = sample_diff
    if args.diff_file:
        try:
            with open(args.diff_file, "r", encoding="utf-8") as f:
                diff_content = f.read()
        except Exception as e:
            print(f"Could not read diff file: {e}. Using sample diff.")

    agent = DevSecOpsPRReviewerAgent()
    report = agent.run(pr_id=args.pr_id, repo=args.repo, diff_text=diff_content, filename=args.filename)

    print("\n--- [SECURITY] DEVSECOPS PR REVIEW REPORT ---")
    print(f"Repository: {report.repository} | PR #{report.pr_id}")
    print(f"Status    : {report.status.upper()}")
    print(f"Cost Est  : {report.cost_impact_estimate}")
    print(f"\nSummary:\n  {report.summary_comment}")

    if report.security_findings:
        print("\nSecurity Findings:")
        for idx, f in enumerate(report.security_findings, 1):
            print(f"  [{idx}] [{f.severity.value.upper()}] {f.description} ({f.file_path}:{f.line_number})")
            print(f"      Remediation: {f.remediation_advice}")


def cmd_finops(args):
    print("\n[*] Analyzing Cloud FinOps cost metrics and rightsizing recommendations...")
    agent = CloudFinOpsAdvisorAgent()
    recs = agent.run()

    total_savings = sum(r.estimated_savings_per_month for r in recs)
    print("\n--- [FINOPS] COST OPTIMIZATION REPORT ---")
    for idx, r in enumerate(recs, 1):
        print(f"\n[{idx}] Resource: {r.resource_id} ({r.resource_type})")
        print(f"    Current Cost: ${r.current_cost_per_month:.2f}/mo")
        print(f"    Action      : {r.recommended_action}")
        print(f"    Est. Savings: ${r.estimated_savings_per_month:.2f}/mo (Confidence: {r.confidence * 100:.0f}%)")

    print(f"\nTotal Potential Monthly Savings: ${total_savings:.2f}/month")


def main():
    parser = argparse.ArgumentParser(description="Agentic DevOps AI Autonomous Framework")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # triage
    p_triage = subparsers.add_parser("triage", help="Triage an alert and generate remediation")
    p_triage.add_argument("--service", default="payment-service", help="Name of service")
    p_triage.add_argument("--namespace", default="default", help="Kubernetes namespace")
    p_triage.add_argument("--severity", default="critical", choices=["low", "medium", "high", "critical"])
    p_triage.add_argument("--title", default=None, help="Alert title")
    p_triage.add_argument("--message", default=None, help="Alert message")
    p_triage.add_argument("--alert-id", default=None, help="Alert ID")
    p_triage.add_argument("--auto-execute", action="store_true", help="Auto-execute safe actions")

    # review-pr
    p_pr = subparsers.add_parser("review-pr", help="Run DevSecOps code review on a PR diff")
    p_pr.add_argument("--repo", default="contoso/ecommerce-platform", help="Repository")
    p_pr.add_argument("--pr-id", type=int, default=142, help="Pull Request ID")
    p_pr.add_argument("--filename", default="infrastructure/storage.tf", help="File name")
    p_pr.add_argument("--diff-file", default=None, help="Path to unified diff file")

    # finops
    subparsers.add_parser("finops", help="Run Cloud FinOps cost analyzer")

    args = parser.parse_args()
    print_banner()

    if args.command == "triage":
        cmd_triage(args)
    elif args.command == "review-pr":
        cmd_review_pr(args)
    elif args.command == "finops":
        cmd_finops(args)
    else:
        # Default run demo triage
        class DemoArgs:
            service = "payment-service"
            namespace = "default"
            severity = "critical"
            title = "Kubernetes Pod CrashLoopBackOff"
            message = "Pod payment-service-7f98c terminated with exit code 137 (OOMKilled)"
            alert_id = "ALT-DEMO-01"
            auto_execute = False
        print("No subcommand provided. Running default Autonomous Incident Triage demo:\n")
        cmd_triage(DemoArgs())


if __name__ == "__main__":
    main()
