import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.core.anomaly_detector import AnomalyDetector

@pytest.fixture
def anomaly_detector():
    with patch('app.core.anomaly_detector.firestore.Client') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        detector = AnomalyDetector()
        detector.db = mock_db
        yield detector

class TestRiskScoreCalculation:

    @pytest.mark.asyncio
    async def test_calculate_risk_score_critical_severity(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        decision = {
            "severity": "critical",
            "decision": "block"
        }

        score = await anomaly_detector.calculate_risk_score("user-123", "tenant-1", decision)

        assert score >= 40
        assert score <= 100

    @pytest.mark.asyncio
    async def test_calculate_risk_score_high_severity(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        decision = {
            "severity": "high",
            "decision": "block"
        }

        score = await anomaly_detector.calculate_risk_score("user-456", "tenant-1", decision)

        assert score >= 30
        assert score <= 100

    @pytest.mark.asyncio
    async def test_calculate_risk_score_medium_severity(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        decision = {
            "severity": "medium",
            "decision": "redact"
        }

        score = await anomaly_detector.calculate_risk_score("user-789", "tenant-1", decision)

        assert score >= 20
        assert score <= 100

    @pytest.mark.asyncio
    async def test_calculate_risk_score_low_severity(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        decision = {
            "severity": "low",
            "decision": "allow"
        }

        score = await anomaly_detector.calculate_risk_score("user-000", "tenant-1", decision)

        assert score >= 0
        assert score <= 100

    @pytest.mark.asyncio
    async def test_calculate_risk_score_unknown_severity(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        decision = {
            "severity": "unknown",
            "decision": "allow"
        }

        score = await anomaly_detector.calculate_risk_score("user-111", "tenant-1", decision)

        assert score >= 0
        assert score <= 100

class TestFrequencyAnomaly:

    @pytest.mark.asyncio
    async def test_frequency_anomaly_empty_history(self, anomaly_detector):
        score = await anomaly_detector._check_frequency_anomaly([])

        assert score == 0

    @pytest.mark.asyncio
    async def test_frequency_anomaly_low_count(self, anomaly_detector):
        history = [{"timestamp": datetime.utcnow()} for _ in range(5)]

        score = await anomaly_detector._check_frequency_anomaly(history)

        assert score >= 0

    @pytest.mark.asyncio
    async def test_frequency_anomaly_moderate_count(self, anomaly_detector):
        history = [{"timestamp": datetime.utcnow()} for _ in range(15)]

        score = await anomaly_detector._check_frequency_anomaly(history)

        assert score >= 5

    @pytest.mark.asyncio
    async def test_frequency_anomaly_high_count(self, anomaly_detector):
        history = [{"timestamp": datetime.utcnow()} for _ in range(35)]

        score = await anomaly_detector._check_frequency_anomaly(history)

        assert score >= 10

class TestPatternAnomaly:

    @pytest.mark.asyncio
    async def test_pattern_anomaly_empty_history(self, anomaly_detector):
        score = await anomaly_detector._check_pattern_anomaly([])

        assert score == 0

    @pytest.mark.asyncio
    async def test_pattern_anomaly_varied_times(self, anomaly_detector):
        now = datetime.utcnow()
        history = [
            {"timestamp": now - timedelta(hours=i * 2)} for i in range(5)
        ]

        score = await anomaly_detector._check_pattern_anomaly(history)

        assert score >= 0

    @pytest.mark.asyncio
    async def test_pattern_anomaly_rapid_requests(self, anomaly_detector):
        now = datetime.utcnow()
        history = [
            {"timestamp": now - timedelta(seconds=i)} for i in range(10)
        ]

        score = await anomaly_detector._check_pattern_anomaly(history)

        assert score >= 0

class TestViolationHistory:

    @pytest.mark.asyncio
    async def test_violation_history_no_violations(self, anomaly_detector):
        history = [
            {"decision": {"decision": "allow"}},
            {"decision": {"decision": "allow"}}
        ]

        score = await anomaly_detector._check_violation_history(history)

        assert score == 0

    @pytest.mark.asyncio
    async def test_violation_history_with_blocks(self, anomaly_detector):
        history = [
            {"decision": {"decision": "block"}},
            {"decision": {"decision": "block"}},
            {"decision": {"decision": "allow"}}
        ]

        score = await anomaly_detector._check_violation_history(history)

        assert score >= 10

    @pytest.mark.asyncio
    async def test_violation_history_with_redacts(self, anomaly_detector):
        history = [
            {"decision": {"decision": "redact"}},
            {"decision": {"decision": "redact"}},
            {"decision": {"decision": "allow"}}
        ]

        score = await anomaly_detector._check_violation_history(history)

        assert score >= 5

    @pytest.mark.asyncio
    async def test_violation_history_mixed_decisions(self, anomaly_detector):
        history = [
            {"decision": {"decision": "block"}},
            {"decision": {"decision": "redact"}},
            {"decision": {"decision": "allow"}},
            {"decision": {"decision": "block"}}
        ]

        score = await anomaly_detector._check_violation_history(history)

        assert score > 0

    @pytest.mark.asyncio
    async def test_violation_history_empty(self, anomaly_detector):
        score = await anomaly_detector._check_violation_history([])

        assert score == 0

class TestGetUserHistory:

    @pytest.mark.asyncio
    async def test_get_user_history_returns_list(self, anomaly_detector):
        mock_docs = []
        for i in range(3):
            doc = MagicMock()
            doc.to_dict.return_value = {
                "timestamp": datetime.utcnow(),
                "decision": {"decision": "allow"}
            }
            mock_docs.append(doc)

        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = mock_docs

        history = await anomaly_detector._get_user_history("user-123", "tenant-1", days=7)

        assert isinstance(history, list)
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_get_user_history_empty(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        history = await anomaly_detector._get_user_history("user-999", "tenant-1", days=7)

        assert history == []

    @pytest.mark.asyncio
    async def test_get_user_history_custom_days(self, anomaly_detector):
        anomaly_detector.db.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []

        history = await anomaly_detector._get_user_history("user-456", "tenant-1", days=30)

        assert isinstance(history, list)
