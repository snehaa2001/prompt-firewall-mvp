from typing import List, Dict, Literal
from pydantic import BaseModel


class PolicyDecision(BaseModel):
    decision: Literal["allow", "block", "redact", "warn"]
    promptModified: str
    responseModified: str
    risks: List[Dict]
    explanations: List[str]
    severity: Literal["low", "medium", "high", "critical"]
    metadata: Dict


class PolicyEngine:
    def __init__(self):
        self.action_priority = {"critical": "block", "high": "block", "medium": "redact", "low": "warn"}

    async def evaluate(
        self,
        prompt: str,
        response: str,
        pii_risks: List[Dict],
        injection_risks: List[Dict],
        custom_risks: List[Dict],
        policies: List[Dict],
    ) -> PolicyDecision:

        all_risks = pii_risks + injection_risks + custom_risks

        if not all_risks:
            return PolicyDecision(
                decision="allow",
                promptModified=prompt,
                responseModified=response,
                risks=[],
                explanations=["No security risks detected"],
                severity="low",
                metadata={"total_checks": 2},
            )

        max_severity = self._get_max_severity(all_risks)
        action = self._determine_action(all_risks, policies)

        modified_prompt = prompt
        modified_response = response
        explanations = []

        if action == "block":
            modified_prompt = "[BLOCKED]"
            modified_response = self._generate_block_message(all_risks)
            explanations = self._generate_explanations(all_risks, "blocked")

        elif action == "redact":
            from app.core.pii_detector import PIIDetector

            detector = PIIDetector()
            modified_prompt = detector.redact(prompt, pii_risks)
            modified_response = detector.redact(response, pii_risks)
            explanations = self._generate_explanations(all_risks, "redacted")

        elif action == "warn":
            explanations = self._generate_explanations(all_risks, "warned")

        elif action == "allow":
            explanations = self._generate_explanations(all_risks, "allowed")

        return PolicyDecision(
            decision=action,
            promptModified=modified_prompt,
            responseModified=modified_response,
            risks=all_risks,
            explanations=explanations,
            severity=max_severity,
            metadata={
                "pii_count": len(pii_risks),
                "injection_count": len(injection_risks),
                "custom_count": len(custom_risks),
                "total_risks": len(all_risks),
            },
        )

    def _get_max_severity(self, risks: List[Dict]) -> str:
        severity_order = ["low", "medium", "high", "critical"]
        max_sev = "low"
        for risk in risks:
            if severity_order.index(risk["severity"]) > severity_order.index(max_sev):
                max_sev = risk["severity"]
        return max_sev

    def _determine_action(self, risks: List[Dict], policies: List[Dict]) -> str:
        max_severity = self._get_max_severity(risks)

        for policy in policies:
            if policy.get("enabled", True):
                policy_type = policy.get("type", "").lower()
                policy_pattern = policy.get("pattern", "").lower()

                if policy_type == "custom":
                    matching_risks = [r for r in risks if r.get("policy_id") == policy.get("id")]
                else:
                    matching_risks = [r for r in risks if r["subtype"].lower() == policy_pattern]

                if matching_risks:
                    return policy["action"]

        return self.action_priority.get(max_severity, "warn")

    def _generate_block_message(self, risks: List[Dict]) -> str:
        risk_types = set(r["subtype"] for r in risks)
        return (
            f"This request was blocked due to security policy violations. "
            f"Detected issues: {', '.join(risk_types)}. "
            f"Please review your input and try again without sensitive information or injection attempts."
        )

    def _generate_explanations(self, risks: List[Dict], action: str) -> List[str]:
        explanations = []
        for risk in risks:
            if risk["type"] == "PII":
                explanations.append(f"PII detected: {risk['subtype']} (severity: {risk['severity']}) - {action}")
            elif risk["type"] == "PROMPT_INJECTION":
                explanations.append(f"Injection attempt detected: {risk['subtype']} (severity: {risk['severity']}) - {action}")
            elif risk["type"] == "CUSTOM":
                explanations.append(
                    f"Custom pattern detected: {risk.get('policy_name', 'custom')} (severity: {risk['severity']}) - {action}"
                )
        return explanations
