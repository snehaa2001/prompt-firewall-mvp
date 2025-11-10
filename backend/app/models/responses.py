from pydantic import BaseModel
from typing import List, Dict, Literal


class QueryResponse(BaseModel):
    decision: Literal["allow", "block", "redact", "warn"]
    originalPrompt: str
    modifiedPrompt: str
    llmResponse: str
    risks: List[Dict]
    explanations: List[str]
    severity: Literal["low", "medium", "high", "critical"]
    latency: float
    metadata: Dict
