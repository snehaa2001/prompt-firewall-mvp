import asyncio
from typing import Optional
from app.core.pii_detector import PIIDetector
from app.core.injection_detector import InjectionDetector
from app.core.custom_detector import CustomDetector
from app.core.policy_engine import PolicyEngine, PolicyDecision


class PromptFirewall:
    def __init__(self):
        self.pii_detector = PIIDetector()
        self.injection_detector = InjectionDetector()
        self.custom_detector = CustomDetector()
        self.policy_engine = PolicyEngine()

    async def analyze_request(self, prompt: str, response: str = "", policies: Optional[list] = None) -> PolicyDecision:

        if policies is None:
            policies = []

        custom_policies = [p for p in policies if p.get("type") == "custom"]

        pii_task = asyncio.create_task(self.pii_detector.detect(prompt))
        injection_task = asyncio.create_task(self.injection_detector.detect(prompt))
        custom_task = asyncio.create_task(self.custom_detector.detect(prompt, custom_policies))

        pii_risks, injection_risks, custom_risks = await asyncio.gather(pii_task, injection_task, custom_task)

        if response:
            response_pii_risks = await self.pii_detector.detect(response)
            pii_risks.extend(response_pii_risks)

        decision = await self.policy_engine.evaluate(
            prompt=prompt,
            response=response,
            pii_risks=pii_risks,
            injection_risks=injection_risks,
            custom_risks=custom_risks,
            policies=policies,
        )

        return decision
