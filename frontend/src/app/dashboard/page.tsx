"use client"

import { useState, useEffect } from "react"
import { Shield, Activity, AlertTriangle, BarChart2, GitBranch, FileText, RefreshCw } from "lucide-react"
import { api, riskColor, actionColor } from "@/lib/api"
import type { DatasetStats, DetectAllResult, AccountScore, MuleRing } from "@/types"
import StatCard from "@/components/StatCard"
import AlertCard from "@/components/AlertCard"
import Badge from "@/components/Badge"
import LiveAlertTicker from "@/components/LiveAlertTicker"
import dynamic from "next/dynamic"

const ForceGraph = dynamic(() => import("@/components/ForceGraph"), { ssr: false })

const DEMO_ACCOUNTS = Array.from({ length: 12 }, (_, i) => ({
  account_id:       `ACC_${String(i + 1).padStart(6, "0")}`,
  account_age_days: i < 4 ? 8 + i * 3 : 100 + i * 50,
  kyc_verified:     true,
  kyc_score:        i < 4 ? 0.6 : 0.9,
  bank:             ["SBI","HDFC","ICICI","AXIS","PNB","BOI"][i % 6],
  city:             "Mumbai",
  device_id:        i < 3 ? "DEV-SHARED001" : `DEV-${i}`,
  jurisdiction:     i === 10 ? "AE" : "IN",
}))

const DEMO_TXNS = [
  ...Array.from({ length: 14 }, (_, i) => ({
    txn_id:               `TXN_${String(i + 1).padStart(6, "0")}`,
    sender_id:            `ACC_${String((i % 6) + 1).padStart(6, "0")}`,
    receiver_id:          `ACC_${String(((i + 1) % 6) + 1).padStart(6, "0")}`,
    amount:               48500 + i * 100,
    channel:              ["MOBILE_APP","UPI","UPI","ATM","NEFT","UPI","ATM"][i % 7],
    timestamp:            `2026-01-15T0${String(8 + Math.floor(i / 4)).padStart(2,"0")}:${String(i % 60).padStart(2,"0")}:00`,
    sender_jurisdiction:  "IN",
    receiver_jurisdiction: i > 10 ? "AE" : "IN",
    device_id:            i < 5 ? "DEV-SHARED001" : `DEV-${i}`,
    tor_ip:               false,
    scenario_tag:         i < 6 ? "S01" : "",
  })),
]

type Tab = "overview" | "alerts" | "graph" | "scores" | "reports"

