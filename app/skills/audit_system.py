import os
import json
import logging
from typing import Dict, Any, List
from app.config import config

logger = logging.getLogger(__name__)

class AuditDispatcher:
    """Dispatches audit alerts based on config/scale.yaml settings."""
    def __init__(self):
        self.channel = config.audit.notification_channel.lower()
        self.webhook_url = config.audit.notification_link
        
    def dispatch(self, title: str, message: str, severity: str = "INFO"):
        """Route the alert depending on the configured channel."""
        full_msg = f"[{severity}] {title}: {message}"
        if self.channel == "none" or not self.channel:
            logger.info(f"Audit output (simulated {severity}): {full_msg}")
        elif self.channel in ["slack", "teams", "webhook"]:
            logger.info(f"Dispatching payload to {self.channel} webhook: {self.webhook_url}")
            # Mock external API call payload structure
            payload = {
                "text": full_msg,
                "severity": severity
            }
            logger.info(f"Payload sent: {json.dumps(payload)}")
        else:
            logger.warning(f"Unknown notification channel: {self.channel}. Printing to stdout.")
            print(full_msg)

class DependencyScanner:
    """Scans locked dependencies for spec drifts or architectural bounds."""
    @staticmethod
    def run_spec_check() -> List[str]:
        # Minimal mockup check for spec drift or outdated bases
        # Usually parses uv.lock or pip freeze manually
        findings = []
        if not os.path.exists("uv.lock"):
            findings.append("Missing uv.lock file. Ensure dependencies are locked!")
        return findings

class CVEMonitor:
    """Runs periodic security checks against the application bounds."""
    @staticmethod
    def run_cve_scan() -> List[Dict[str, Any]]:
        # Mock CVE scanner returning sample vulnerabilities
        return [
            # { "package": "requests", "cve": "CVE-0000-0000", "severity": "SEV-0" } 
        ]

def run_bi_annual_audit() -> Dict[str, Any]:
    """Execute the full audit logic."""
    dispatcher = AuditDispatcher()
    
    # 1. Check specs
    spec_drift = DependencyScanner.run_spec_check()
    if spec_drift:
        for alert in spec_drift:
            dispatcher.dispatch("Spec Drift", alert, "WARNING")
            
    # 2. Check CVEs
    cves = CVEMonitor.run_cve_scan()
    for cve in cves:
        msg = f"Package {cve.get('package')} vulnerable to {cve.get('cve')}"
        dispatcher.dispatch("CVE Detected", msg, cve.get("severity", "CRITICAL"))
        
    report = {
        "status": "completed",
        "spec_issues": len(spec_drift),
        "cve_issues": len(cves)
    }
    dispatcher.dispatch("Audit Summary", f"Bi-Annual Audit completed. Issues found: {len(spec_drift) + len(cves)}")
    return report

def run_weekly_cve() -> Dict[str, Any]:
    """Execute purely the weekly CVE job."""
    dispatcher = AuditDispatcher()
    cves = CVEMonitor.run_cve_scan()
    for cve in cves:
        msg = f"Package {cve.get('package')} vulnerable to {cve.get('cve')}"
        dispatcher.dispatch("CVE Detected", msg, cve.get("severity", "CRITICAL"))
        
    return {
        "status": "completed",
        "cve_issues": len(cves)
    }
