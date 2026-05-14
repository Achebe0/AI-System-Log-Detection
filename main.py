#!/usr/bin/env python3
"""
Main entry point with FastAPI server for health checks and monitoring.
This allows the agent to run with health endpoints in containerized environments.
"""

import sys
import os
import threading
import time
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import agent components
sys.path.insert(0, str(Path(__file__).parent))
from agent.agent import LogAgent

# FastAPI app
app = FastAPI(title="AI System Log Detection", version="1.0.0")

# Global agent instance
agent_instance = None
agent_thread = None


class AgentManager:
    """Manages the log agent lifecycle"""
    
    def __init__(self):
        self.agent = None
        self.thread = None
        self.running = False
        self.error = None
    
    def start(self, log_file: str):
        """Start the agent in a background thread"""
        try:
            self.agent = LogAgent(log_file)
            self.running = True
            
            def run_agent():
                try:
                    duration = int(os.getenv("DURATION", "10"))
                    poll_interval = float(os.getenv("POLL_INTERVAL", "0.5"))
                    self.agent.run(duration_seconds=duration, poll_interval=poll_interval)
                except Exception as e:
                    self.error = str(e)
                    self.running = False
            
            self.thread = threading.Thread(target=run_agent, daemon=True)
            self.thread.start()
        except Exception as e:
            self.error = str(e)
            self.running = False
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        return self.running and self.error is None
    
    def get_status(self) -> dict:
        """Get agent status"""
        return {
            "running": self.running,
            "healthy": self.is_healthy(),
            "error": self.error,
            "logs_seen": self.agent.monitor.logs_seen if self.agent else 0,
            "decisions_made": self.agent.reasoner.decisions_made if self.agent else 0,
        }


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent_instance
    log_file = os.getenv("LOG_FILE_PATH", "logs.jsonl")
    agent_instance = AgentManager()
    agent_instance.start(log_file)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if agent_instance:
        agent_instance.stop()


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestrators"""
    if agent_instance and agent_instance.is_healthy():
        return JSONResponse(
            {"status": "healthy", "message": "Agent is running"},
            status_code=200
        )
    else:
        error_msg = agent_instance.error if agent_instance else "Agent not initialized"
        return JSONResponse(
            {"status": "unhealthy", "error": error_msg},
            status_code=503
        )


@app.get("/status")
async def get_status():
    """Get detailed agent status"""
    if not agent_instance:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    return agent_instance.get_status()


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    if not agent_instance or not agent_instance.agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    agent = agent_instance.agent
    metrics_text = f"""# HELP log_detection_logs_seen Total logs processed
# TYPE log_detection_logs_seen counter
log_detection_logs_seen {agent.monitor.logs_seen}

# HELP log_detection_decisions_made Total decisions made
# TYPE log_detection_decisions_made counter
log_detection_decisions_made {agent.reasoner.decisions_made}

# HELP log_detection_latency_ms Average latency in milliseconds
# TYPE log_detection_latency_ms gauge
log_detection_latency_ms {sum(agent.latencies)/len(agent.latencies) if agent.latencies else 0}
"""
    
    return JSONResponse(
        content={"text": metrics_text},
        media_type="text/plain"
    )


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "AI System Log Detection",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health - Health check",
            "status": "/status - Agent status",
            "metrics": "/metrics - Prometheus metrics",
            "docs": "/docs - API documentation",
        }
    }


def main():
    """Run the FastAPI server"""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))
    
    print("\n" + "="*70)
    print("🚀 AI System Log Detection - Starting")
    print("="*70)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info",
        reload=os.getenv("RELOAD", "false").lower() == "true"
    )


if __name__ == "__main__":
    main()
