from fastapi import FastAPI, Request
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import sys
sys.path.insert(0, '/mnt/d/projects/prompt-wall')
from detectors.vigil_scanner import VigilScanner
from detectors.bert_classifier import BertClassifier

# Bouncer setup - tracks by IP
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

scanner = VigilScanner()
classifier = BertClassifier()

class CheckRequest(BaseModel):
    prompt: str

class CheckResponse(BaseModel):
    verdict: str
    confidence: float
    layer_hit: str
    latency_ms: float
    details: dict

@app.post("/v1/check")
@limiter.limit("10/minute")       # MAX 10 per minute per IP
async def check_prompt(request: Request, req: CheckRequest):
    vigil_result = scanner.scan(req.prompt)
    if vigil_result["blocked"]:
        return CheckResponse(
            verdict="BLOCK",
            confidence=0.95,
            layer_hit="L1_VIGIL",
            latency_ms=vigil_result["latency_ms"],
            details={"hits": vigil_result["hits"]}
        )
    bert_result = classifier.classify(req.prompt)
    if bert_result["is_injection"] and bert_result["confidence"] > 0.7:
        return CheckResponse(
            verdict="BLOCK",
            confidence=bert_result["confidence"],
            layer_hit="L2_BERT",
            latency_ms=bert_result["latency_ms"],
            details={"model_confidence": bert_result["confidence"]}
        )
    return CheckResponse(
        verdict="ALLOW",
        confidence=0.0,
        layer_hit="L1_L2_PASS",
        latency_ms=vigil_result["latency_ms"] + bert_result["latency_ms"],
        details={}
    )

@app.get("/health")
@limiter.limit("60/minute")       # Health check - relaxed limit
async def health(request: Request):
    return {"status": "ok", "layers": ["L1_VIGIL", "L2_BERT"]}