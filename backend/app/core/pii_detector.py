from typing import List, Dict
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

class PIIDetector:
    def __init__(self):
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()

        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()

    async def detect(self, text: str) -> List[Dict]:
        risks = []

        presidio_results = self.analyzer.analyze(
            text=text,
            language='en',
            entities=[
                "EMAIL_ADDRESS",     
                "PHONE_NUMBER",      
                "US_SSN",           
                "CREDIT_CARD",      
                "IP_ADDRESS",       
                "MEDICAL_LICENSE",  
                "US_PASSPORT",      
                "US_DRIVER_LICENSE",
                "US_BANK_NUMBER",   
                "IBAN_CODE"         
            ],
            score_threshold=0.75  
        )

        for result in presidio_results:
            original_text = text[result.start:result.end]
            risks.append({
                "type": "PII",
                "subtype": result.entity_type.lower(),
                "match": self._mask_presidio(original_text, result.entity_type),
                "original_match": original_text,
                "severity": self._get_severity(result.entity_type.lower()),
                "position": result.start,
                "confidence": result.score
            })

        return risks

    def redact(self, text: str, risks: List[Dict]) -> str:
        sorted_risks = sorted(risks, key=lambda x: x["position"], reverse=True)

        redacted_text = text
        for risk in sorted_risks:
            if risk["severity"] in ["medium", "high", "critical"]:
                original_match = risk.get("original_match", risk["match"])
                placeholder = f"[REDACTED_{risk['subtype'].upper()}]"
                redacted_text = redacted_text.replace(original_match, placeholder, 1)

        return redacted_text

    def _mask_presidio(self, value: str, entity_type: str) -> str:
        if len(value) <= 4:
            return "***"
        return value[:2] + "***" + value[-2:]

    def _get_severity(self, pii_type: str) -> str:
        severity_map = {
            "us_ssn": "critical",
            "credit_card": "critical",
            "us_passport": "critical",
            "us_driver_license": "critical",
            "us_bank_number": "critical",
            "iban_code": "critical",
            "medical_license": "critical",

            # Medium - Contact information
            "email_address": "medium",
            "phone_number": "medium",
            "ip_address": "medium"
        }
        return severity_map.get(pii_type, "medium")
