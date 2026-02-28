'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

// ── Types ──────────────────────────────────────────────────────────────────────
interface Stats {
  total_transactions: number;
  flagged_transactions: number;
  active_rings: number;
  blocked_amount: number;
  accounts_monitored: number;
  alert_count: number;
  live_tps?: number;
}

interface Alert {
  alert_id: string;
  timestamp: string;
  scenario: string;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  description: string;
  sender_id: string;
  receiver_id: string;
  amount: number;
  channel: string;
  confidence_score: number;
  recommended_action: string;
  evidence: {
    sender_risk: number;
    receiver_risk: number;
    top_risk_factor: string;
  };
}

interface Transaction {
  txn_id: string;
  sender_id: string;
  receiver_id: string;
  amount: number;
  channel: string;
  timestamp: string;
  label: string;
  scenario?: string;
}

interface Scenario {
  id: string;
  title: string;
  description: string;
  risk_level: string;
  confidence: number;
  accounts_involved: number;
  amount: number;
  channels: string[];
  key_indicators: string[];
}

// ── API Config ────────────────────────────────────────────────────────────────
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/live';

// ── Helpers ───────────────────────────────────────────────────────────────────
const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);

const formatTime = (ts: string) => {
  try {
    return new Date(ts).toLocaleTimeString('en-IN', { hour12: false });
  } catch { return ts; }
};

const riskColor = (level: string) => {
  switch (level) {
    case 'CRITICAL': return { bg: '#ff1a1a20', border: '#ff1a1a', text: '#ff4444', dot: '#ff1a1a' };
    case 'HIGH': return { bg: '#ff6b0020', border: '#ff6b00', text: '#ff8c00', dot: '#ff6b00' };
    case 'MEDIUM': return { bg: '#ffd70020', border: '#ffd700', text: '#ffd700', dot: '#ffd700' };
    default: return { bg: '#00ff8820', border: '#00ff88', text: '#00ff88', dot: '#00ff88' };
  }
};

const channelIcon = (ch: string) => {
  const icons: Record<string, string> = {
    MOBILE_APP: '📱', WEB: '🌐', ATM: '🏧', UPI: '⚡', NEFT: '🏦', IMPS: '⚡', SWIFT: '🌍',
  };
  return icons[ch] || '💳';
};

// ── Main Dashboard ────────────────────────────────────────────────────────────
export default function DashboardComponent() {
  const [stats, setStats] = useState<Stats>({
    total_transactions: 8073, flagged_transactions: 47, active_rings: 3,
    blocked_amount: 2830000, accounts_monitored: 523, alert_count: 5, live_tps: 67,
  });
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'alerts' | 'scenarios' | 'graph'>('overview');
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [clockTime, setClockTime] = useState('--:--:--');
  useEffect(() => {
    setClockTime(new Date().toLocaleTimeString('en-IN', { hour12: false }));
    const t = setInterval(() => setClockTime(new Date().toLocaleTimeString('en-IN', { hour12: false })), 1000);
    return () => clearInterval(t);
  }, []);
  const [liveTransactions, setLiveTransactions] = useState<Transaction[]>([]);
  const [pulseStats, setPulseStats] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const liveRef = useRef<HTMLDivElement>(null);

  // ── Fetch data ──────────────────────────────────────────────────────────────
  useEffect(() => {
    fetchData();
    connectWS();
    return () => wsRef.current?.close();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, alertsRes, scenariosRes] = await Promise.all([
        fetch(`${API_BASE}/api/stats`),
        fetch(`${API_BASE}/api/alerts?limit=20`),
        fetch(`${API_BASE}/api/scenarios`),
      ]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (alertsRes.ok) { const d = await alertsRes.json(); setAlerts(d.alerts || []); }
      if (scenariosRes.ok) { const d = await scenariosRes.json(); setScenarios(d.scenarios || []); }
    } catch (e) {
      // Use demo data if API not running
      setAlerts(DEMO_ALERTS);
      setScenarios(DEMO_SCENARIOS);
    }
  };

  const connectWS = () => {
    try {
      // Auto-detect correct WS URL based on current hostname
      const wsUrl = typeof window !== 'undefined'
        ? `ws://${window.location.hostname}:8000/ws/live`
        : WS_URL;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onopen = () => setWsStatus('connected');
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'transaction') {
          setLiveTransactions(prev => [msg.transaction, ...prev].slice(0, 15));
          if (msg.stats) { setStats(msg.stats); setPulseStats(true); setTimeout(() => setPulseStats(false), 500); }
          if (msg.alert) setAlerts(prev => [msg.alert, ...prev].slice(0, 20));
        }
      };
      ws.onclose = () => { setWsStatus('disconnected'); setTimeout(connectWS, 3000); };
      ws.onerror = () => setWsStatus('disconnected');
    } catch { setWsStatus('disconnected'); }
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div style={styles.root}>
      {/* Scanline overlay */}
      <div style={styles.scanlines} />

      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logo}>
            <span style={styles.logoIcon}>⬡</span>
            <div>
              <div style={styles.logoTitle}>INTELLITRACE</div>
              <div style={styles.logoSub}>Cross-Channel Mule Detection System · Indian Bank × VIT Chennai</div>
            </div>
          </div>
        </div>
        <div style={styles.headerRight}>
          <div style={styles.wsIndicator}>
            <div style={{ ...styles.wsDot, background: wsStatus === 'connected' ? '#00ff88' : '#ff4444',
              boxShadow: wsStatus === 'connected' ? '0 0 8px #00ff88' : 'none' }} />
            <span style={{ color: wsStatus === 'connected' ? '#00ff88' : '#ff4444', fontSize: 11 }}>
              {wsStatus === 'connected' ? 'LIVE' : 'OFFLINE'}
            </span>
          </div>
          <div style={styles.tpsBox}>
            <span style={styles.tpsNum}>{stats.live_tps || 67}</span>
            <span style={styles.tpsLabel}>TPS</span>
          </div>
          <div style={styles.clock}>{clockTime}</div>
        </div>
      </header>

      {/* Nav */}
      <nav style={styles.nav}>
        {(['overview', 'alerts', 'scenarios', 'graph'] as const).map(tab => (
          <button key={tab} style={{ ...styles.navBtn, ...(activeTab === tab ? styles.navBtnActive : {}) }}
            onClick={() => setActiveTab(tab)}>
            {tab === 'overview' ? '⬡ OVERVIEW' : tab === 'alerts' ? '⚠ ALERTS' : tab === 'scenarios' ? '🎯 SCENARIOS' : '🕸 GRAPH'}
          </button>
        ))}
      </nav>

      <main style={styles.main}>
        {activeTab === 'overview' && <OverviewTab stats={stats} pulseStats={pulseStats} liveTransactions={liveTransactions} alerts={alerts} />}
        {activeTab === 'alerts' && <AlertsTab alerts={alerts} />}
        {activeTab === 'scenarios' && <ScenariosTab scenarios={scenarios} selected={selectedScenario} onSelect={setSelectedScenario} />}
        {activeTab === 'graph' && <GraphTab />}
      </main>
    </div>
  );
}

