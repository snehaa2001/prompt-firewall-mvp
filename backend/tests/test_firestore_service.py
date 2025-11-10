import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.firestore_service import FirestoreService

@pytest.fixture
def firestore_service():
    with patch('app.services.firestore_service.firebase_admin') as mock_firebase:
        mock_firebase._apps = {}
        with patch('app.services.firestore_service.firestore.Client') as mock_client:
            mock_db = MagicMock()
            mock_client.return_value = mock_db
            service = FirestoreService()
            service.db = mock_db
            yield service

class TestPIIRedaction:

    @pytest.mark.asyncio
    async def test_redact_pii_empty_text(self, firestore_service):
        result = await firestore_service.redact_pii_for_logging("")
        assert result == ""

    @pytest.mark.asyncio
    async def test_redact_pii_none_text(self, firestore_service):
        result = await firestore_service.redact_pii_for_logging(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_redact_pii_with_email(self, firestore_service):
        text = "Contact john@example.com"
        result = await firestore_service.redact_pii_for_logging(text)
        assert isinstance(result, str)

class TestLogRequest:

    @pytest.mark.asyncio
    async def test_log_request_without_db(self):
        service = FirestoreService()
        service.db = None
        result = await service.log_request("test", "response", {}, 0.5)
        assert result == "firestore_not_configured"

    @pytest.mark.asyncio
    async def test_log_request_with_db(self, firestore_service):
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "log-123"
        mock_collection.add.return_value = (None, mock_doc_ref)
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.log_request(
            prompt="Test prompt",
            response="Test response",
            decision={"decision": "allow"},
            latency=0.5
        )

        assert result == "log-123"
        firestore_service.db.collection.assert_called_with('logs')

    @pytest.mark.asyncio
    async def test_log_request_with_user_and_tenant(self, firestore_service):
        mock_collection = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "log-456"
        mock_collection.add.return_value = (None, mock_doc_ref)
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.log_request(
            prompt="Test",
            response="Response",
            decision={},
            latency=1.0,
            user_id="user-123",
            tenant_id="tenant-456"
        )

        assert result == "log-456"

class TestGetLogs:

    @pytest.mark.asyncio
    async def test_get_logs_without_db(self):
        service = FirestoreService()
        service.db = None
        result = await service.get_logs()
        assert result == {"logs": [], "total": 0}

    @pytest.mark.asyncio
    async def test_get_logs_with_limit(self, firestore_service):
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        mock_collection.order_by.return_value.limit.return_value = mock_query
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_logs(limit=10, offset=0)

        assert 'logs' in result
        assert 'total' in result

    @pytest.mark.asyncio
    async def test_get_logs_with_filter_blocked(self, firestore_service):
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        mock_collection.where.return_value.order_by.return_value.limit.return_value = mock_query
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_logs(filter_type="blocked")

        assert 'logs' in result

    @pytest.mark.asyncio
    async def test_get_logs_with_filter_redacted(self, firestore_service):
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        mock_collection.where.return_value.order_by.return_value.limit.return_value = mock_query
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_logs(filter_type="redacted")

        assert 'logs' in result

    @pytest.mark.asyncio
    async def test_get_logs_with_offset(self, firestore_service):
        mock_docs = []
        for i in range(5):
            doc = MagicMock()
            doc.id = f"log-{i}"
            doc.to_dict.return_value = {"prompt": f"test{i}"}
            mock_docs.append(doc)

        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = mock_docs
        mock_collection.order_by.return_value.limit.return_value = mock_query
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_logs(limit=5, offset=10)

        assert len(result['logs']) == 5

class TestPolicyOperations:

    @pytest.mark.asyncio
    async def test_get_active_policies_without_db(self):
        service = FirestoreService()
        service.db = None
        result = await service.get_active_policies()
        assert result == []

    @pytest.mark.asyncio
    async def test_get_active_policies(self, firestore_service):
        mock_docs = [MagicMock()]
        mock_docs[0].id = "policy-1"
        mock_docs[0].to_dict.return_value = {"name": "Test", "enabled": True}

        mock_collection = MagicMock()
        mock_collection.where.return_value.stream.return_value = mock_docs
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_active_policies()

        assert len(result) == 1
        assert result[0]['id'] == "policy-1"

    @pytest.mark.asyncio
    async def test_get_all_policies(self, firestore_service):
        mock_docs = []
        for i in range(3):
            doc = MagicMock()
            doc.id = f"policy-{i}"
            doc.to_dict.return_value = {"name": f"Policy {i}"}
            mock_docs.append(doc)

        mock_collection = MagicMock()
        mock_collection.stream.return_value = mock_docs
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_all_policies()

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_create_policy(self, firestore_service):
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "new-policy-123"
        mock_collection = MagicMock()
        mock_collection.add.return_value = (None, mock_doc_ref)
        firestore_service.db.collection.return_value = mock_collection

        policy = {
            "name": "Test Policy",
            "type": "pii",
            "pattern": "email",
            "action": "block"
        }

        result = await firestore_service.create_policy(policy)

        assert result == "new-policy-123"

    @pytest.mark.asyncio
    async def test_update_policy_with_history(self, firestore_service):
        mock_doc_ref = MagicMock()
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "name": "Old Name",
            "version": 1,
            "updatedAt": datetime.utcnow(),
            "createdBy": "admin"
        }
        mock_doc_ref.get.return_value = mock_doc
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        firestore_service.db.collection.return_value = mock_collection

        await firestore_service.update_policy("policy-123", {"name": "New Name"})

        mock_doc_ref.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_policy(self, firestore_service):
        mock_doc_ref = MagicMock()
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        firestore_service.db.collection.return_value = mock_collection

        await firestore_service.delete_policy("policy-123")

        mock_doc_ref.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_policy_history(self, firestore_service):
        history = [
            {"version": 1, "name": "V1"},
            {"version": 2, "name": "V2"}
        ]

        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"history": history}
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.get_policy_history("policy-123")

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_rollback_policy(self, firestore_service):
        history = [
            {"version": 1, "data": {"name": "V1"}, "updatedAt": datetime.utcnow()},
            {"version": 2, "data": {"name": "V2"}, "updatedAt": datetime.utcnow()}
        ]

        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "name": "Current",
            "version": 3,
            "history": history
        }
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        firestore_service.db.collection.return_value = mock_collection

        await firestore_service.rollback_policy("policy-123", 2)

        mock_doc_ref.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollback_policy_version_not_found(self, firestore_service):
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "version": 3,
            "history": []
        }
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc_ref
        firestore_service.db.collection.return_value = mock_collection

        with pytest.raises(ValueError):
            await firestore_service.rollback_policy("policy-123", 99)

class TestCleanupLogs:

    @pytest.mark.asyncio
    async def test_cleanup_old_logs(self, firestore_service):
        old_logs = []
        for i in range(5):
            doc = MagicMock()
            doc.id = f"old-log-{i}"
            doc.reference = MagicMock()
            old_logs.append(doc)

        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = old_logs
        mock_collection.where.return_value = mock_query
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.cleanup_old_logs(retention_days=90)

        assert result == 5

    @pytest.mark.asyncio
    async def test_cleanup_logs_custom_retention(self, firestore_service):
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_query.stream.return_value = []
        mock_collection.where.return_value = mock_query
        firestore_service.db.collection.return_value = mock_collection

        result = await firestore_service.cleanup_old_logs(retention_days=30)

        assert result == 0
