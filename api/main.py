from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.insert(0, '/mnt/d/projects/prompt-wall')
from detectors.vigil_scanner import VigilScanner
from detectors.bert_classifier import BertClassifier

app = FastAPI()
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
async def check_prompt(req: CheckRequest):
    # L1: Vigil (fast regex)
    vigil_result = scanner.scan(req.prompt)
    if vigil_result["blocked"]:
        return CheckResponse(
            verdict="BLOCK",
            confidence=0.95,
            layer_hit="L1_VIGIL",
            latency_ms=vigil_result["latency_ms"],
            details={"hits": vigil_result["hits"]}
        )
    
    # L2: DistilBERT (semantic)
    bert_result = classifier.classify(req.prompt)
    if bert_result["is_injection"] and bert_result["confidence"] > 0.7:
        return CheckResponse(
            verdict="BLOCK",
            confidence=bert_result["confidence"],
            layer_hit="L2_BERT",
            latency_ms=bert_result["latency_ms"],
            details={"model_confidence": bert_result["confidence"]}
        )
    
    # Passed both layers
    return CheckResponse(
        verdict="ALLOW",
        confidence=0.0,
        layer_hit="L1_L2_PASS",
        latency_ms=vigil_result["latency_ms"] + bert_result["latency_ms"],
        details={}
    )

@app.get("/health")
async def health():
    return {"status": "ok", "layers": ["L1_VIGIL", "L2_BERT"]}
