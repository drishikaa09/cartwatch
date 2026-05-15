from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI()

@app.get("/")
def root():
    return {
        "project": "CartWatch",
        "status": "running",
        "message": "Real-time cart abandonment detection system",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
