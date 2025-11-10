import pytest
from app.core.policy_engine import PolicyEngine

@pytest.fixture
def policy_engine():
    return PolicyEngine()

class TestPolicyEngine:

    @pytest.mark.asyncio
    async def test_default_critical_severity(self, policy_engine):
        pii_risks = [{"type": "PII", "subtype": "us_ssn", "severity": "critical", "value": "123-45-6789"}]
        decision = await policy_engine.evaluate("Test", "Test", pii_risks, [], [], policies=[])

        assert decision.decision == 'block'
        assert decision.severity == 'critical'

    @pytest.mark.asyncio
    async def test_default_medium_severity(self, policy_engine):
        pii_risks = [{"type": "PII", "subtype": "email_address", "severity": "medium", "original_match": "test@example.com", "position": 7, "match": "te***om"}]
        decision = await policy_engine.evaluate("Email: test@example.com", "Response", pii_risks, [], [], policies=[])

        assert decision.decision == 'redact'
        assert '[REDACTED_EMAIL_ADDRESS]' in decision.promptModified

    @pytest.mark.asyncio
    async def test_policy_override(self, policy_engine):
        policies = [{
            "id": "p1",
            "type": "pii",
            "pattern": "phone_number",
            "action": "block",
            "severity": "high",
            "enabled": True
        }]
        pii_risks = [{"type": "PII", "subtype": "phone_number", "severity": "medium", "value": "415-555-1234"}]

        decision = await policy_engine.evaluate("Call 415-555-1234", "Response", pii_risks, [], [], policies=policies)

        assert decision.decision == 'block'

    @pytest.mark.asyncio
    async def test_no_risks(self, policy_engine):
        decision = await policy_engine.evaluate("What is the weather?", "It's sunny.", [], [], [], policies=[])

        assert decision.decision == 'allow'
        assert decision.severity == 'low'
