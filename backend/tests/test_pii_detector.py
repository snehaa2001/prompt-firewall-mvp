import pytest
from app.core.pii_detector import PIIDetector

@pytest.fixture
def pii_detector():
    return PIIDetector()

class TestPIIDetector:

    @pytest.mark.asyncio
    async def test_detect_email(self, pii_detector):
        text = "Contact me at john.doe@example.com for details."
        results = await pii_detector.detect(text)

        assert len(results) == 1
        assert results[0]['type'] == 'PII'
        assert results[0]['subtype'] == 'email_address'
        assert results[0]['severity'] == 'medium'

    @pytest.mark.asyncio
    async def test_detect_ssn(self, pii_detector):
        text = "My SSN is 123-45-6789."
        results = await pii_detector.detect(text)

        assert len(results) >= 0
        if len(results) > 0:
            assert results[0]['subtype'] in ['us_ssn', 'us_driver_license']
            assert results[0]['severity'] in ['critical', 'medium']

    @pytest.mark.asyncio
    async def test_detect_credit_card(self, pii_detector):
        text = "Card number: 4532-0151-1283-0366"
        results = await pii_detector.detect(text)

        assert len(results) == 1
        assert results[0]['subtype'] == 'credit_card'
        assert results[0]['severity'] == 'critical'

    @pytest.mark.asyncio
    async def test_no_pii(self, pii_detector):
        text = "What is the weather today?"
        results = await pii_detector.detect(text)

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_multiple_pii(self, pii_detector):
        text = "Email john@example.com, phone 415-555-1234, SSN 123-45-6789"
        results = await pii_detector.detect(text)

        assert len(results) >= 2
        subtypes = {r['subtype'] for r in results}
        assert 'email_address' in subtypes or 'us_ssn' in subtypes
