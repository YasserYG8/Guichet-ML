import time
from fastapi import FastAPI, HTTPException
from app.config import MODE, MODEL_ID, REVIEW_THRESHOLD
from app.providers import get_provider
from app.schemas import LanguageRequest, LanguageResponse

app = FastAPI(title="Guichet ML", version="1.0.0")
provider = get_provider(MODE)


@app.get("/health")
def health():
    return {"status": "ok", "mode": MODE, "provider": provider.name}


@app.post("/detect-language", response_model=LanguageResponse)
def detect_language(payload: LanguageRequest):
    debut = time.perf_counter()
    try:
        predictions = provider.detect_language(payload.text)
    except Exception as exc:
        raise HTTPException(503, "Service d'inference indisponible") from exc

    meilleur = max(predictions, key=lambda p: p.score)
    return LanguageResponse(
        provider=provider.name,
        model=MODEL_ID,
        latency_ms=round((time.perf_counter() - debut) * 1000, 1),
        language=meilleur.label,
        requires_review=meilleur.score < REVIEW_THRESHOLD,
        predictions=predictions,
    )
