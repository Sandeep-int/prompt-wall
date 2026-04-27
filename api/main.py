from fastapi import FastAPI
from pydantic import BaseModel
import sys
import time

# Import scanner
sys.path.insert(0, '/home/sandy/prompt-wall')
from detectors.vigil_scanner import VigilScanner

app = FastAPI(title="Prompt Shield API", version="0.1.0")
scanner = VigilScanner()

class CheckRequest(BaseModel):
    prompt: str
    metadata: dict = {}

class CheckResponse(BaseModel):
    verdict: str
    confidence: float
    layer_hit: str
    latency_ms: float
    details: dict

@app.post("/v1/check")
async def check_prompt(req: CheckRequest):
    """
    Multi-layer injection detection.
    Layer 1: Vigil (regex patterns)
    """
    start = time.time()
    vigil_result = scanner.scan(req.prompt)
    total_latency = (time.time() - start) * 1000
    
    if vigil_result["blocked"]:
        return CheckResponse(
            verdict="BLOCK",
            confidence=0.95,
            layer_hit="L1_VIGIL",
            latency_ms=total_latency,
            details={"hits": vigil_result["hits"]}
        )
    
    # Passed L1 - next weeks will add L2, L3, L4
    return CheckResponse(
        verdict="ALLOW",
        confidence=0.0,
        layer_hit="L1_PASS",
        latency_ms=total_latency,
        details={"message": "passed L1 scan"}
    )

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0", "layer": "L1_VIGIL"}

@app.get("/")
async def root():
    return {
        "service": "Prompt Shield",
        "month": 1,
        "current_layer": "Vigil (L1)",
        "status": "development"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
