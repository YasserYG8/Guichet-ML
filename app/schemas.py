from pydantic import BaseModel, Field
class Prediction(BaseModel):
    label: str
    score: float = Field(ge=0, le=1)
    
class LanguageRequest(BaseModel):
    text: str = Field(min_length=3, max_length=1000)

class LanguageResponse(BaseModel):
    provider: str
    model: str
    latency_ms: float
    language: str
    requires_review: bool
    predictions: list[Prediction]

    