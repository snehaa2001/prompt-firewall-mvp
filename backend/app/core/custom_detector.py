import re
from typing import List, Dict


class CustomDetector:
    def __init__(self):
        pass

    async def detect(self, text: str, custom_policies: List[Dict]) -> List[Dict]:
        risks = []

        for policy in custom_policies:
            if not policy.get("enabled", True):
                continue

            pattern = policy.get("pattern", "")
            if not pattern:
                continue

            try:
                compiled_pattern = re.compile(pattern)
                matches = compiled_pattern.finditer(text)

                for match in matches:
                    risks.append(
                        {
                            "type": "CUSTOM",
                            "subtype": "custom",
                            "match": match.group(0)[:50],
                            "severity": policy.get("severity", "medium"),
                            "position": match.start(),
                            "policy_id": policy.get("id"),
                            "policy_name": policy.get("name"),
                            "pattern": pattern[:50],
                        }
                    )
            except re.error:
                pass

        return risks
