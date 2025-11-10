import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import os

os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'

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
        mock_collection.stream.return_value = []
        mock_collection.document.return_value.get.return_value.to_dict.return_value = {}
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
    mock_user.return_value.custom_claims = {'role': 'admin'}

    return mock

@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer test-admin-token"}
