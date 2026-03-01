import psutil
import random
import time
import threading
from datetime import datetime
from db import insert_log, insert_alert, insert_metrics
from ai.model import get_model

# ──────────────────────────────────────────────
# Simulated threat state (for demo purposes)
# ──────────────────────────────────────────────
_sim_state = {
    "failed_logins": 0,
    "suspicious_proc": False,
    "port_scan_ips": {},      # ip → set of ports
    "conn_count_ips": {},     # ip → count
    "arp_anomaly": False,
}

def _simulate_threats():
    """Randomly inject simulated threats for demo."""
    while True:
        time.sleep(random.randint(15, 45))
        event = random.choice(["failed_login", "port_scan", "suspicious_proc", "arp"])
        if event == "failed_login":
            _sim_state["failed_logins"] += random.randint(1, 3)
        elif event == "port_scan":
            ip = f"192.168.1.{random.randint(10, 50)}"
            _sim_state["port_scan_ips"][ip] = set(random.sample(range(1, 65535), random.randint(6, 20)))
        elif event == "suspicious_proc":
            _sim_state["suspicious_proc"] = True
        elif event == "arp":
            _sim_state["arp_anomaly"] = True

def start_threat_simulator():
    t = threading.Thread(target=_simulate_threats, daemon=True)
    t.start()

# ──────────────────────────────────────────────
# Host Monitoring
# ──────────────────────────────────────────────
def collect_host_metrics() -> dict:
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    procs = len(psutil.pids())
    users = [u.name for u in psutil.users()]
    net = psutil.net_connections()
    net_count = len(net)

    return {
        "cpu_percent": cpu,
        "mem_percent": mem,
        "process_count": procs,
        "active_users": users,
        "net_connections": net_count,
        "timestamp": datetime.utcnow().isoformat(),
    }

def check_host_alerts(metrics: dict):
    alerts = []

    if metrics["cpu_percent"] > 85:
        alerts.append(("HIGH", "CPU", f"CPU usage critical: {metrics['cpu_percent']}%"))

    if _sim_state["failed_logins"] >= 5:
        alerts.append(("HIGH", "AUTH", f"Brute force detected: {_sim_state['failed_logins']} failed logins"))
        _sim_state["failed_logins"] = 0  # reset after alert

    if _sim_state["suspicious_proc"]:
        alerts.append(("MEDIUM", "PROCESS", "Suspicious process detected: netcat-like behavior"))
        _sim_state["suspicious_proc"] = False

    if metrics["net_connections"] > 100:
        alerts.append(("MEDIUM", "NETWORK", f"High outbound connections: {metrics['net_connections']}"))

    return alerts

# ──────────────────────────────────────────────
# Network Monitoring
# ──────────────────────────────────────────────
def check_network_alerts() -> list:
    alerts = []

    for ip, ports in list(_sim_state["port_scan_ips"].items()):
        if len(ports) > 5:
            alerts.append(("HIGH", "PORTSCAN", f"Port scan from {ip}: {len(ports)} ports probed"))
    _sim_state["port_scan_ips"].clear()

    if _sim_state["arp_anomaly"]:
        alerts.append(("MEDIUM", "ARP", "Suspicious ARP packet detected — possible ARP spoofing"))
        _sim_state["arp_anomaly"] = False

    return alerts

# ──────────────────────────────────────────────
# Main Monitor Loop
# ──────────────────────────────────────────────
_latest_metrics = {}
_latest_risk = 0.0

def get_latest_metrics():
    return _latest_metrics

def get_latest_risk():
    return _latest_risk

def monitor_loop():
    global _latest_metrics, _latest_risk
    model = get_model()

    while True:
        try:
            metrics = collect_host_metrics()
            _latest_metrics = metrics

            # Feed AI model
            model.add_sample(
                metrics["cpu_percent"],
                metrics["mem_percent"],
                metrics["process_count"],
                metrics["net_connections"],
            )
            result = model.predict(
                metrics["cpu_percent"],
                metrics["mem_percent"],
                metrics["process_count"],
                metrics["net_connections"],
            )
            _latest_risk = result["risk_score"]

            # Save to DB
            insert_metrics(
                metrics["cpu_percent"],
                metrics["mem_percent"],
                metrics["process_count"],
                metrics["net_connections"],
                result["risk_score"],
            )

            insert_log("INFO", "monitor", f"Metrics collected — CPU:{metrics['cpu_percent']}% MEM:{metrics['mem_percent']}%")

            if result["anomaly"]:
                insert_log("WARN", "ai", f"Anomaly detected — risk score: {result['risk_score']}")
                insert_alert("HIGH", "AI_ANOMALY", f"AI model flagged anomalous behavior. Risk: {result['risk_score']}/10")

            # Host alerts
            for sev, cat, desc in check_host_alerts(metrics):
                insert_alert(sev, cat, desc)
                insert_log("WARN", cat.lower(), desc)

            # Network alerts
            for sev, cat, desc in check_network_alerts():
                insert_alert(sev, cat, desc)
                insert_log("WARN", cat.lower(), desc)

        except Exception as e:
            insert_log("ERROR", "monitor", str(e))

        time.sleep(5)

def start_monitor():
    start_threat_simulator()
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()
