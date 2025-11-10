from pydantic import BaseModel, Field
from typing import Optional, Literal

class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=10000)
    model: Optional[str] = Field(default="gpt-3.5-turbo")
    userId: Optional[str] = None
    tenantId: Optional[str] = Field(default="default")

class PolicyRequest(BaseModel):
    name: str
    type: Literal["pii", "injection", "custom"]
    pattern: str
    action: Literal["block", "redact", "warn"]
    severity: Literal["low", "medium", "high", "critical"]
    enabled: bool = True

class LogsQuery(BaseModel):
    limit: int = Field(default=50, le=500)
    offset: int = 0
    filterType: Optional[Literal["pii", "injection", "all"]] = "all"
    startDate: Optional[str] = None
    endDate: Optional[str] = None
