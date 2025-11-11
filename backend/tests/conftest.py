import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import os

os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
os.environ['ADMIN_CREATION_SECRET'] = 'change-this-secret-in-production'

@pytest.fixture(autouse=True)
def mock_error_reporting():
    with patch('google.cloud.error_reporting.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client.report_exception = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client

@pytest.fixture(autouse=True)
def mock_firebase_admin():
    with patch('app.services.firestore_service.firebase_admin') as mock:
        mock._apps = {}
        mock.initialize_app = MagicMock()
        yield mock

@pytest.fixture(autouse=True)
def mock_secrets():
    with patch('app.core.secrets.access_secret_version') as mock:
        mock.return_value = ''
        yield mock

@pytest.fixture(autouse=True)
def mock_firestore():
    with patch('app.services.firestore_service.firestore.Client') as mock:
        mock_client = MagicMock()
        mock_collection = MagicMock()

        # Mock where() to return self for chaining
        mock_where = MagicMock()
        mock_where.where.return_value = mock_where
        mock_where.stream.return_value = []
        mock_collection.where.return_value = mock_where

        mock_collection.stream.return_value = []
        mock_collection.document.return_value.get.return_value.to_dict.return_value = {}
        # Setup add() to return (None, doc_ref) tuple
        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "test-doc-id"
        mock_collection.add.return_value = (None, mock_doc_ref)
        mock_client.collection.return_value = mock_collection
        mock.return_value = mock_client
        yield mock

@pytest.fixture(autouse=True)
def mock_llm():
    with patch('app.services.llm_service.LLMService.generate_response', new_callable=AsyncMock) as mock:
        mock.return_value = "This is a test response."
        yield mock

@pytest.fixture(autouse=True)
def mock_anomaly_detector():
    with patch('app.core.anomaly_detector.firestore.Client') as mock:
        mock_client = MagicMock()
        mock_client.collection.return_value.where.return_value.order_by.return_value.limit.return_value.stream.return_value = []
        mock.return_value = mock_client
        yield mock

@pytest.fixture
def test_client():
    from app.main import app
    return TestClient(app)

@pytest.fixture
def mock_firebase_token(mocker):
    mock = mocker.patch('app.services.firebase_auth_service.firebase_auth.verify_id_token')
    mock.return_value = {
        'uid': 'test-user-123',
        'email': 'test@example.com'
    }

    mock_user = mocker.patch('app.services.firebase_auth_service.firebase_auth.get_user')
    mock_user.return_value.custom_claims = {'role': 'admin', 'tenantId': 'tenant-a'}

    return mock

@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer test-admin-token"}
