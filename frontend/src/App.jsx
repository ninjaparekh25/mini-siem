import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const SEVERITY_COLOR = {
  HIGH: '#ef4444',
  CRITICAL: '#7c3aed',
  MEDIUM: '#f97316',
  LOW: '#22c55e',
  AI_ANOMALY: '#ef4444',
};

const RISK_COLOR = (score) => {
  if (score < 3) return '#22c55e';
  if (score < 6) return '#f97316';
  if (score < 8) return '#ef4444';
  return '#7c3aed';
};

function MetricCard({ label, value, unit, warn }) {
  return (
    <div style={{
      background: '#1e293b', borderRadius: 10, padding: '20px 24px',
      border: `1px solid ${warn ? '#ef4444' : '#334155'}`,
    }}>
      <div style={{ color: '#94a3b8', fontSize: 13, marginBottom: 6 }}>{label}</div>
      <div style={{ color: warn ? '#ef4444' : '#f1f5f9', fontSize: 32, fontWeight: 700 }}>
        {value}<span style={{ fontSize: 16, color: '#64748b' }}>{unit}</span>
      </div>
    </div>
  );
}

function RiskGauge({ score }) {
  const color = RISK_COLOR(score);
  const pct = (score / 10) * 100;
  return (
    <div style={{ background: '#1e293b', borderRadius: 10, padding: '20px 24px', border: `1px solid ${color}` }}>
      <div style={{ color: '#94a3b8', fontSize: 13, marginBottom: 10 }}>AI RISK SCORE</div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
        <span style={{ color, fontSize: 48, fontWeight: 800 }}>{score.toFixed(1)}</span>
        <span style={{ color: '#64748b', fontSize: 16 }}>/10</span>
      </div>
      <div style={{ marginTop: 10, background: '#0f172a', borderRadius: 4, height: 8 }}>
        <div style={{ width: `${pct}%`, height: 8, background: color, borderRadius: 4, transition: 'width 0.5s' }} />
      </div>
    </div>
  );
}

function AlertRow({ alert }) {
  const color = SEVERITY_COLOR[alert.severity] || '#94a3b8';
  return (
    <div style={{
      display: 'flex', gap: 12, alignItems: 'flex-start',
      padding: '10px 0', borderBottom: '1px solid #1e293b',
    }}>
      <span style={{
        background: color + '22', color, fontSize: 11, fontWeight: 700,
        padding: '2px 8px', borderRadius: 4, minWidth: 60, textAlign: 'center',
      }}>
        {alert.severity}
      </span>
      <div>
        <div style={{ color: '#e2e8f0', fontSize: 13 }}>{alert.description}</div>
        <div style={{ color: '#475569', fontSize: 11, marginTop: 2 }}>
          {alert.category} · {alert.timestamp}
        </div>
      </div>
    </div>
  );
}

function LogRow({ log }) {
  const colors = { ERROR: '#ef4444', WARN: '#f97316', INFO: '#22c55e' };
  return (
    <div style={{
      display: 'flex', gap: 10, fontSize: 12,
      padding: '5px 0', borderBottom: '1px solid #1e293b', fontFamily: 'monospace',
    }}>
      <span style={{ color: colors[log.level] || '#94a3b8', minWidth: 40 }}>{log.level}</span>
      <span style={{ color: '#64748b', minWidth: 60 }}>[{log.source}]</span>
      <span style={{ color: '#94a3b8' }}>{log.message}</span>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={{ background: '#0f172a', borderRadius: 12, padding: 20, border: '1px solid #1e293b' }}>
      <div style={{
        color: '#38bdf8', fontSize: 11, fontWeight: 700, letterSpacing: 2,
        marginBottom: 14, textTransform: 'uppercase',
      }}>{title}</div>
      {children}
    </div>
  );
}

export default function App() {
  const [metrics, setMetrics] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [risk, setRisk] = useState({ risk_score: 0, level: 'LOW', model_trained: false });
  const [status, setStatus] = useState('checking...');
  const [lastRefresh, setLastRefresh] = useState('');

  const fetchAll = async () => {
    try {
      const [m, a, l, r, s] = await Promise.all([
        fetch(`${API}/metrics`).then(r => r.json()),
        fetch(`${API}/alerts`).then(r => r.json()),
        fetch(`${API}/logs?limit=30`).then(r => r.json()),
        fetch(`${API}/risk-score`).then(r => r.json()),
        fetch(`${API}/status`).then(r => r.json()),
      ]);
      setMetrics(m);
      setAlerts(a);
      setLogs(l);
      setRisk(r);
      setStatus(s.status);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch {
      setStatus('offline');
    }
  };

  useEffect(() => {
    fetchAll();
    const iv = setInterval(fetchAll, 5000);
    return () => clearInterval(iv);
  }, []);

  return (
    <div style={{ minHeight: '100vh', background: '#020617', color: '#f1f5f9', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <div style={{
        padding: '16px 32px', background: '#0f172a',
        borderBottom: '1px solid #1e293b', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ fontSize: 22 }}>🛡️</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 18, color: '#f1f5f9' }}>SentinalX</div>
            <div style={{ fontSize: 11, color: '#475569' }}>AI-Powered Security Monitor · AMD Optimized</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: status === 'online' ? '#22c55e' : '#ef4444',
            }} />
            <span style={{ color: '#94a3b8', fontSize: 12 }}>
              Backend {status} · refreshed {lastRefresh}
            </span>
          </div>
          <div style={{
            background: risk.model_trained ? '#22c55e22' : '#f9731622',
            color: risk.model_trained ? '#22c55e' : '#f97316',
            padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700,
          }}>
            AI {risk.model_trained ? `✓ TRAINED (${risk.samples_collected} samples)` : `⟳ LEARNING (${risk.samples_collected}/20)`}
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div style={{ padding: '24px 32px', display: 'grid', gap: 20 }}>

        {/* Top row: metrics + risk */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr) 1.5fr', gap: 16 }}>
          <MetricCard
            label="CPU Usage"
            value={metrics.cpu_percent?.toFixed(1) ?? '--'}
            unit="%"
            warn={metrics.cpu_percent > 85}
          />
          <MetricCard
            label="Memory Usage"
            value={metrics.mem_percent?.toFixed(1) ?? '--'}
            unit="%"
            warn={metrics.mem_percent > 90}
          />
          <MetricCard
            label="Processes"
            value={metrics.process_count ?? '--'}
            unit=""
            warn={false}
          />
          <MetricCard
            label="Net Connections"
            value={metrics.net_connections ?? '--'}
            unit=""
            warn={metrics.net_connections > 100}
          />
          <RiskGauge score={risk.risk_score ?? 0} />
        </div>

        {/* Alerts + Logs */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
          <Section title={`⚠ Alerts (${alerts.length})`}>
            {alerts.length === 0
              ? <div style={{ color: '#475569', fontSize: 13 }}>No alerts — system normal</div>
              : alerts.slice(0, 10).map(a => <AlertRow key={a.id} alert={a} />)
            }
          </Section>
          <Section title="📋 Recent Logs">
            {logs.length === 0
              ? <div style={{ color: '#475569', fontSize: 13 }}>No logs yet</div>
              : logs.slice(0, 20).map(l => <LogRow key={l.id} log={l} />)
            }
          </Section>
        </div>

      </div>
    </div>
  );
}
