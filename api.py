"""
Simple FastAPI server to serve logs via HTTP.
Can be used as a microservice for log ingestion.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
from pathlib import Path

app = FastAPI(title="Log API", version="1.0.0")


@app.get("/health")
def health():
    """Health check endpoint"""
    return JSONResponse({"status": "ok"})


@app.get("/logs")
def get_logs(limit: int = None, skip: int = 0):
    """
    Get logs from logs.jsonl
    
    Query parameters:
    - limit: Max number of logs to return
    - skip: Number of logs to skip
    """
    try:
        logs = []
        with open("/app/logs.jsonl", "r") as f:
            for i, line in enumerate(f):
                if i < skip:
                    continue
                if limit and len(logs) >= limit:
                    break
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return JSONResponse({
            "count": len(logs),
            "total": sum(1 for _ in open("/app/logs.jsonl")),
            "logs": logs
        })
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Logs file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/{log_id}")
def get_log(log_id: int):
    """Get a specific log by ID"""
    try:
        with open("/app/logs.jsonl", "r") as f:
            for i, line in enumerate(f):
                if i == log_id:
                    return JSONResponse(json.loads(line))
        raise HTTPException(status_code=404, detail="Log not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Logs file not found")


@app.post("/logs")
def add_log(log_data: dict):
    """Add a new log entry"""
    try:
        with open("/app/logs.jsonl", "a") as f:
            f.write(json.dumps(log_data) + "\n")
        return JSONResponse({"status": "created", "log": log_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    """API information"""
    return {
        "name": "Log API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /logs": "Get all logs",
            "GET /logs/{id}": "Get specific log",
            "POST /logs": "Add new log",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
