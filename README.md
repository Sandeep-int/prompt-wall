# Prompt Shield - Multi-layer AI Injection Detection

## Month 1: Layer 1 (Vigil - Regex patterns)

### Architecture
### Detection Coverage
- Direct prompt injection (`ignore previous instructions`)
- Jailbreak patterns (`DAN mode`)
- SQL injection attempts
- Encoding bypasses (hex, base64)

### Quick Start
```bash
source venv/bin/activate
pytest tests/test_vigil.py -v
python api/main.py
```

### API Endpoint
```bash
POST /v1/check
{
  "prompt": "user input here",
  "metadata": {}
}
```

### Response
```json
{
  "verdict": "BLOCK or ALLOW",
  "confidence": 0.95,
  "layer_hit": "L1_VIGIL",
  "latency_ms": 1.2,
  "details": {}
}
```

### Next: Layer 2 (DistilBERT - ML classifier)