// ── Overview Tab ──────────────────────────────────────────────────────────────
function OverviewTab({ stats, pulseStats, liveTransactions, alerts }: {
  stats: Stats; pulseStats: boolean; liveTransactions: Transaction[]; alerts: Alert[];
}) {
  return (
    <div style={styles.overviewGrid}>
      {/* Stat cards */}
      <div style={styles.statsRow}>
        <StatCard label="TRANSACTIONS MONITORED" value={stats.total_transactions.toLocaleString('en-IN')} sub="Last 72 hours" color="#00d4ff" icon="📊" pulse={pulseStats} />
        <StatCard label="MULE ACCOUNTS FLAGGED" value={stats.flagged_transactions.toString()} sub="+3 in last hour" color="#ff4444" icon="🎯" pulse={pulseStats} />
        <StatCard label="ACTIVE MULE RINGS" value={stats.active_rings.toString()} sub="Under investigation" color="#ff6b00" icon="⭕" pulse={pulseStats} />
        <StatCard label="AMOUNT BLOCKED" value={formatINR(stats.blocked_amount)} sub="Pre-disbursement" color="#ffd700" icon="🛡" pulse={pulseStats} />
        <StatCard label="ACCOUNTS MONITORED" value={stats.accounts_monitored.toLocaleString('en-IN')} sub="Across all channels" color="#a855f7" icon="👤" pulse={pulseStats} />
      </div>

      {/* Live feed + recent alerts */}
      <div style={styles.twoCol}>
        {/* Live transaction feed */}
        <div style={styles.panel}>
          <div style={styles.panelHeader}>
            <span>⚡ LIVE TRANSACTION FEED</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#00ff88',
                animation: 'pulse 1.5s infinite', boxShadow: '0 0 6px #00ff88' }} />
              <span style={{ fontSize: 10, color: '#00ff88' }}>STREAMING</span>
            </div>
          </div>
          <div style={styles.feedList}>
            {(liveTransactions.length > 0 ? liveTransactions : DEMO_LIVE_TXNS).map((txn, i) => (
              <LiveTxnRow key={i} txn={txn} />
            ))}
          </div>
        </div>

        {/* Recent alerts */}
        <div style={styles.panel}>
          <div style={styles.panelHeader}><span>🚨 RECENT ALERTS</span></div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {(alerts.length > 0 ? alerts : DEMO_ALERTS).slice(0, 5).map((a, i) => (
              <AlertRow key={i} alert={a} compact />
            ))}
          </div>
        </div>
      </div>

      {/* Channel breakdown */}
      <div style={styles.panel}>
        <div style={styles.panelHeader}><span>📡 CHANNEL RISK BREAKDOWN</span></div>
        <div style={styles.channelGrid}>
          {CHANNEL_STATS.map(ch => (
            <ChannelCard key={ch.name} {...ch} />
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Alerts Tab ────────────────────────────────────────────────────────────────
function AlertsTab({ alerts }: { alerts: Alert[] }) {
  const displayAlerts = alerts.length > 0 ? alerts : DEMO_ALERTS;
  return (
    <div style={styles.alertsPage}>
      <div style={styles.alertsHeader}>
        <div>
          <div style={{ fontSize: 20, fontWeight: 700, color: '#fff', fontFamily: 'var(--font-mono)' }}>FRAUD ALERTS</div>
          <div style={{ fontSize: 12, color: '#a0b4cc', marginTop: 4 }}>{displayAlerts.length} alerts • Ranked by confidence score</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {['CRITICAL', 'HIGH', 'MEDIUM'].map(level => {
            const c = riskColor(level);
            return (
              <div key={level} style={{ padding: '4px 10px', borderRadius: 4, border: `1px solid ${c.border}`,
                background: c.bg, color: c.text, fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                {displayAlerts.filter(a => a.risk_level === level).length} {level}
              </div>
            );
          })}
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {displayAlerts.map((alert, i) => <AlertRow key={i} alert={alert} />)}
      </div>
    </div>
  );
}

// ── Scenarios Tab ─────────────────────────────────────────────────────────────
function ScenariosTab({ scenarios, selected, onSelect }: {
  scenarios: Scenario[]; selected: Scenario | null; onSelect: (s: Scenario) => void;
}) {
  const displayScenarios = scenarios.length > 0 ? scenarios : DEMO_SCENARIOS;
  return (
    <div style={styles.scenariosPage}>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#fff', fontFamily: 'var(--font-mono)', marginBottom: 20 }}>
        🎯 DEMO SCENARIOS — 5 Real Fraud Patterns
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {displayScenarios.map((sc, i) => (
          <ScenarioCard key={i} scenario={sc} isSelected={selected?.id === sc.id} onClick={() => onSelect(sc)} />
        ))}
      </div>
      {selected && <ScenarioDetail scenario={selected} />}
    </div>
  );
}

// ── Graph Tab ─────────────────────────────────────────────────────────────────
function GraphTab() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const nodesRef = useRef<any[]>([]);
  const edgesRef = useRef<any[]>([]);
  const [hoveredNode, setHoveredNode] = useState<any>(null);
  const [selectedScenarioFilter, setSelectedScenarioFilter] = useState<string>('ALL');

  useEffect(() => {
    initGraph();
    return () => cancelAnimationFrame(animRef.current);
  }, [selectedScenarioFilter]);

  const initGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    const W = canvas.width, H = canvas.height;

    // Build nodes
    const nodeData = GRAPH_NODES.filter(n =>
      selectedScenarioFilter === 'ALL' || n.scenario === selectedScenarioFilter || n.type === 'LEGITIMATE'
    );

    // Position nodes using force-directed simulation seed
    const nodes = nodeData.map((n, i) => {
      const angle = (i / nodeData.length) * Math.PI * 2;
      const radius = n.type === 'MULE' ? 120 + Math.random() * 80 : 220 + Math.random() * 80;
      const cx = W / 2 + Math.cos(angle) * radius;
      const cy = H / 2 + Math.sin(angle) * radius;
      return {
        ...n,
        x: cx + (Math.random() - 0.5) * 40,
        y: cy + (Math.random() - 0.5) * 40,
        vx: 0, vy: 0,
        radius: n.type === 'MULE' ? 12 : 7,
      };
    });

    // Build edges
    const edges = GRAPH_EDGES.filter(e =>
      nodes.find(n => n.id === e.source) && nodes.find(n => n.id === e.target)
    ).map(e => ({
      ...e,
      sourceNode: nodes.find(n => n.id === e.source),
      targetNode: nodes.find(n => n.id === e.target),
      progress: Math.random(), // For animated particles
    }));

    nodesRef.current = nodes;
    edgesRef.current = edges;

    // Force simulation
    for (let iter = 0; iter < 100; iter++) {
      // Repulsion
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = 800 / (dist * dist);
          nodes[i].vx -= force * dx / dist;
          nodes[i].vy -= force * dy / dist;
          nodes[j].vx += force * dx / dist;
          nodes[j].vy += force * dy / dist;
        }
      }
      // Attraction (edges)
      edges.forEach(e => {
        if (!e.sourceNode || !e.targetNode) return;
        const dx = e.targetNode.x - e.sourceNode.x;
        const dy = e.targetNode.y - e.sourceNode.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = (dist - 80) * 0.05;
        e.sourceNode.vx += force * dx / dist;
        e.sourceNode.vy += force * dy / dist;
        e.targetNode.vx -= force * dx / dist;
        e.targetNode.vy -= force * dy / dist;
      });
      // Center gravity + damping
      nodes.forEach(n => {
        n.vx += (W / 2 - n.x) * 0.002;
        n.vy += (H / 2 - n.y) * 0.002;
        n.vx *= 0.85;
        n.vy *= 0.85;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(20, Math.min(W - 20, n.x));
        n.y = Math.max(20, Math.min(H - 20, n.y));
      });
    }

    // Animate
    const draw = () => {
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = '#050b14';
      ctx.fillRect(0, 0, W, H);

      // Draw edges
      edges.forEach(e => {
        if (!e.sourceNode || !e.targetNode) return;
        const isMule = e.label === 'MULE';
        const color = isMule ? '#ff444480' : '#ffffff15';
        ctx.beginPath();
        ctx.moveTo(e.sourceNode.x, e.sourceNode.y);
        ctx.lineTo(e.targetNode.x, e.targetNode.y);
        ctx.strokeStyle = color;
        ctx.lineWidth = isMule ? 1.5 : 0.5;
        ctx.stroke();

        // Animated particle on mule edges
        if (isMule) {
          e.progress = (e.progress + 0.008) % 1;
          const px = e.sourceNode.x + (e.targetNode.x - e.sourceNode.x) * e.progress;
          const py = e.sourceNode.y + (e.targetNode.y - e.sourceNode.y) * e.progress;
          ctx.beginPath();
          ctx.arc(px, py, 3, 0, Math.PI * 2);
          ctx.fillStyle = '#ff4444';
          ctx.shadowBlur = 8;
          ctx.shadowColor = '#ff4444';
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Draw nodes
      nodes.forEach(n => {
        const isMule = n.type === 'MULE';
        const scenarioColors: Record<string, string> = {
          CLASSIC_MULE_RING: '#ff1a1a',
          STRUCTURING: '#ff6b00',
          CROSS_JURISDICTION: '#ff00aa',
          NESTING: '#aa00ff',
          SANCTIONS_EVASION: '#ff0066',
        };
        const nodeColor = isMule ? (scenarioColors[n.scenario] || '#ff4444') : '#004488';

        // Glow for mule nodes
        if (isMule) {
          ctx.shadowBlur = 15;
          ctx.shadowColor = nodeColor;
        }

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = nodeColor;
        ctx.fill();
        ctx.strokeStyle = isMule ? '#ffffff40' : '#ffffff10';
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.shadowBlur = 0;

        // Label for mule nodes
        if (isMule) {
          ctx.fillStyle = '#ffffff';
          ctx.font = '8px monospace';
          ctx.textAlign = 'center';
          ctx.fillText(n.id.slice(-4), n.x, n.y + n.radius + 12);
        }
      });

      animRef.current = requestAnimationFrame(draw);
    };
    draw();
  };

  const SCENARIOS_FILTER = ['ALL', 'CLASSIC_MULE_RING', 'STRUCTURING', 'CROSS_JURISDICTION', 'NESTING', 'SANCTIONS_EVASION'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, height: '100%' }}>
      <div style={styles.panel}>
        <div style={styles.panelHeader}>
          <span>🕸 ENTITY GRAPH — Real-time Account Network</span>
          <div style={{ display: 'flex', gap: 8 }}>
            {SCENARIOS_FILTER.map(f => (
              <button key={f} onClick={() => setSelectedScenarioFilter(f)}
                style={{ padding: '3px 8px', borderRadius: 3, fontSize: 9, cursor: 'pointer', fontFamily: 'monospace',
                  background: selectedScenarioFilter === f ? '#00d4ff20' : 'transparent',
                  border: `1px solid ${selectedScenarioFilter === f ? '#00d4ff' : '#333'}`,
                  color: selectedScenarioFilter === f ? '#00d4ff' : '#666' }}>
                {f === 'ALL' ? 'ALL' : f.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
        <canvas ref={canvasRef} style={{ width: '100%', height: 460, background: '#070f1e', borderRadius: 8, display: 'block' }} />
        <div style={{ display: 'flex', gap: 20, marginTop: 12, flexWrap: 'wrap' }}>
          {[
            { color: '#ff1a1a', label: 'Classic Mule Ring' },
            { color: '#ff6b00', label: 'Structuring' },
            { color: '#ff00aa', label: 'Cross-Jurisdiction' },
            { color: '#aa00ff', label: 'Nesting' },
            { color: '#ff0066', label: 'Sanctions Evasion' },
            { color: '#004488', label: 'Legitimate' },
          ].map(item => (
            <div key={item.label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ width: 10, height: 10, borderRadius: '50%', background: item.color, boxShadow: `0 0 6px ${item.color}` }} />
              <span style={{ fontSize: 11, color: '#c8ddef' }}>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────
function StatCard({ label, value, sub, color, icon, pulse }: any) {
  return (
    <div style={{ ...styles.statCard, borderColor: `${color}40`, animation: pulse ? 'statPulse 0.5s ease' : 'none' }}>
      <div style={{ fontSize: 22, marginBottom: 8 }}>{icon}</div>
      <div style={{ fontSize: 28, fontWeight: 900, color, fontFamily: 'var(--font-mono)', letterSpacing: '-1px' }}>{value}</div>
      <div style={{ fontSize: 10, color: '#a0b4cc', textTransform: 'uppercase', letterSpacing: 1, marginTop: 4 }}>{label}</div>
      <div style={{ fontSize: 10, color: `${color}90`, marginTop: 2 }}>{sub}</div>
    </div>
  );
}

function LiveTxnRow({ txn }: { txn: Transaction }) {
  const isMule = txn.label === 'MULE';
  return (
    <div style={{ ...styles.liveTxnRow, borderLeftColor: isMule ? '#ff4444' : '#00ff8840',
      background: isMule ? '#ff111108' : 'transparent' }}>
      <span style={{ color: '#7a9ab8', fontSize: 10, minWidth: 60 }}>{formatTime(txn.timestamp)}</span>
      <span style={{ fontSize: 12 }}>{channelIcon(txn.channel)}</span>
      <span style={{ color: '#c8ddef', fontSize: 11, flex: 1 }}>{txn.sender_id?.slice(-6)}→{txn.receiver_id?.slice(-6)}</span>
      <span style={{ color: isMule ? '#ff4444' : '#00d4ff', fontSize: 11, fontFamily: 'monospace' }}>
        {formatINR(txn.amount)}
      </span>
      {isMule && <span style={{ background: '#ff444420', color: '#ff4444', border: '1px solid #ff444440',
        padding: '1px 5px', borderRadius: 3, fontSize: 9 }}>FLAGGED</span>}
    </div>
  );
}

function AlertRow({ alert, compact }: { alert: Alert; compact?: boolean }) {
  const c = riskColor(alert.risk_level);
  return (
    <div style={{ ...styles.alertRow, borderColor: `${c.border}40`, background: c.bg }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: compact ? 2 : 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: c.dot,
              boxShadow: `0 0 6px ${c.dot}`, flexShrink: 0 }} />
            <span style={{ color: c.text, fontSize: 10, fontFamily: 'monospace', fontWeight: 700 }}>{alert.risk_level}</span>
            <span style={{ color: '#7a9ab8', fontSize: 10 }}>•</span>
            <span style={{ color: '#a0b4cc', fontSize: 10 }}>{alert.scenario?.replace(/_/g, ' ')}</span>
            <span style={{ color: '#7a9ab8', fontSize: 10 }}>•</span>
            <span style={{ color: '#7a9ab8', fontSize: 10 }}>{formatTime(alert.timestamp)}</span>
          </div>
          <div style={{ color: '#eef4ff', fontSize: compact ? 11 : 12, lineHeight: 1.5 }}>{alert.description}</div>
          {!compact && (
            <div style={{ display: 'flex', gap: 16, marginTop: 8 }}>
              <div style={{ color: '#8aabcc', fontSize: 10 }}>
                <span style={{ color: '#c8ddef' }}>FROM: </span>{alert.sender_id}
              </div>
              <div style={{ color: '#8aabcc', fontSize: 10 }}>
                <span style={{ color: '#c8ddef' }}>TO: </span>{alert.receiver_id}
              </div>
              <div style={{ color: '#8aabcc', fontSize: 10 }}>
                <span style={{ color: '#c8ddef' }}>AMT: </span>
                <span style={{ color: '#00d4ff' }}>{formatINR(alert.amount)}</span>
              </div>
            </div>
          )}
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: compact ? 16 : 22, fontWeight: 900, color: c.text, fontFamily: 'monospace' }}>
            {Math.round(alert.confidence_score * 100)}%
          </div>
          <div style={{ fontSize: 9, color: '#8aabcc' }}>confidence</div>
          {!compact && (
            <div style={{ marginTop: 8, padding: '3px 8px', borderRadius: 3,
              background: alert.recommended_action === 'BLOCK' ? '#ff444430' : '#ff6b0030',
              border: `1px solid ${alert.recommended_action === 'BLOCK' ? '#ff4444' : '#ff6b00'}`,
              color: alert.recommended_action === 'BLOCK' ? '#ff4444' : '#ff6b00',
              fontSize: 10, fontFamily: 'monospace' }}>
              ⛔ {alert.recommended_action}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ScenarioCard({ scenario, isSelected, onClick }: { scenario: Scenario; isSelected: boolean; onClick: () => void }) {
  const c = riskColor(scenario.risk_level);
  return (
    <div onClick={onClick} style={{ ...styles.scenarioCard, borderColor: isSelected ? c.border : `${c.border}40`,
      background: isSelected ? c.bg : '#0a0f1a', cursor: 'pointer', transition: 'all 0.2s' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ color: c.text, fontSize: 11, fontFamily: 'monospace', fontWeight: 700 }}>{scenario.risk_level}</span>
        <span style={{ color: '#00d4ff', fontSize: 18, fontWeight: 900, fontFamily: 'monospace' }}>
          {Math.round(scenario.confidence * 100)}%
        </span>
      </div>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#fff', marginBottom: 6 }}>{scenario.title}</div>
      <div style={{ fontSize: 12, color: '#a0b4cc', lineHeight: 1.5, marginBottom: 12 }}>{scenario.description}</div>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        <div style={styles.badge}>👤 {scenario.accounts_involved} accounts</div>
        <div style={styles.badge}>{formatINR(scenario.amount)}</div>
        {scenario.channels.map(ch => (
          <div key={ch} style={styles.badge}>{channelIcon(ch)} {ch}</div>
        ))}
      </div>
    </div>
  );
}

function ScenarioDetail({ scenario }: { scenario: Scenario }) {
  const c = riskColor(scenario.risk_level);
  return (
    <div style={{ ...styles.panel, marginTop: 16, borderColor: `${c.border}60` }}>
      <div style={styles.panelHeader}><span>📋 SCENARIO DETAIL — {scenario.title}</span></div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div>
          <div style={{ fontSize: 12, color: '#a0b4cc', marginBottom: 8 }}>KEY INDICATORS</div>
          {scenario.key_indicators.map((ind, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: c.dot }} />
              <span style={{ color: '#ddeeff', fontSize: 12, fontFamily: 'monospace' }}>
                {ind.replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
          ))}
        </div>
        <div>
          <div style={{ fontSize: 12, color: '#a0b4cc', marginBottom: 8 }}>RECOMMENDED ACTIONS</div>
          {RECOMMENDED_ACTIONS[scenario.id]?.map((action, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6, alignItems: 'flex-start' }}>
              <span style={{ color: '#ffd700', fontSize: 11 }}>{i + 1}.</span>
              <span style={{ color: '#ddeeff', fontSize: 11 }}>{action}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ChannelCard({ name, txns, flagged, risk, icon }: any) {
  const pct = Math.round((flagged / txns) * 100);
  return (
    <div style={styles.channelCard}>
      <div style={{ fontSize: 20, marginBottom: 6 }}>{icon}</div>
      <div style={{ fontSize: 12, fontWeight: 700, color: '#fff' }}>{name}</div>
      <div style={{ fontSize: 11, color: '#a0b4cc', margin: '4px 0' }}>{txns.toLocaleString()} txns</div>
      <div style={{ fontSize: 11, color: '#ff4444' }}>{flagged} flagged ({pct}%)</div>
      <div style={{ marginTop: 8, height: 4, background: '#1a1a2e', borderRadius: 2 }}>
        <div style={{ height: '100%', borderRadius: 2, width: `${risk}%`,
          background: risk > 70 ? '#ff4444' : risk > 40 ? '#ff6b00' : '#00ff88' }} />
      </div>
    </div>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const styles: Record<string, any> = {
  root: { minHeight: '100vh', background: '#070f1e', color: '#e0e0e0', fontFamily: "'Courier New', monospace",
    position: 'relative', overflow: 'hidden' },
  scanlines: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, pointerEvents: 'none', zIndex: 100,
    background: 'repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px)' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px',
    borderBottom: '1px solid #0a2040', background: 'rgba(3,8,16,0.95)', backdropFilter: 'blur(10px)',
    position: 'sticky', top: 0, zIndex: 50 },
  headerLeft: { display: 'flex', alignItems: 'center', gap: 16 },
  logo: { display: 'flex', alignItems: 'center', gap: 12 },
  logoIcon: { fontSize: 28, color: '#00d4ff', textShadow: '0 0 20px #00d4ff' },
  logoTitle: { fontSize: 22, fontWeight: 900, color: '#00d4ff', letterSpacing: 4, textShadow: '0 0 20px #00d4ff' },
  logoSub: { fontSize: 9, color: '#7a9fc4', letterSpacing: 2, marginTop: 2 },
  headerRight: { display: 'flex', alignItems: 'center', gap: 16 },
  wsIndicator: { display: 'flex', alignItems: 'center', gap: 6, padding: '4px 10px',
    background: '#0f1e33', borderRadius: 4, border: '1px solid #1a3555' },
  wsDot: { width: 8, height: 8, borderRadius: '50%' },
  tpsBox: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '4px 10px',
    background: '#0f1e33', borderRadius: 4, border: '1px solid #1a3555' },
  tpsNum: { fontSize: 16, fontWeight: 900, color: '#00ff88', fontFamily: 'monospace' },
  tpsLabel: { fontSize: 9, color: '#6a8aaa' },
  clock: { fontSize: 13, color: '#557', fontFamily: 'monospace' },
  nav: { display: 'flex', padding: '0 24px', background: '#070f1e', borderBottom: '1px solid #1a3050' },
  navBtn: { padding: '12px 20px', background: 'transparent', border: 'none', color: '#6a8aaa',
    cursor: 'pointer', fontSize: 11, letterSpacing: 2, borderBottom: '2px solid transparent', transition: 'all 0.2s' },
  navBtnActive: { color: '#00d4ff', borderBottomColor: '#00d4ff' },
  main: { padding: '20px 24px', maxWidth: 1400, margin: '0 auto' },
  overviewGrid: { display: 'flex', flexDirection: 'column', gap: 20 },
  statsRow: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12 },
  statCard: { background: '#0d1829', border: '1px solid', borderRadius: 8, padding: '20px 16px',
    textAlign: 'center', transition: 'all 0.2s' },
  twoCol: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 },
  panel: { background: '#0d1829', border: '1px solid #1a3050', borderRadius: 8, padding: 20 },
  panelHeader: { fontSize: 11, color: '#7a9fc4', letterSpacing: 2, marginBottom: 16, paddingBottom: 10,
    borderBottom: '1px solid #1a3050', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  feedList: { display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 320, overflowY: 'auto' },
  liveTxnRow: { display: 'flex', alignItems: 'center', gap: 10, padding: '6px 10px',
    borderLeft: '3px solid', borderRadius: '0 4px 4px 0', fontSize: 11 },
  alertRow: { border: '1px solid', borderRadius: 6, padding: 14 },
  alertsPage: { display: 'flex', flexDirection: 'column', gap: 16 },
  alertsHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '12px 0', borderBottom: '1px solid #1a3050' },
  channelGrid: { display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12 },
  channelCard: { background: '#0d1829', border: '1px solid #1a3050', borderRadius: 6, padding: 12, textAlign: 'center' },
  scenariosPage: { display: 'flex', flexDirection: 'column', gap: 0 },
  scenarioCard: { border: '1px solid', borderRadius: 8, padding: 20 },
  badge: { padding: '3px 8px', background: '#0f1e33', border: '1px solid #1a3555',
    borderRadius: 4, fontSize: 10, color: '#8aabcc' },
};

// ── Demo Data ─────────────────────────────────────────────────────────────────
const DEMO_ALERTS: Alert[] = [
  { alert_id: 'ALT-001', timestamp: new Date().toISOString(), scenario: 'CLASSIC_MULE_RING',
    risk_level: 'CRITICAL', description: '🔴 Mule ring: App→Wallet→ATM chain, ₹2.3L moved in 4 mins, 6 accounts flagged',
    sender_id: 'MULE_RING1_01', receiver_id: 'MULE_RING1_06', amount: 230000, channel: 'MOBILE_APP',
    confidence_score: 0.97, recommended_action: 'BLOCK',
    evidence: { sender_risk: 97, receiver_risk: 94, top_risk_factor: 'velocity_anomaly' } },
  { alert_id: 'ALT-002', timestamp: new Date(Date.now()-120000).toISOString(), scenario: 'STRUCTURING',
    risk_level: 'HIGH', description: '🟠 Structuring: 12 txns × ₹49,500 just below RBI threshold — coordinated smurfing',
    sender_id: 'SMURF_01', receiver_id: 'SMURF_DEST_01', amount: 594000, channel: 'NEFT',
    confidence_score: 0.89, recommended_action: 'REVIEW',
    evidence: { sender_risk: 88, receiver_risk: 91, top_risk_factor: 'structuring_pattern' } },
  { alert_id: 'ALT-003', timestamp: new Date(Date.now()-300000).toISOString(), scenario: 'CROSS_JURISDICTION',
    risk_level: 'CRITICAL', description: '🔴 Cross-jurisdiction: India→Singapore→UAE routing, risk score 94/100',
    sender_id: 'XJUR_IN_01', receiver_id: 'XJUR_AE_01', amount: 850000, channel: 'SWIFT',
    confidence_score: 0.94, recommended_action: 'BLOCK',
    evidence: { sender_risk: 92, receiver_risk: 96, top_risk_factor: 'jurisdiction_risk' } },
  { alert_id: 'ALT-004', timestamp: new Date(Date.now()-600000).toISOString(), scenario: 'NESTING',
    risk_level: 'HIGH', description: '🟠 Nesting: 4-hop shell chain detected, ₹12L layered across accounts',
    sender_id: 'NEST_00', receiver_id: 'NEST_04', amount: 1200000, channel: 'IMPS',
    confidence_score: 0.82, recommended_action: 'REVIEW',
    evidence: { sender_risk: 85, receiver_risk: 82, top_risk_factor: 'deep_chain' } },
  { alert_id: 'ALT-005', timestamp: new Date(Date.now()-900000).toISOString(), scenario: 'SANCTIONS_EVASION',
    risk_level: 'CRITICAL', description: '🔴 Sanctions evasion: Behaviour matches sanctioned entity (device fingerprint match)',
    sender_id: 'SANC_EVADE_01', receiver_id: 'SANC_EVADE_02', amount: 500000, channel: 'NEFT',
    confidence_score: 0.91, recommended_action: 'BLOCK',
    evidence: { sender_risk: 94, receiver_risk: 89, top_risk_factor: 'device_fingerprint_match' } },
];

const DEMO_SCENARIOS: Scenario[] = [
  { id: 'CLASSIC_MULE_RING', title: 'Classic Mule Ring', risk_level: 'CRITICAL', confidence: 0.97,
    description: '6 accounts chain: App → Wallet → ATM. ₹2.3L moved in 4 minutes.',
    accounts_involved: 6, amount: 230000, channels: ['MOBILE_APP', 'UPI', 'ATM'],
    key_indicators: ['velocity_anomaly', 'cross_channel_movement', 'new_accounts', 'kyc_unverified'] },
  { id: 'STRUCTURING', title: 'Structuring / Smurfing', risk_level: 'HIGH', confidence: 0.89,
    description: '12 transactions × ₹49,500 to same destination — just below RBI ₹50,000 threshold.',
    accounts_involved: 4, amount: 594000, channels: ['NEFT', 'IMPS', 'UPI'],
    key_indicators: ['structuring_pattern', 'threshold_avoidance', 'coordinated_senders'] },
  { id: 'CROSS_JURISDICTION', title: 'Cross-Jurisdiction Routing', risk_level: 'CRITICAL', confidence: 0.94,
    description: 'India → Singapore → UAE chain. Jurisdiction risk score: 94/100.',
    accounts_involved: 4, amount: 850000, channels: ['NEFT', 'SWIFT'],
    key_indicators: ['jurisdiction_risk', 'high_risk_corridor', 'round_amounts', 'swift_routing'] },
  { id: 'NESTING', title: 'Nesting / Layering', risk_level: 'HIGH', confidence: 0.82,
    description: '4-hop shell account chain. Each hop takes a cut, obscuring origin.',
    accounts_involved: 5, amount: 1200000, channels: ['IMPS', 'NEFT', 'UPI'],
    key_indicators: ['deep_chain', 'amount_reduction', 'new_accounts', 'shell_accounts'] },
  { id: 'SANCTIONS_EVASION', title: 'Behaviour-Based Sanctions', risk_level: 'CRITICAL', confidence: 0.91,
    description: 'Passed KYC. But device + routing behaviour matches known sanctioned entity.',
    accounts_involved: 2, amount: 1200000, channels: ['NEFT', 'SWIFT'],
    key_indicators: ['device_fingerprint_match', 'round_numbers', 'immediate_withdrawal', 'aml_risk'] },
];

const DEMO_LIVE_TXNS: Transaction[] = Array.from({ length: 10 }, (_, i) => ({
  txn_id: `TXN-${i}`, sender_id: `ACC${100000 + i}`, receiver_id: `ACC${200000 + i}`,
  amount: [45000, 12500, 230000, 8900, 67000, 49500, 15000, 88000, 32000, 120000][i % 10], channel: ['MOBILE_APP', 'UPI', 'ATM', 'NEFT'][i % 4],
  timestamp: '2024-01-15T14:00:00.000Z', label: i === 2 ? 'MULE' : 'LEGITIMATE',
}));

const CHANNEL_STATS = [
  { name: 'MOBILE APP', txns: 2840, flagged: 18, risk: 65, icon: '📱' },
  { name: 'UPI', txns: 3120, flagged: 12, risk: 38, icon: '⚡' },
  { name: 'ATM', txns: 890, flagged: 9, risk: 72, icon: '🏧' },
  { name: 'NEFT', txns: 1240, flagged: 5, risk: 28, icon: '🏦' },
  { name: 'IMPS', txns: 980, flagged: 7, risk: 42, icon: '💸' },
  { name: 'SWIFT', txns: 120, flagged: 4, risk: 85, icon: '🌍' },
];

const RECOMMENDED_ACTIONS: Record<string, string[]> = {
  CLASSIC_MULE_RING: ['Freeze all 6 accounts immediately', 'File STR with FIU-IND within 7 days', 'Block associated devices', 'KYC re-verification for all ring members'],
  STRUCTURING: ['Flag destination account for enhanced monitoring', 'Review all senders for source of funds', 'File CTR if total > ₹10L', 'Investigate coordinator account'],
  CROSS_JURISDICTION: ['Escalate to PMLA cell', 'Request SWIFT message details', 'File with FIU-IND and ED', 'Block future SWIFT to AE corridors'],
  NESTING: ['Trace full 4-hop chain to origin', 'Identify shell company beneficial owners', 'Initiate account closure proceedings', 'Report to RBI'],
  SANCTIONS_EVASION: ['Immediate account freeze', 'File with OFAC/UN sanctions committee', 'Device fingerprint block across all channels', 'Law enforcement referral'],
};

// ── Graph Data ─────────────────────────────────────────────────────────────────
const GRAPH_NODES = [
  ...['MULE_RING1_01','MULE_RING1_02','MULE_RING1_03','MULE_RING1_04','MULE_RING1_05','MULE_RING1_06'].map(id => ({ id, type: 'MULE', scenario: 'CLASSIC_MULE_RING' })),
  ...['SMURF_01','SMURF_02','SMURF_03','SMURF_DEST_01'].map(id => ({ id, type: 'MULE', scenario: 'STRUCTURING' })),
  ...['XJUR_IN_01','XJUR_SG_01','XJUR_AE_01','XJUR_IN_02'].map(id => ({ id, type: 'MULE', scenario: 'CROSS_JURISDICTION' })),
  ...['NEST_00','NEST_01','NEST_02','NEST_03','NEST_04'].map(id => ({ id, type: 'MULE', scenario: 'NESTING' })),
  ...['SANC_EVADE_01','SANC_EVADE_02'].map(id => ({ id, type: 'MULE', scenario: 'SANCTIONS_EVASION' })),
  ...Array.from({ length: 25 }, (_, i) => ({ id: `ACC${100000 + i}`, type: 'LEGITIMATE', scenario: null })),
];

const GRAPH_EDGES = [
  { source: 'MULE_RING1_01', target: 'MULE_RING1_02', label: 'MULE', channel: 'MOBILE_APP' },
  { source: 'MULE_RING1_02', target: 'MULE_RING1_03', label: 'MULE', channel: 'UPI' },
  { source: 'MULE_RING1_03', target: 'MULE_RING1_04', label: 'MULE', channel: 'UPI' },
  { source: 'MULE_RING1_04', target: 'MULE_RING1_05', label: 'MULE', channel: 'ATM' },
  { source: 'MULE_RING1_04', target: 'MULE_RING1_06', label: 'MULE', channel: 'ATM' },
  { source: 'SMURF_01', target: 'SMURF_DEST_01', label: 'MULE', channel: 'NEFT' },
  { source: 'SMURF_02', target: 'SMURF_DEST_01', label: 'MULE', channel: 'IMPS' },
  { source: 'SMURF_03', target: 'SMURF_DEST_01', label: 'MULE', channel: 'UPI' },
  { source: 'XJUR_IN_01', target: 'XJUR_SG_01', label: 'MULE', channel: 'SWIFT' },
  { source: 'XJUR_SG_01', target: 'XJUR_AE_01', label: 'MULE', channel: 'SWIFT' },
  { source: 'XJUR_AE_01', target: 'XJUR_IN_02', label: 'MULE', channel: 'SWIFT' },
  { source: 'NEST_00', target: 'NEST_01', label: 'MULE', channel: 'IMPS' },
  { source: 'NEST_01', target: 'NEST_02', label: 'MULE', channel: 'NEFT' },
  { source: 'NEST_02', target: 'NEST_03', label: 'MULE', channel: 'UPI' },
  { source: 'NEST_03', target: 'NEST_04', label: 'MULE', channel: 'IMPS' },
  { source: 'SANC_EVADE_01', target: 'SANC_EVADE_02', label: 'MULE', channel: 'SWIFT' },
  ...Array.from({ length: 20 }, (_, i) => ({
    source: `ACC${100000 + i}`, target: `ACC${100001 + (i % 24)}`, label: 'LEGITIMATE', channel: 'UPI',
  })),
];
