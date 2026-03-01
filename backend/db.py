import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "siem.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            level TEXT,
            source TEXT,
            message TEXT
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            severity TEXT,
            category TEXT,
            description TEXT,
            resolved INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            cpu_percent REAL,
            mem_percent REAL,
            process_count INTEGER,
            net_connections INTEGER,
            risk_score REAL
        );
    """)
    conn.commit()
    conn.close()

def insert_log(level: str, source: str, message: str):
    conn = get_conn()
    conn.execute("INSERT INTO logs (level, source, message) VALUES (?, ?, ?)", (level, source, message))
    conn.commit()
    conn.close()

def insert_alert(severity: str, category: str, description: str):
    conn = get_conn()
    conn.execute("INSERT INTO alerts (severity, category, description) VALUES (?, ?, ?)", (severity, category, description))
    conn.commit()
    conn.close()

def insert_metrics(cpu: float, mem: float, procs: int, conns: int, risk: float):
    conn = get_conn()
    conn.execute(
        "INSERT INTO metrics (cpu_percent, mem_percent, process_count, net_connections, risk_score) VALUES (?,?,?,?,?)",
        (cpu, mem, procs, conns, risk)
    )
    conn.commit()
    conn.close()

def get_recent_logs(limit=50):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_alerts(limit=20):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_metrics(limit=1):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM metrics ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
