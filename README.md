# 🔍 INTELLITRACE
### Cross-Channel Mule Account Detection System
**IntelliTrace Hackathon 2026 · Indian Bank × VIT Chennai · PSBs Hackathon Series**

---

## 🎯 Problem Statement
Money mules operate across channels (Mobile App → Wallet → ATM) within minutes. Siloed fraud rules miss these high-velocity patterns. Traditional systems check transactions individually — IntelliTrace watches the **entire network** simultaneously.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSACTION SOURCES                       │
│         Mobile App │ Web │ ATM │ UPI │ NEFT │ SWIFT         │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Apache Kafka   │  Event Streaming
                    │  (Transaction    │  (Real-time ingestion)
                    │   Topics)        │
                    └────────┬────────┘
                             │
              ┌──────────────▼──────────────┐
              │    Spring Boot API Gateway   │
              │    (Auth + Rate Limiting)    │
              └──────────┬──────────────────┘
                         │
          ┌──────────────▼──────────────┐
          │       FastAPI ML Engine      │
          │                             │
          │  ┌─────────────────────┐    │
          │  │  GraphSAGE GNN      │    │  ← PyTorch Geometric
          │  │  (Node Scoring)     │    │    Inductive learning
          │  └─────────────────────┘    │
          │  ┌─────────────────────┐    │
          │  │  Mule Ring Detector │    │  ← Louvain community
          │  │  (Graph Community)  │    │    detection
          │  └─────────────────────┘    │
          │  ┌─────────────────────┐    │
          │  │  Velocity Analyzer  │    │  ← Sliding window
          │  │  Structuring Det.   │    │    anomaly detection
          │  │  Jurisdiction Score │    │
          │  └─────────────────────┘    │
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │         Neo4j Graph DB       │
          │   Accounts ←→ Transactions  │
          │   Devices  ←→ IPs           │  ← Native graph storage
          │   Jurisdictions ←→ Banks    │    Cypher ring queries
          └──────────────┬──────────────┘
                         │
          ┌──────────────▼──────────────┐
          │     Next.js Dashboard        │
          │  Live Graph Visualization   │
          │  Real-time Alert Feed       │  ← WebSocket streaming
          │  5 Demo Scenarios           │
          │  Regulator-ready Reports    │
          └─────────────────────────────┘
```

---

## 🚀 Quick Start (3 commands)

```bash
# 1. Clone
git clone https://github.com/YOUR_TEAM/intellitrace.git
cd intellitrace

# 2. Generate data + launch everything
make demo

# 3. Open dashboard
open http://localhost:3000
```

**That's it.** The entire stack launches with one command.

---

## 🎯 5 Demo Scenarios (Pre-loaded)

| # | Scenario | Pattern | Amount | Confidence |
|---|---|---|---|---|
| 1 | **Classic Mule Ring** | App→Wallet→ATM in 4 mins, 6 accounts | ₹2.3L | **97%** |
| 2 | **Structuring / Smurfing** | 12 × ₹49,500 below RBI threshold | ₹5.94L | **89%** |
| 3 | **Cross-Jurisdiction** | India→Singapore→UAE, risk 94/100 | ₹8.5L | **94%** |
| 4 | **Nesting / Layering** | 4-hop shell account chain | ₹12L | **82%** |
| 5 | **Sanctions Evasion** | Behaviour-match (not list-match) | ₹12L | **91%** |

---

## 🧠 Technical Highlights

### Real GNN (Not Fake)
- **GraphSAGE** (3-layer, inductive) — scores accounts never seen in training
- **Focal Loss** — handles extreme class imbalance (mule accounts = ~2% of data)
- **10 node features**: velocity, channel diversity, jurisdiction risk, KYC status, account age, etc.
- **72-hour sliding window graph** — real-time neighborhood updates

### What Judges Will See
- Live transaction stream with MULE/LEGITIMATE classification in real-time
- Interactive force-directed graph — click on rings to see full evidence
- 5 pre-loaded fraud scenarios with confidence scores
- Regulator-ready report generation per scenario
- All 6 expected outcomes from the problem statement addressed

---

## 📋 Expected Outcomes — Addressed

| Expected Outcome | Our Implementation |
|---|---|
| ✅ GNN-based real-time monitoring | GraphSAGE on PyTorch Geometric |
| ✅ Unified Entity Graph (App/Web/ATM/UPI) | Neo4j — all channels in one graph |
| ✅ Score relationships + transaction velocity | Edge features + VelocityAnalyzer |
| ✅ Identify + block mule rings in near real-time | Louvain community detection + block API |
| ✅ Structuring / fragmentation / nesting | StructuringDetector + nesting scenario |
| ✅ Jurisdiction-based risk scoring | JurisdictionScorer (10 jurisdictions) |
| ✅ Enhanced sanctions screening (behaviour-based) | Scenario 5 — not list-matching |
| ✅ Privacy-safe bank-to-bank intelligence sharing | Hashed account IDs in shared patterns |
| ✅ Real-time regulator-ready reports with confidence | PDF report generator with evidence chain |
| ✅ End-to-end visibility across payment rails | Dashboard — 6 channels unified |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| GNN | PyTorch Geometric (GraphSAGE) | Industry standard, inductive learning |
| Graph DB | Neo4j 5.15 | Native graph, Cypher ring detection |
| ML API | FastAPI + Uvicorn | Async, <100ms inference |
| API Gateway | Spring Boot 3 | Enterprise banking credibility |
| Streaming | Apache Kafka | Real-time, industry standard |
| Frontend | Next.js 14 + TypeScript | Type-safe, production-ready |
| Graph Viz | Canvas API (force-directed) | Renders 500+ nodes smoothly |
| Reports | WeasyPrint | PDF from HTML templates |
| Infra | Docker Compose | One-command demo |

---

## 📂 Project Structure

```
intellitrace/
├── ml-engine/          # Python — GNN brain
│   ├── gnn/            # GraphSAGE model + training + inference
│   ├── detection/      # Ring detector, velocity, structuring, jurisdiction
│   ├── data/           # Synthetic data generator (5 scenarios)
│   └── api/            # FastAPI server + WebSocket
├── backend/            # Java Spring Boot — API gateway
├── graph-db/           # Neo4j schema + Cypher queries
├── frontend/           # Next.js dashboard
├── kafka/              # Event streaming setup
├── docs/               # Architecture diagrams + demo script
├── docker-compose.yml  # Full stack
└── Makefile            # make demo → everything runs
```

---

## 👥 Team
**[Your Team Name]** · VIT Chennai

---

## 📄 License
MIT — Built for IntelliTrace Hackathon 2026
