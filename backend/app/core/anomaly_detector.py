from datetime import datetime, timedelta
from typing import Dict, List
from google.cloud import firestore


class AnomalyDetector:

    def __init__(self):
        self.db = firestore.Client()

    async def calculate_risk_score(self, user_id: str, tenant_id: str, current_decision: dict) -> int:
        severity_scores = {"low": 10, "medium": 20, "high": 30, "critical": 40}
        base_score = severity_scores.get(current_decision["severity"], 0)

        history = await self._get_user_history(user_id, tenant_id, days=7)

        frequency_score = await self._check_frequency_anomaly(history)
        pattern_score = await self._check_pattern_anomaly(history)
        violation_score = await self._check_violation_history(history)

        total_score = base_score + frequency_score + pattern_score + violation_score

        return min(total_score, 100)

    async def _get_user_history(self, user_id: str, tenant_id: str, days: int) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = (
            self.db.collection("logs")
            .where("userId", "==", user_id)
            .where("tenantId", "==", tenant_id)
            .where("timestamp", ">=", cutoff)
            .limit(1000)
        )

        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    async def _check_frequency_anomaly(self, history: List[Dict]) -> int:
        if not history:
            return 0

        hourly_counts: Dict[datetime, int] = {}
        for log in history:
            timestamp = log.get("timestamp")
            if timestamp:
                hour = timestamp.replace(minute=0, second=0, microsecond=0)
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1

        if not hourly_counts:
            return 0

        max_hourly_count = max(hourly_counts.values())

        # Check for high frequency based on absolute thresholds
        if max_hourly_count > 30:
            return 20
        elif max_hourly_count > 20:
            return 10
        elif max_hourly_count > 10:
            return 5

        return 0

    async def _check_pattern_anomaly(self, history: List[Dict]) -> int:
        if len(history) < 10:
            return 0

        total_detections = sum(1 for log in history if log.get("risks"))
        baseline_rate = total_detections / len(history)

        recent_logs = history[:10]
        recent_detections = sum(1 for log in recent_logs if log.get("risks"))
        recent_rate = recent_detections / len(recent_logs)

        if recent_rate > (baseline_rate * 2) and recent_rate > 0.5:
            return 20
        elif recent_rate > (baseline_rate * 1.5):
            return 10

        return 0

    async def _check_violation_history(self, history: List[Dict]) -> int:
        if not history:
            return 0

        block_count = sum(1 for log in history if log.get("decision", {}).get("decision") == "block")
        redact_count = sum(1 for log in history if log.get("decision", {}).get("decision") == "redact")

        total_violations = block_count + (redact_count * 0.5)

        if total_violations > 5:
            return 20
        elif total_violations >= 2:
            return 10
        elif total_violations > 0:
            return 5

        return 0
