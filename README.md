<div align="center">

<img src="https://img.shields.io/badge/PSBs_Hackathon_2026-Problem_Statement_1-1a1a2e?style=for-the-badge&labelColor=8B0000" />

# 🛡️ ShaktiSafe

### *Cross-Channel Mule Account Detection using Graph Neural Networks*

> A real-time fraud intelligence platform that builds a unified entity graph across all payment channels and applies GraphSAGE neural networks to identify mule rings **before funds are disbursed.**

<br/>

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch_Geometric-GNN-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch-geometric.readthedocs.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-ML_Engine-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.2-6DB33F?style=flat-square&logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-3.6-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org)
[![Docker](https://img.shields.io/badge/Docker_Compose-One_Command-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

<br/>

| 📊 42,152 Transactions | 🔍 12 Fraud Scenarios | 🏦 9 Payment Channels | 💰 INR 6.79 Cr Flagged |
|:---:|:---:|:---:|:---:|
| Modelled in synthetic dataset | All major AML typologies | Full cross-channel coverage | Detected in synthetic data |

<br/>

**VIT Bhopal · School of Computing · Team WebsiteCrash**

</div>

---

## 📌 Table of Contents

- [The Problem](#-the-problem)
- [Our Solution](#-our-solution)
- [System Architecture](#-system-architecture)
- [GNN Model](#-gnn-model--graphsage)
- [12 Fraud Scenarios](#-12-embedded-fraud-scenarios)
- [Detection Algorithms](#-detection-algorithms)
- [Regulatory Compliance](#-regulatory--compliance-coverage)
- [Tech Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Team](#-team)

---

## 🚨 The Problem

India lost **INR 11,333 Crore** to bank fraud in FY2023-24 (RBI). ~87% of financial fraud involves mule networks — legitimate account holders recruited to receive and rapidly forward illicit funds across multiple banks and payment channels to evade detection.

**The Cross-Channel Blind Spot:**

```
Mobile App     →     Linked Wallet     →     ATM Withdraw     →     Disperse
  Receive              Move                   Cash Out               Gone
  
  ✅ Passes           ✅ Passes               ✅ Passes           ❌ Too late
  all rules           all rules               all rules
```

> *"A documented mule ring completes in under 6 minutes — each transaction passes every rule-based check individually. No single channel team sees the full picture."*
> — PSBs Hackathon 2026, Problem Statement 2

Current AML systems operate in **silos**. The mobile banking team cannot see ATM patterns. The NEFT compliance officer cannot see UPI velocity. ShaktiSafe eliminates this blind spot entirely.

---

## 💡 Our Solution

ShaktiSafe ingests **all transaction streams** into a single Neo4j entity graph and runs **GraphSAGE inference** across the entire connected network simultaneously — not channel by channel.

| # | Pillar | What it does |
|---|--------|-------------|
| **01** | 🕸️ **Unified Entity Graph** | Every account, device, IP, bank, and jurisdiction is a node. Every transaction is a directed edge. Cross-channel correlation by design. |
| **02** | 🧠 **GraphSAGE Neural Network** | 3-layer inductive GNN trained on 42,152 synthetic transactions. Scores **new accounts without retraining** by aggregating neighbourhood features. |
| **03** | 🔍 **Parallel Detection Engine** | Six deterministic detectors run alongside the GNN: Mule Ring, Structuring, Jurisdiction, Device Fingerprint, Nesting Depth, Behavioural Sanctions. |
| **04** | 📋 **Compliance & Sharing Layer** | Auto-generated FIU-IND STR reports. Privacy-safe inter-bank sharing via SHA-256 hashed IDs. PMLA, RBI and FATF aligned. |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION (9 Rails)                        │
│  📱 Mobile App  🌐 Web Banking  🏧 ATM  📲 UPI/BHIM  💸 NEFT/IMPS      │
│                    RTGS  🌍 SWIFT  📄 NACH                              │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    EVENT STREAMING — Apache Kafka                        │
│  Account-partitioned · Replay-capable · Fault-tolerant · No data loss  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
┌─────────────────────────┐       ┌─────────────────────────────────────┐
│   GRAPH ENGINE — Neo4j  │       │      SPRING BOOT API GATEWAY         │
│  42,152 txn edges       │       │  Transaction ingestion · REST API    │
│  3,073 account nodes    │       │  Kafka producer · ML proxy          │
│  Cypher ring queries    │       └──────────────────┬──────────────────┘
└─────────────┬───────────┘                          │
              │                                      ▼
              └──────────────┐        ┌──────────────────────────────────┐
                             ▼        ▼         ML ENGINE — FastAPI       │
                   ┌───────────────────────────────────────────────────┐  │
                   │              GNN INFERENCE (GraphSAGE)            │  │
                   │  32 node features · 3 SAGEConv layers · <100ms   │  │
                   └───────────────────────┬───────────────────────────┘  │
                                           │                              │
              ┌────────────────────────────┼──────────────────────┐      │
              ▼                ▼           ▼           ▼           ▼      │
         🔴 BLOCK         🟡 REVIEW    📄 FILE     🏦 INTER     📊 ALERT │
         ACCOUNT          / FLAG        STR         BANK        GRAPH    │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    NEXT.JS REAL-TIME DASHBOARD                           │
│  Live alert ticker · Force-directed graph · STR reports · Stats         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Neo4j Property Graph Schema:**
```cypher
Account  -[TRANSACTS {amount, channel, timestamp}]→  Account
Account  -[SHARES_DEVICE]→                           Device
Device   -[LOCATED_IN]→                              Jurisdiction
Account  -[MANAGED_BY]→  Bank  -[OPERATES_IN]→      Jurisdiction
```

---

## 🧠 GNN Model — GraphSAGE

**32 Node Features per Account:**

| Range | Category | Key Features |
|-------|----------|-------------|
| F-0 to F-9 | **Account Level** | Account Age, KYC Status, Txn Velocity, Avg Amount, Channel Diversity, Receive Ratio, New Account Flag, Round Amounts, Velocity Proxy, KYC Risk |
| F-10 to F-19 | **Transaction Pattern** | Cross-Jurisdiction, High-Risk Juris., Structuring Signal, ATM Ratio, SWIFT Ratio, App-to-ATM, Shared Device, Amt Variability, Send/Recv Ratio, Tor IP Flag |
| F-20 to F-31 | **GraphSAGE Neighbourhood** | Neighbour Age/KYC, Degree/Out-Degree, Neighbour Activity, Edge Amounts, Fan-Out/Fan-In, Chain Node, In/Out Degree |

**Network Architecture:**
```
Input (32 features)
    → SAGEConv Layer 1  [64 hidden · BatchNorm · ReLU]
    → SAGEConv Layer 2  [128 dims · BN · ReLU · Residual]
    → SAGEConv Layer 3  [64 dims · BN · ReLU · Residual]
    → Dropout (0.3)
    → Classifier Head   [Mule probability 0.0–1.0]
```

**Training Configuration:**

| Parameter | Value |
|-----------|-------|
| Dataset | 48,396 txns · 1,875 accounts · 75 mule (4%) |
| Loss Function | Focal Loss (alpha=0.75, gamma=2.0) |
| Optimiser | Adam lr=0.005 · Cosine annealing · Grad clip 1.0 |
| Split | 70% train · 15% val · 15% test · stratified |

**Performance on Synthetic Dataset:**

| Metric | Score |
|--------|-------|
| 🎯 ROC-AUC | **0.98+** |
| 📊 F1 Score | **~0.95** |
| ⚡ False Positive Rate | **~2–5%** |
| 🔄 Convergence | **Stable** |

> ⚠️ Metrics are on controlled synthetic data where patterns are embedded by design. Real-world performance on live bank data will differ and requires field validation.

---

## 🎭 12 Embedded Fraud Scenarios

| ID | Severity | Scenario | Signal |
|----|----------|----------|--------|
| **S01** | 🔴 CRITICAL | **Classic Mule Ring** — 6 accounts: App→UPI×3→ATM×2, INR 3.8L in 6 min | Ring topology + velocity |
| **S02** | 🟠 HIGH | **Coordinated Smurfing** — 18 txns × INR 48,500–49,900 to Singapore below ₹50K threshold | Threshold-band clustering |
| **S03** | 🔴 CRITICAL | **Cross-Border SWIFT** — India→Singapore→UAE→Switzerland→India, 4-hop, AE on FATF grey list | Jurisdiction risk path scoring |
| **S04** | 🟠 HIGH | **Shell Nesting (6-Hop)** — INR 50L through 6 shells, 6 banks, 6 cities, each hop takes 10–15% cut | Multi-hop depth + cut ratio |
| **S05** | 🔴 CRITICAL | **Sanctions Evasion** — Passed KYC, not on any list — device fingerprint matches flagged entity | Behavioural fingerprint match |
| **S06** | 🟠 HIGH | **Carousel Fraud** — 8 accounts, funds circle back to origin, creates fictitious trade history | Circular flow detection |
| **S07** | 🔴 CRITICAL | **Mass ATM Cashout** — 1 source → 12 ATM mules simultaneously, INR 9,500–9,999 within 1 hour | Fan-out velocity burst detection |
| **S08** | 🟠 HIGH | **Trade-Based Laundering** — 5 over-invoiced phantom SWIFT exports to mask value transfer | Invoice anomaly + SWIFT flag |
| **S09** | 🟠 HIGH | **Loan Stacking** — 6 loans, same device, 4 banks, within 2 hours — classic bust-out fraud | Shared device + timing correlation |
| **S10** | 🟠 HIGH | **Crypto Off-Ramp** — 5 P2P crypto exchanges → aggregation → SWIFT exit to Hong Kong | Aggregation + SWIFT exit |
| **S11** | 🟠 HIGH | **Salary Diversion** — 40 salaries via NACH redirected to 8 mule accounts opened <15 days ago | NACH anomaly + new account flag |
| **S12** | 🟠 HIGH | **Dark Web Carding** — 30 txns, single IP, 6 wallets, avg INR 3,200, stolen card cashout | Single-IP burst + wallet pattern |

---

## 🔍 Detection Algorithms

**Mule Ring — Louvain Community Detection:**
```
Load 90-day window → Build weighted directed graph
→ Run Louvain community detection
→ Community Score ≥ 0.65? → YES: BLOCK + FILE STR | NO: MONITOR
```

**Structuring — Threshold Band Analysis:**
```
Scan rolling 24-hour window → Filter: INR 45,000–49,999 band
→ Group by receiver + time window
→ Same dest. ≥ 3 txns? + Multiple coordinated senders? → FILE CTR
```

**Jurisdiction Risk — FATF Matrix (20 countries):**
```
Score = Σ(hop risks) + corridor penalty
Score > 60 → HIGH RISK FLAG
Score > 80 → BLOCK
```

| Jurisdiction | Risk | Status |
|---|---|---|
| India (IN) | 8–10 | Domestic |
| Singapore (SG) | 42 | FATF Member |
| UAE (AE) | 65 | FATF Grey List |
| Panama (PA) | 78 | Grey List |

**Behavioural Sanctions — Beyond KYC Lists:**
```
KYC Status:      PASS — not on sanctions list
Device ID:       MATCH — hash matches flagged entity  ← catches them here
Transfer:        Round amounts: 100K, 500K, 1M
Withdrawal:      < 5 min after receipt
→ Behaviour Score: 91 / Threshold: 70 → ESCALATE TO COMPLIANCE
```

---

## ⚖️ Regulatory & Compliance Coverage

| Regulation | Requirement | ShaktiSafe Implementation | Status |
|---|---|---|---|
| PMLA 2002, Sec 12 | Records + STR within 7 days | Auto-generated STR per pattern with evidence chain | ✅ COVERED |
| RBI KYC Master Dir. 2023 | KYC verification, enhanced due diligence | KYC status = node feature F-1 in GNN | ✅ COVERED |
| FIU-IND STR Requirements | STR with evidence and rationale | PDF: evidence chain + confidence score + actions | ✅ COVERED |
| FATF Recommendation 16 | Wire transfer transparency | 20-jurisdiction FATF matrix + SWIFT hop tracking | ✅ COVERED |
| FATF Rec. 1 — Risk-Based | Risk-based approach to AML/CFT | GNN probability score = quantified risk output | ✅ COVERED |
| IBA AML Guidelines 2024 | Inter-bank intelligence sharing | SHA-256 hashed IDs + amount bucketing API | ✅ COVERED |
| RBI Cybersecurity Framework | Device-level fraud signals | Device fingerprint as dedicated entity node | ✅ COVERED |
| GDPR / RBI Data Localisation | Account ID privacy in shared reports | Account IDs hashed before any external export | ✅ COVERED |
| FEMA | Monitor outward remittances | SWIFT node tracking + jurisdiction hop scoring | ✅ COVERED |
| RBI AML Guidelines | Transaction monitoring, velocity checks | Velocity = F-2; rolling 24hr and 90-day windows | ✅ COVERED |

**Privacy-Safe Inter-Bank Sharing:**
```python
anonymized_id      = SHA256(account_id)[:16]    # Not reversible
txn_count_bucket   = len(txns) // 10 * 10       # Round to nearest 10
avg_amount_bucket  = round(mean_amount, -4)      # Round to nearest INR 10,000
fingerprint_hash   = SHA256(JSON(behaviour))     # Deterministic match key — no PII
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| 🧠 **GNN** | PyTorch Geometric — GraphSAGE | Inductive mule probability scoring |
| 🕸️ **Graph DB** | Neo4j 5.x | Unified entity graph, Cypher ring queries |
| ⚡ **ML API** | FastAPI + Uvicorn | Inference server, WebSocket streaming |
| 📨 **Streaming** | Apache Kafka 3.6 | Transaction event bus, forensic replay |
| 🌐 **Gateway** | Spring Boot 3.2 + Java 21 | API orchestration, Kafka producer |
| 💻 **Frontend** | Next.js 14 + TypeScript + Tailwind | Real-time dashboard |
| 🐳 **Deployment** | Docker Compose | One-command full-stack deploy |
| 📄 **Reports** | ReportLab / WeasyPrint | Auto FIU-IND STR PDF generation |
| 🔒 **Privacy** | SHA-256 + Bucketing | GDPR-safe inter-bank fingerprinting |

---

## 🚀 Quick Start

**Prerequisites:** Docker + Docker Compose installed

```bash
# 1. Clone the repo
git clone https://github.com/akshat440/ShaktiSafe.git
cd ShaktiSafe

# 2. One command to launch everything
docker-compose up --build
```

Wait ~60 seconds for all services to start, then:

| Service | URL | Credentials |
|---|---|---|
| 📊 **Dashboard** | http://localhost:3000 | — |
| 🌐 **Gateway API** | http://localhost:8080/api/v1 | — |
| 🔬 **ML Engine** | http://localhost:8000 | — |
| 📚 **API Docs** | http://localhost:8000/docs | — |
| 🕸️ **Neo4j Browser** | http://localhost:7474 | neo4j / intellitrace2026 |
| 📨 **Kafka UI** | http://localhost:8090 | — |

**Useful Make commands:**
```bash
make demo          # Launch full Docker stack
make test          # Smoke test all endpoints
make logs          # Tail all container logs
make logs-ml       # ML Engine logs only
make logs-gateway  # Spring Boot gateway logs only
make data          # Regenerate synthetic data
make train         # Retrain GNN model
make report        # Generate sample STR report
make stop          # Stop all containers
make clean         # Tear down + wipe volumes
```

---

## 📡 API Reference

### Spring Boot Gateway — `http://localhost:8080/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transactions` | Ingest a single transaction |
| `POST` | `/transactions/batch` | Ingest batch (up to 500) |
| `POST` | `/transactions/analyze` | Ingest + synchronous ML risk score |
| `GET` | `/stats` | Dashboard statistics |
| `GET` | `/graph` | Transaction graph for D3 visualization |
| `GET` | `/alerts` | Recent fraud alerts |
| `GET` | `/accounts` | Account risk scores |
| `GET` | `/health` | Service health check |

**Example — Ingest a transaction:**
```bash
curl -X POST http://localhost:8080/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "ACC001",
    "receiver_id": "ACC002",
    "amount": 49999,
    "channel": "UPI",
    "sender_country": "IN",
    "receiver_country": "SG"
  }'
```

**Example — Get real-time risk score:**
```bash
curl -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{"sender_id":"ACC001","receiver_id":"ACC002","amount":49500,"channel":"UPI"}'
```

### ML Engine Direct — `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stats` | Fraud detection statistics |
| `GET` | `/graph` | Full entity graph data |
| `GET` | `/alerts` | All fraud alerts |
| `GET` | `/accounts` | Scored account list |
| `POST` | `/analyze` | Direct GNN inference |
| `WS` | `/ws/live` | Real-time alert WebSocket stream |

---

## 📁 Project Structure

```
ShaktiSafe/
├── 🐳 docker-compose.yml          # Full stack — one command deploy
├── 📋 Makefile                    # Developer shortcuts
│
├── 🧠 ml-engine/                  # Python FastAPI + GNN
│   ├── gnn/
│   │   ├── model.py               # GraphSAGE 3-layer architecture
│   │   ├── train.py               # Focal loss + cosine annealing
│   │   └── inference.py           # Runtime scoring
│   ├── detection/
│   │   ├── mule_ring_detector.py  # Louvain community detection
│   │   ├── structuring_detector.py# Threshold band analysis
│   │   ├── jurisdiction_scorer.py # 20-country FATF matrix
│   │   ├── device_fingerprint.py  # Hash matching
│   │   ├── nesting_depth.py       # Multi-hop shell chain
│   │   └── sanctions_screener.py  # Behavioural screening
│   ├── data/
│   │   └── generator.py           # 42,152 synthetic transactions
│   ├── reports/
│   │   └── report_generator.py    # Auto FIU-IND STR PDF
│   └── api/
│       └── main.py                # FastAPI + WebSocket endpoints
│
├── 🌐 backend/                    # Spring Boot API Gateway
│   └── src/main/java/com/shaktisafe/gateway/
│       ├── controller/            # REST endpoints
│       ├── service/               # Kafka + ML proxy
│       ├── config/                # Kafka topics + WebClient
│       └── model/                 # Transaction + FraudAlert
│
├── 💻 frontend/                   # Next.js 14 Dashboard
│   └── src/
│       ├── app/dashboard/         # Main dashboard page
│       ├── components/
│       │   ├── ForceGraph.tsx     # D3 force-directed graph
│       │   ├── LiveAlertTicker.tsx# WebSocket live feed
│       │   ├── AlertCard.tsx      # Alert display
│       │   ├── StatCard.tsx       # Metric cards
│       │   └── Badge.tsx          # Severity badges
│       └── lib/api.ts             # API client
│
├── 🕸️ graph-db/
│   ├── init/schema.cypher         # Neo4j schema + indexes
│   └── queries/mule_ring_detection.cypher
│
└── 📨 kafka/
    └── init-topics.sh             # Creates all 4 Kafka topics
```

---

## 📊 Dataset Facts

| Metric | Value |
|--------|-------|
| Transactions in dataset | 42,152 |
| Account nodes | 3,073 |
| Mule accounts (2.4%) | 73 |
| Embedded fraud scenarios | 12 |
| Payment channels covered | 9 |
| Jurisdictions in FATF matrix | 20 |
| GNN model parameters | 156,326 |
| Validation AUC (synthetic) | 0.98+ |
| Full-graph inference | Est. < 80ms |
| Parallel detectors | 6 |
| Total flagged (synthetic) | INR 6.79 Cr |
| Privacy method | SHA-256 + Bucketing |

---

## 👥 Team

<table>
<tr>
<td align="center" width="33%">
<br/>
<b>Vidhi Luniya</b>
<br/>
<i>Team Leader</i>
<br/>
<sub>VIT Bhopal · School of Computing</sub>
</td>
<td align="center" width="33%">
<br/>
<b>Akshat Singh Tomar</b>
<br/>
<i>Member</i>
<br/>
<sub>VIT Bhopal · School of Computing</sub>
<br/>
<a href="https://github.com/akshat440">
<img src="https://img.shields.io/badge/GitHub-akshat440-181717?style=flat-square&logo=github"/>
</a>
</td>
<td align="center" width="33%">
<br/>
<b>Anushka Pareek</b>
<br/>
<i>Member</i>
<br/>
<sub>VIT Bhopal · School of Computing</sub>
</td>
</tr>
</table>

<br/>

| Field | Details |
|---|---|
| 🏫 **Institution** | VIT Bhopal University |
| 🏛️ **Department** | School of Computing |
| 👥 **Team Name** | WebsiteCrash |
| 🏆 **Competition** | PSBs Hackathon 2026 |
| 📋 **Problem Statement** | Statement 2 — Cross-Channel Mule Account Detection |
| 🔄 **Round** | Idea Submission |

---

## 🔮 Expected Outcomes

| Metric | Target |
|--------|--------|
| ⚡ Ring detection latency | **< 100ms** |
| 🎯 Fraud patterns covered | **12** |
| 🏦 Payment channels | **9 Rails** |
| 📄 STR auto-generation | **< 1 second** |
| 🔒 Privacy method | **SHA-256 + Bucketing** |
| 📊 GNN AUC | **0.98+ (synthetic)** |

---

<div align="center">

### *One Graph. Every Channel. Real Time.*
### *Before Disbursement. Explained. Compliant.*

<br/>

[![Made with ❤️ at VIT Bhopal](https://img.shields.io/badge/Made_with_❤️_at-VIT_Bhopal-8B0000?style=for-the-badge)](https://vitbhopal.ac.in)
[![PSBs Hackathon 2026](https://img.shields.io/badge/PSBs_Hackathon-2026-1a1a2e?style=for-the-badge)](https://github.com/akshat440/ShaktiSafe)

</div>
