from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psutil
from datetime import datetime

from db import init_db, get_recent_logs, get_recent_alerts, get_recent_metrics
from monitor import start_monitor, get_latest_metrics, get_latest_risk
from ai.model import get_model

app = FastAPI(title="Mini SIEM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    start_monitor()

# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.get("/status")
def status():
    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "monitoring": True,
    }

@app.get("/metrics")
def metrics():
    m = get_latest_metrics()
    if not m:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "mem_percent": psutil.virtual_memory().percent,
            "process_count": len(psutil.pids()),
            "net_connections": len(psutil.net_connections()),
            "active_users": [],
            "timestamp": datetime.utcnow().isoformat(),
        }
    return m

@app.get("/alerts")
def alerts(limit: int = 20):
    return get_recent_alerts(limit)

@app.get("/risk-score")
def risk_score():
    model = get_model()
    m = get_latest_metrics()
    risk = get_latest_risk()
    return {
        "risk_score": risk,
        "level": _risk_label(risk),
        "model_trained": model.trained,
        "samples_collected": len(model.baseline_data),
    }

@app.get("/logs")
def logs(limit: int = 50):
    return get_recent_logs(limit)

@app.get("/metrics/history")
def metrics_history():
    return get_recent_metrics(limit=60)

def _risk_label(score: float) -> str:
    if score < 3:   return "LOW"
    if score < 6:   return "MEDIUM"
    if score < 8:   return "HIGH"
    return "CRITICAL"
