#!/usr/bin/env python3
import click
import subprocess
import sys
import os
import time

@click.group()
def monitor():
    """Mini SIEM - AI-Powered Security Monitor"""
    pass

@monitor.command()
def start():
    """Start monitoring service and dashboard"""
    click.echo("🚀 Starting Mini SIEM...")
    click.echo("🔍 Initializing host monitor...")
    click.echo("🤖 Loading AI anomaly model...")

    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"],
        cwd=os.path.abspath(backend_dir),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(2)
    click.echo("")
    click.echo("✅ Monitoring started...")
    click.echo("📊 Dashboard running at: http://localhost:3000")
    click.echo("🔌 API running at:       http://localhost:5000")
    click.echo("")
    click.echo("Press Ctrl+C to stop.")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        click.echo("\n🛑 Monitoring stopped.")

@monitor.command()
def status():
    """Check monitoring status"""
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:5000/status", timeout=2) as r:
            click.echo(f"✅ Backend online: {r.read().decode()}")
    except Exception:
        click.echo("❌ Backend is not running. Use: monitor start")

if __name__ == '__main__':
    monitor()
