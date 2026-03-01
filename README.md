# 🛡️ Mini SIEM — AI-Powered Security Monitor

A hackathon-grade, demo-ready SIEM prototype with:
- Real host + simulated network monitoring
- Isolation Forest AI anomaly detection
- FastAPI backend + React dashboard
- SQLite storage · Docker setup
- AMD ROCm placeholder for GPU-ready AI

---

## 🗂 Project Structure

```
mini-siem/
├── cli/
│   ├── cli.py              # Click CLI: `monitor start`
│   └── setup.py
├── backend/
│   ├── main.py             # FastAPI app
│   ├── monitor.py          # Host + network monitor loop
│   ├── db.py               # SQLite helpers
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ai/
│       ├── model.py        # IsolationForest anomaly model
│       └── trainer.py      # Trainer + ROCm placeholder
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # React dashboard
│   │   └── index.js
│   ├── public/index.html
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start (5-Minute Demo)

### Option A: Docker (Recommended)

```bash
cd mini-siem
docker-compose up --build
```

Then open:
- **Dashboard:** http://localhost:3000
- **API:**       http://localhost:5000

---

### Option B: Local Dev (Faster iteration)

**Terminal 1 — Backend:**
```bash
cd mini-siem/backend
pip install -r requirements.txt
uvicorn main:app --port 5000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd mini-siem/frontend
npm install
npm start          # opens http://localhost:3000
```

**Terminal 3 — CLI (optional):**
```bash
cd mini-siem/cli
pip install click
python cli.py start
```

---

## 📊 API Endpoints

| Endpoint | Description |
|---|---|
| `GET /status` | Health check |
| `GET /metrics` | CPU, RAM, process count, net connections |
| `GET /alerts` | All alerts (newest first) |
| `GET /risk-score` | AI risk score 0–10 |
| `GET /logs` | Recent log entries |

---

## 🤖 AI Module

**Current:** scikit-learn `IsolationForest`
- Collects 20 baseline samples automatically
- Trains in-memory (no GPU needed)
- Outputs risk score 0–10

**AMD ROCm Placeholder:** `backend/ai/trainer.py`
- `AutoencoderPlaceholder` class ready for PyTorch
- Set `PYTORCH_ENABLED = True` when ROCm is available

---

## 🔔 Alert Rules

| Condition | Severity |
|---|---|
| CPU > 85% | HIGH |
| 5+ failed logins (simulated) | HIGH |
| Port scan (5+ ports from 1 IP) | HIGH |
| AI anomaly detected | HIGH |
| Suspicious process | MEDIUM |
| Net connections > 100 | MEDIUM |
| ARP spoofing packet | MEDIUM |

---

## 🎯 5-Minute Demo Script

1. `docker-compose up --build`
2. Open http://localhost:3000
3. Watch AI status badge: "LEARNING → TRAINED" (after ~20 polls)
4. Risk score animates based on real system load
5. Simulated threats fire every 15–45 seconds → alerts appear
6. Hit `GET http://localhost:5000/alerts` in browser to show API
7. Show `backend/ai/trainer.py` → ROCm placeholder

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `siem.db` | SQLite database path |
| `REACT_APP_API_URL` | `http://localhost:5000` | Backend URL for frontend |
