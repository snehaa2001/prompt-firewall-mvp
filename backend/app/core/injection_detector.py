import re
from typing import List, Dict
import base64


class InjectionDetector:
    def __init__(self):
        self.roleplay_patterns = [
            r"(?i)ignore\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above)\s+instructions",
            r"(?i)act\s+as\s+(?:a\s+)?(?:DAN|evil|unrestricted)",
            r"(?i)you\s+are\s+now\s+(?:a\s+)?(?!assistant)",
            r"(?i)forget\s+(?:all\s+)?(?:the\s+)?(?:previous|your)\s+(?:instructions|rules)",
            r"(?i)disregard\s+(?:all\s+)?(?:the\s+)?(?:previous|prior)",
            r"(?i)new\s+instructions?\s*:",
            r"(?i)system\s+prompt\s*:",
            r"(?i)developer\s+mode",
        ]

        self.logic_trap_patterns = [
            r"(?i)if\s+you\s+(?:don\'t|do\s+not)\s+\w+\s*,\s*then",
            r"(?i)you\s+must\s+(?:respond|answer|tell)",
            r"(?i)it\'s\s+(?:okay|fine|safe)\s+to\s+(?:tell|share|reveal)",
            r"(?i)this\s+is\s+(?:a\s+)?(?:test|simulation|hypothetical)",
        ]

        self.encoding_indicators = [
            r"(?i)base64:",
            r"(?i)decode\s+(?:this|the\s+following)",
            r"[A-Za-z0-9+/]{20,}={0,2}",
            r"&#x200[B-F];",
            r"\\u200[B-F]",
        ]

        self.exfiltration_patterns = [
            r"(?i)(?:send|post|transmit)\s+(?:to|at)\s+https?://",
            r"(?i)webhook\s+(?:url|endpoint)",
            r"(?i)api\s+key\s+is",
            r"(?i)secret\s*=",
            r"(?i)password\s*[:=]",
        ]

        self.compiled_patterns = {
            "roleplay": [re.compile(p) for p in self.roleplay_patterns],
            "logic_trap": [re.compile(p) for p in self.logic_trap_patterns],
            "encoding": [re.compile(p) for p in self.encoding_indicators],
            "exfiltration": [re.compile(p) for p in self.exfiltration_patterns],
        }

    async def detect(self, text: str) -> List[Dict]:
        risks = []

        normalized_text = self._normalize_input(text)

        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(normalized_text)
                for match in matches:
                    risks.append(
                        {
                            "type": "PROMPT_INJECTION",
                            "subtype": category,
                            "match": match.group(0)[:50],
                            "severity": self._get_injection_severity(category),
                            "position": match.start(),
                            "pattern": pattern.pattern[:50],
                        }
                    )

        if self._check_repeated_delimiters(text):
            risks.append(
                {
                    "type": "PROMPT_INJECTION",
                    "subtype": "delimiter_attack",
                    "match": "Multiple delimiter sequences detected",
                    "severity": "high",
                    "position": 0,
                }
            )

        if self._check_length_anomaly(text):
            risks.append(
                {
                    "type": "PROMPT_INJECTION",
                    "subtype": "anomalous_length",
                    "match": f"Unusual prompt length: {len(text)} chars",
                    "severity": "medium",
                    "position": 0,
                }
            )

        return risks

    def _normalize_input(self, text: str) -> str:
        normalized = text

        try:
            if any(indicator in text.lower() for indicator in ["base64", "===", "=="]):
                potential_b64 = re.findall(r"[A-Za-z0-9+/]{20,}={0,2}", text)
                for encoded in potential_b64:
                    try:
                        decoded = base64.b64decode(encoded).decode("utf-8")
                        normalized += " " + decoded
                    except Exception:
                        pass
        except Exception:
            pass

        normalized = normalized.replace("\u200b", "")
        normalized = normalized.replace("\u200c", "")
        normalized = normalized.replace("\u200d", "")
        normalized = normalized.replace("\ufeff", "")

        return normalized

    def _check_repeated_delimiters(self, text: str) -> bool:
        delimiters = ["---", "===", "***", "###", "```"]
        count = sum(text.count(d) for d in delimiters)
        return count > 5

    def _check_length_anomaly(self, text: str) -> bool:
        # Only flag extremely long prompts (potential DoS/overflow)
        # Short prompts like "hi", "hello" are normal and should be allowed
        return len(text) > 5000

    def _get_injection_severity(self, category: str) -> str:
        severity_map = {
            "roleplay": "high",
            "logic_trap": "high",
            "exfiltration": "critical",
            "encoding": "medium",
            "delimiter_attack": "high",
        }
        return severity_map.get(category, "medium")