export default function Dashboard() {
  const [stats,        setStats]        = useState<DatasetStats | null>(null)
  const [detectResult, setDetectResult] = useState<DetectAllResult | null>(null)
  const [scores,       setScores]       = useState<AccountScore[]>([])
  const [loading,      setLoading]      = useState(false)
  const [tab,          setTab]          = useState<Tab>("overview")
  const [apiStatus,    setApiStatus]    = useState<"checking"|"ok"|"error">("checking")

  useEffect(() => {
    api.health().then(() => setApiStatus("ok")).catch(() => setApiStatus("error"))
    api.stats().then(setStats).catch(() => {})
  }, [])

  const runDetection = async () => {
    setLoading(true)
    try {
      const [detectRes, scoreRes] = await Promise.all([
        api.detectAll({ accounts: DEMO_ACCOUNTS, transactions: DEMO_TXNS, threshold: 0.6 }),
        api.score({ accounts: DEMO_ACCOUNTS, transactions: DEMO_TXNS, threshold: 0.6 }),
      ])
      setDetectResult(detectRes)
      setScores(scoreRes.scores || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const graphNodes = DEMO_ACCOUNTS.map((a) => {
    const sc = scores.find((s) => s.account_id === a.account_id)
    return { id: a.account_id, is_mule: sc?.risk_level === "CRITICAL", score: sc?.mule_score }
  })
  const graphLinks = DEMO_TXNS.map((t) => ({
    source: t.sender_id, target: t.receiver_id, amount: t.amount,
  }))

  const totalAlerts = detectResult?.total_alerts || 0
  const rings       = detectResult?.detectors.rings.alerts       || []
  const structAlerts= detectResult?.detectors.structuring.alerts || []
  const jurAlerts   = detectResult?.detectors.jurisdiction.alerts|| []
  const highRisk    = detectResult?.gnn_high_risk || []

  return (
    <div className="min-h-screen" style={{ background: "#0f0f1e" }}>
      {/* ── Header ── */}
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between"
              style={{ background: "#1a1a2e" }}>
        <div className="flex items-center gap-3">
          <Shield className="text-red-500" size={28} />
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide">ShaktiSafe</h1>
            <p className="text-xs text-gray-400">Cross-Channel Mule Account Detection · GraphSAGE GNN</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 text-xs px-2 py-1 rounded border ${
            apiStatus === "ok"       ? "border-green-700 text-green-400" :
            apiStatus === "error"    ? "border-red-700 text-red-400" :
            "border-gray-700 text-gray-400"}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${apiStatus === "ok" ? "bg-green-400" : apiStatus === "error" ? "bg-red-400" : "bg-yellow-400"}`} />
            {apiStatus === "ok" ? "API Online" : apiStatus === "error" ? "API Offline" : "Checking…"}
          </div>
          <button onClick={runDetection} disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-red-800 hover:bg-red-700 text-white text-sm rounded-lg transition disabled:opacity-50">
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            {loading ? "Running…" : "Run Detection"}
          </button>
        </div>
      </header>

      {/* ── Tabs ── */}
      <nav className="border-b border-white/10 px-6 flex gap-1" style={{ background: "#1a1a2e" }}>
        {([
          ["overview", Activity,    "Overview"],
          ["alerts",   AlertTriangle,"Alerts"],
          ["graph",    GitBranch,   "Entity Graph"],
          ["scores",   BarChart2,   "GNN Scores"],
          ["reports",  FileText,    "Reports"],
        ] as const).map(([id, Icon, label]) => (
          <button key={id} onClick={() => setTab(id as Tab)}
            className={`flex items-center gap-1.5 px-4 py-3 text-sm border-b-2 transition ${
              tab === id
                ? "border-red-500 text-white"
                : "border-transparent text-gray-400 hover:text-gray-200"}`}>
            <Icon size={14} />{label}
          </button>
        ))}
      </nav>

      {/* ── Content ── */}
      <main className="p-6">

        {/* ── OVERVIEW ── */}
        {tab === "overview" && (
          <div className="space-y-6">
            {/* KPI row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Transactions Modelled" value="42,152"  sub="9 payment channels" color="blue" />
              <StatCard label="Fraud Scenarios"        value="12"       sub="All major AML typologies" color="gold" />
              <StatCard label="Amount Flagged"         value="INR 6.79 Cr" sub="Synthetic dataset" color="crimson" />
              <StatCard label="GNN Validation AUC"    value="0.98+"    sub="On synthetic data"  color="teal" />
            </div>
            {/* Live stats from API */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Accounts" value={stats.total_accounts.toLocaleString()} color="blue" />
                <StatCard label="Mule Accounts" value={`${stats.mule_accounts} (${stats.mule_rate_pct}%)`} color="crimson" />
                <StatCard label="Fraud Txns" value={stats.fraud_txns.toLocaleString()} color="gold" />
                <StatCard label="Channels Covered" value={stats.channels} color="teal" />
              </div>
            )}
            {/* Detection results */}
            {detectResult && (
              <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {Object.entries(detectResult.detectors).map(([key, val]) => (
                  <div key={key} className="bg-white/5 rounded-lg p-3 border border-white/10 text-center">
                    <div className="text-2xl font-bold text-red-400">{val.count}</div>
                    <div className="text-[10px] text-gray-400 uppercase mt-1">{key.replace(/_/g," ")}</div>
                  </div>
                ))}
              </div>
            )}
            {/* Timing */}
            {detectResult && (
              <div className="bg-white/5 border border-white/10 rounded-lg p-4 flex items-center gap-4">
                <div className="text-3xl font-bold text-green-400">{detectResult.elapsed_ms}ms</div>
                <div>
                  <div className="text-sm text-white">Full pipeline execution time</div>
                  <div className="text-xs text-gray-400">6 parallel detectors + GNN inference on {DEMO_ACCOUNTS.length} accounts</div>
                </div>
              </div>
            )}
            {!detectResult && (
              <div className="bg-white/5 rounded-lg p-8 text-center text-gray-500 border border-white/10">
                Press <strong className="text-white">Run Detection</strong> to execute the full ShaktiSafe pipeline
              </div>
            )}
            <LiveAlertTicker />
          </div>
        )}

        {/* ── ALERTS ── */}
        {tab === "alerts" && (
          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-300">
              {totalAlerts} Alerts Detected
            </h2>
            {rings.map((r, i) => (
              <AlertCard key={i} type="MULE_RING" action="BLOCK"
                confidence={r.confidence} amount={r.total_amount}
                accounts={r.accounts} evidence={r.evidence} />
            ))}
            {structAlerts.map((s, i) => (
              <AlertCard key={i} type={s.alert_type} action="FILE_STR"
                confidence={s.confidence} amount={s.total_amount} evidence={s.evidence} />
            ))}
            {jurAlerts.map((j, i) => (
              <AlertCard key={i} type="JURISDICTION_RISK" action={j.action}
                confidence={j.confidence} evidence={j.evidence} />
            ))}
            {highRisk.map((h, i) => (
              <AlertCard key={i} type="GNN_HIGH_RISK" action={h.action}
                confidence={h.confidence}
                evidence={h.risk_factors.slice(0,3).map((f) => `${f.factor}: ${(f.score*100).toFixed(0)}%`)} />
            ))}
            {totalAlerts === 0 && (
              <div className="text-gray-500 text-sm text-center py-8">No alerts — run detection first.</div>
            )}
          </div>
        )}

        {/* ── GRAPH ── */}
        {tab === "graph" && (
          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-300">
              Unified Entity Graph — {graphNodes.length} accounts, {graphLinks.length} transactions
            </h2>
            <ForceGraph nodes={graphNodes} links={graphLinks} width={900} height={500} />
          </div>
        )}

        {/* ── SCORES ── */}
        {tab === "scores" && (
          <div className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-300">
              GNN Account Scores
            </h2>
            {scores.length === 0 && (
              <div className="text-gray-500 text-sm text-center py-8">Run detection to see GNN scores.</div>
            )}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-gray-400 uppercase border-b border-white/10">
                    <th className="text-left py-2 pr-4">Account</th>
                    <th className="text-left py-2 pr-4">Score</th>
                    <th className="text-left py-2 pr-4">Risk</th>
                    <th className="text-left py-2 pr-4">Action</th>
                    <th className="text-left py-2">Top Risk Factor</th>
                  </tr>
                </thead>
                <tbody>
                  {scores.map((s, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                      <td className="py-2 pr-4 font-mono text-xs text-gray-300">{s.account_id}</td>
                      <td className="py-2 pr-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-white/10 rounded-full h-1.5">
                            <div className="h-1.5 rounded-full"
                                 style={{ width: `${s.mule_score * 100}%`,
                                          background: s.mule_score > 0.7 ? "#8b1a1a" : s.mule_score > 0.5 ? "#c17a00" : "#1a4a3c" }} />
                          </div>
                          <span className="text-xs">{(s.mule_score * 100).toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="py-2 pr-4">
                        <span className={`text-xs px-1.5 py-0.5 rounded border ${riskColor(s.risk_level)}`}>
                          {s.risk_level}
                        </span>
                      </td>
                      <td className="py-2 pr-4">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${actionColor(s.action)}`}>
                          {s.action}
                        </span>
                      </td>
                      <td className="py-2 text-xs text-gray-400">
                        {s.risk_factors[0]?.factor?.replace(/_/g," ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── REPORTS ── */}
        {tab === "reports" && (
          <div className="space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-300">
              FIU-IND STR Reports — Auto Generated
            </h2>
            <div className="bg-white/5 border border-white/10 rounded-lg p-6 text-center">
              <FileText size={32} className="mx-auto text-gray-500 mb-3" />
              <p className="text-gray-400 text-sm mb-4">
                Each detected event produces a regulator-ready STR with GNN confidence, evidence chain, and recommended actions.
              </p>
              <a href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/docs`}
                 target="_blank" rel="noopener noreferrer"
                 className="inline-block px-4 py-2 bg-teal-800 hover:bg-teal-700 text-white text-sm rounded-lg transition">
                View API Docs → POST /api/report/str
              </a>
            </div>
            {rings.slice(0, 3).map((r, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-white">Ring STR — {r.ring_id}</span>
                  <Badge label="FILE STR" variant="str" />
                </div>
                <div className="text-xs text-gray-400">
                  {r.account_count} accounts · INR {r.total_amount.toLocaleString("en-IN")} · Confidence {(r.confidence*100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        )}

      </main>
    </div>
  )
}
