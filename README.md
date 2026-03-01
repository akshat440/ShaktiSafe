<div align="center">

# SHAKTISAFE

**Cross-Channel Mule Account Detection using Graph Neural Networks**

A production-grade, real-time fraud intelligence platform that constructs a unified entity graph across all payment channels and applies GraphSAGE neural networks to identify and block mule rings before funds are disbursed.

---

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch_Geometric-GraphSAGE-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch-geometric.readthedocs.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-ML_Engine-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.2-6DB33F?style=flat-square&logo=springboot&logoColor=white)](https://spring.io)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Kafka](https://img.shields.io/badge/Apache_Kafka-3.6-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org)
[![Docker](https://img.shields.io/badge/Docker_Compose-Full_Stack-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

---

<table>
<tr>
<td align="center"><strong>42,152</strong><br/><sub>Transactions Modelled</sub></td>
<td align="center"><strong>12</strong><br/><sub>Fraud Scenarios</sub></td>
<td align="center"><strong>9</strong><br/><sub>Payment Channels</sub></td>
<td align="center"><strong>0.98+</strong><br/><sub>ROC-AUC (Synthetic)</sub></td>
<td align="center"><strong>INR 6.79 Cr</strong><br/><sub>Amount Flagged</sub></td>
<td align="center"><strong>&lt;100ms</strong><br/><sub>Detection Latency</sub></td>
</tr>
</table>

*PSBs Hackathon 2026 &nbsp;·&nbsp; Problem Statement 2 &nbsp;·&nbsp; Idea Submission*<br/>
*VIT Bhopal &nbsp;·&nbsp; School of Computing &nbsp;·&nbsp; Team WebsiteCrash*

</div>

---

## Team WebsiteCrash

> **VIT Bhopal University &nbsp;·&nbsp; School of Computing &nbsp;·&nbsp; PSBs Hackathon 2026**

<table width="100%">
<thead>
<tr>
<th align="left">Role</th>
<th align="left">Name</th>
<th align="left">Institution</th>
<th align="left">GitHub</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Team Leader</strong></td>
<td>Vidhi Luniya</td>
<td>VIT Bhopal &nbsp;·&nbsp; School of Computing</td>
<td>—</td>
</tr>
<tr>
<td><strong>Member</strong></td>
<td>Akshat Singh Tomar</td>
<td>VIT Bhopal &nbsp;·&nbsp; School of Computing</td>
<td><a href="https://github.com/akshat440"><img src="https://img.shields.io/badge/akshat440-181717?style=flat-square&logo=github"/></a></td>
</tr>
<tr>
<td><strong>Member</strong></td>
<td>Anushka Pareek</td>
<td>VIT Bhopal &nbsp;·&nbsp; School of Computing</td>
<td>—</td>
</tr>
</tbody>
</table>

| | |
|---|---|
| **Competition** | PSBs Hackathon 2026 |
| **Problem Statement** | Statement 2 — Cross-Channel Mule Account Detection |
| **Round** | Idea Submission |
| **Repository** | [github.com/akshat440/ShaktiSafe](https://github.com/akshat440/ShaktiSafe) |

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Proposed Solution](#2-proposed-solution)
3. [System Architecture](#3-system-architecture)
4. [GNN Model — GraphSAGE](#4-gnn-model--graphsage)
5. [Detection Engine](#5-detection-engine)
6. [12 Fraud Scenarios](#6-12-embedded-fraud-scenarios)
7. [Regulatory Compliance](#7-regulatory--compliance-coverage)
8. [Privacy Architecture](#8-privacy-safe-inter-bank-sharing)
9. [Technology Stack](#9-technology-stack)
10. [Quick Start](#10-quick-start)
11. [API Reference](#11-api-reference)
12. [Project Structure](#12-project-structure)
13. [Dataset Facts](#13-dataset-facts)

---

## 1. Problem Statement

India lost **INR 11,333 Crore** to bank fraud in FY 2023–24 (RBI). Approximately 87% of financial fraud involves mule networks — legitimate account holders recruited to receive and rapidly forward illicit funds across multiple banks and payment channels, deliberately to evade detection.

### The Cross-Channel Blind Spot

Current AML systems operate in hard silos. The mobile banking fraud team cannot see ATM patterns. The NEFT compliance officer does not see UPI velocity. Fraudsters construct transactions that individually pass every rule-based check, while the aggregate cross-channel pattern is unmistakable.

```
  MOBILE APP         LINKED WALLET         ATM WITHDRAW          DISPERSE
  [ Receive ]  -->   [    Move    ]  -->   [ Cash Out  ]  -->   [  Gone  ]

  Passes all         Passes all            Passes all            Too late
  rule checks        rule checks           rule checks
```

> *"Money mules operate across channels — receiving via Mobile App, moving to a Linked Wallet, and withdrawing at ATM in minutes. Siloed fraud rules miss this high-velocity pattern."*
> — PSBs Hackathon 2026, Problem Statement 2

### Scale of the Threat

| Metric | Value | Source |
|--------|-------|--------|
| Bank fraud losses FY 2023–24 | INR 11,333 Crore | RBI Annual Report |
| Financial fraud involving mule networks | ~87% | Industry estimate |
| Average mule ring clear and disperse time | < 6 minutes | Documented cases |
| RBI structuring threshold (primary target) | INR 50,000 | RBI Circular |

### What the Solution Must Cover

| Requirement | Priority |
|---|:---:|
| Unified entity graph across all 9 channels | Critical |
| Real-time ring detection before disbursement | Critical |
| Structuring and fragmentation detection | High |
| Cross-jurisdiction risk scoring (FATF) | High |
| Behaviour-based sanctions beyond KYC lists | High |
| Privacy-safe inter-bank sharing | High |
| Regulator-ready STR reports with confidence scores | Critical |

---

## 2. Proposed Solution

ShaktiSafe ingests all transaction streams into a single Neo4j entity graph and runs GraphSAGE inference across the entire connected network simultaneously — not channel by channel. Cross-channel correlation is achieved by design, not by post-hoc aggregation.

### Four Pillars

| # | Pillar | Description |
|:---:|---|---|
| 01 | **Unified Entity Graph** | Every account, device, IP address, bank, and jurisdiction is a node. Every transaction is a directed edge. The Mobile App team and SWIFT compliance officer analyse the same graph in real time. |
| 02 | **GraphSAGE Neural Network** | 3-layer inductive GNN trained on 42,152 synthetic transactions embedding 12 real fraud patterns. Scores new accounts without retraining by aggregating transaction neighbourhood features. Outputs mule probability per account. |
| 03 | **Parallel Detection Engine** | Six deterministic detectors run alongside the GNN: Mule Ring (Louvain community), Structuring/Smurfing, Cross-Jurisdiction (FATF risk map), Device Fingerprint, Nesting Depth, and Behavioural Sanctions Screener. |
| 04 | **Compliance and Sharing Layer** | Auto-generated FIU-IND STR reports per detected pattern. Privacy-safe inter-bank sharing via SHA-256 hashed IDs. All outputs are PMLA, RBI, and FATF aligned with GNN confidence scores and full evidence chains. |

### Requirements Coverage Matrix

| Requirement | ShaktiSafe Implementation |
|---|---|
| Unified entity graph | Neo4j: all 9 channels — one graph |
| Real-time ring detection | Louvain community + GNN inference |
| Block rings before dispersal | API freeze before disbursement window |
| Structuring / fragmentation | Threshold-band transaction detector |
| Jurisdiction risk scoring | 20-country FATF risk matrix |
| Behaviour-based sanctions | Device + routing fingerprint match |
| Privacy-safe sharing | SHA-256 hashed IDs + amount bucketing |
| Regulator-ready reports | Auto STR with evidence chain + confidence score |

---

## 3. System Architecture

### End-to-End Detection Pipeline

```
+------------------------------------------------------------------------------+
|                      DATA INGESTION  (9 Payment Rails)                       |
|                                                                              |
|   Mobile App    Web Banking    ATM Network    UPI / BHIM    NEFT / IMPS     |
|   RTGS          SWIFT          NACH                                          |
+--------------------------------------+---------------------------------------+
                                       |
                                       v
+------------------------------------------------------------------------------+
|                  EVENT STREAMING  --  Apache Kafka 3.6                       |
|                                                                              |
|   Account-partitioned topics       Ordered per-account delivery              |
|   Replay-capable forensic log      Fault-tolerant, zero data loss            |
|                                                                              |
|   Topics:  transactions.raw  /  fraud.alerts  /  str.reports  /  dlq        |
+------------------+---------------------------+------------------------------+
                   |                           |
        +----------v----------+     +----------v----------+
        |    GRAPH ENGINE     |     |   SPRING BOOT       |
        |    Neo4j 5.x        |     |   API GATEWAY       |
        |                     |     |                     |
        |  42,152 txn edges   |     |  REST ingestion     |
        |  3,073 acct nodes   |     |  Kafka producer     |
        |  Cypher ring query  |     |  ML Engine proxy    |
        +---------------------+     +----------+----------+
                   |                           |
                   +--------------+------------+
                                  |
                                  v
+------------------------------------------------------------------------------+
|                    ML ENGINE  --  FastAPI + GraphSAGE                        |
|                                                                              |
|   Input Layer        32 node features per account                           |
|   SAGEConv Layer 1   64 hidden dims  .  BatchNorm  .  ReLU                  |
|   SAGEConv Layer 2   128 dims  .  BN  .  ReLU  .  Residual                 |
|   SAGEConv Layer 3   64 dims  .  BN  .  ReLU  .  Residual                  |
|   Dropout (0.3)  ->  Classifier Head  ->  Mule probability [0.0, 1.0]      |
|                                                                              |
|   Target inference latency:  < 100ms                                        |
+--------+---------+----------+-----------+-----------+----------------------+
         |         |          |           |           |
         v         v          v           v           v
    +--------+ +--------+ +-------+ +--------+ +--------+
    | BLOCK  | | REVIEW | | FILE  | | INTER  | | GRAPH  |
    | ACCOUNT| |  FLAG  | |  STR  | |  BANK  | | ALERT  |
    +--------+ +--------+ +-------+ +--------+ +--------+
         |         |          |           |           |
         +----+----+----------+-----------+      +----+
              |                                  |
              v                                  v
+------------------------------------------------------------------------------+
|                   NEXT.JS 14  REAL-TIME DASHBOARD                            |
|                                                                              |
|   Live WebSocket alert ticker    D3 force-directed mule ring graph           |
|   Account risk score table       STR report viewer                           |
|   Cross-channel stats overview   Transaction explorer                        |
+------------------------------------------------------------------------------+
```

### Neo4j Property Graph Schema

```cypher
// Node types
(:Account     {id, kyc_status, account_age, risk_score, channel_count})
(:Device      {device_id, fingerprint_hash, platform})
(:Bank        {bank_id, name, country})
(:Jurisdiction {code, fatf_risk_score, status})

// Relationships
(Account) -[:TRANSACTS {amount, channel, timestamp, txn_id}]-> (Account)
(Account) -[:SHARES_DEVICE]->                                   (Device)
(Device)  -[:LOCATED_IN]->                                      (Jurisdiction)
(Account) -[:MANAGED_BY]-> (Bank) -[:OPERATES_IN]->            (Jurisdiction)
```

### Architecture Design Rationale

| Component | Rationale |
|---|---|
| **Neo4j** | Property graphs natively model the account-device-jurisdiction topology. Cypher ring queries are far more expressive than equivalent relational SQL multi-joins, and APOC procedures enable in-database Louvain community detection. |
| **GraphSAGE** | Unlike transductive GCN, GraphSAGE is inductive — it generalises to unseen accounts at runtime. New mule accounts registered today are scored without waiting for a full model retraining cycle. |
| **Apache Kafka** | Decouples ingestion from scoring, enables independent service scaling, and allows forensic replay of any historical transaction window without touching production databases. |
| **Spring Boot** | Handles high-throughput REST ingestion and Kafka fan-out cleanly in Java 21 virtual threads, with a non-blocking WebClient proxy to the Python ML Engine. |

---

## 4. GNN Model — GraphSAGE

### Node Feature Engineering — 32 Features Per Account

**Account-Level Features (F-0 to F-9)**

| Feature | Name | Signal Description |
|---------|------|--------------------|
| F-0 | Account Age | Normalised — low age = higher risk |
| F-1 | KYC Status | Binary: failed verification flag |
| F-2 | Txn Velocity | log(count) normalised [0,1] |
| F-3 | Avg Amount | log(average) normalised |
| F-4 | Channel Diversity | Unique channels / 9 total |
| F-5 | Receive Ratio | Inbound / total — transit signal |
| F-6 | New Account Flag | Age < 30 days — strong mule indicator |
| F-7 | Round Amounts | Structuring + sanctions signal |
| F-8 | Velocity Proxy | Txn count vs peer median |
| F-9 | KYC Risk | Inverted KYC quality score |

**Transaction Pattern Features (F-10 to F-19)**

| Feature | Name | Signal Description |
|---------|------|--------------------|
| F-10 | Cross-Jurisdiction | Fraction of cross-border transactions |
| F-11 | High-Risk Juris. | FATF grey-list destination ratio |
| F-12 | Structuring Signal | Transactions in INR 45K–49.9K band |
| F-13 | ATM Ratio | Cash withdrawal frequency |
| F-14 | SWIFT Ratio | International wire frequency |
| F-15 | App-to-ATM | Mobile App then ATM sequence flag |
| F-16 | Shared Device | Device fingerprint ring signal |
| F-17 | Amt Variability | Std dev / mean ratio |
| F-18 | Send/Recv Ratio | Transit account indicator |
| F-19 | Tor IP Flag | Known anonymising IP prefix |

**GraphSAGE Neighbourhood Features (F-20 to F-31)**

| Feature | Name | Signal Description |
|---------|------|--------------------|
| F-20/21 | Neighbour Age/KYC | Mean age and KYC of connected nodes |
| F-22/23 | Degree / Out-Degree | Normalised node degree metrics |
| F-24 | Neighbour Activity | Mean transaction count of neighbours |
| F-25/26 | Edge Amounts | Mean in / out edge amounts |
| F-27/28 | Fan-Out / Fan-In | Hub and sink detection metrics |
| F-29 | Chain Node | Single in + single out = layering signal |
| F-30/31 | In / Out Degree | Final structural degree features |

### Network Architecture

```
Input Layer           32 features per node
        |
        v
SAGEConv Layer 1      64 hidden dims  .  BatchNorm  .  ReLU
        |
        v
SAGEConv Layer 2      128 dims  .  BatchNorm  .  ReLU  .  Residual connection
        |
        v
SAGEConv Layer 3      64 dims  .  BatchNorm  .  ReLU  .  Residual connection
        |
        v
Dropout (0.3)         Regularisation
        |
        v
Classifier Head       Mule probability output  [0.0, 1.0]
```

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | 48,396 transactions · 1,875 accounts · 75 mule accounts (4%) |
| Class imbalance handling | Focal Loss (alpha=0.75, gamma=2.0) |
| Optimiser | Adam lr=0.005 · Cosine annealing · Gradient clip 1.0 |
| Data split | 70% train · 15% validation · 15% test · stratified |
| Early stopping | Patience = 30 epochs on validation AUC |
| Feature extraction | GraphSAGE 1-hop neighbourhood aggregation |
| Total model parameters | 156,326 |

### Model Performance — Synthetic Dataset

| Metric | Score | Notes |
|--------|-------|-------|
| ROC-AUC | **0.98+** | High separation on embedded patterns |
| F1 Score | **~0.95** | Focal loss handling on imbalanced classes |
| False Positive Rate | **~2–5%** | Tunable via detection threshold |
| Convergence | **Stable** | No divergence with focal loss |
| Full-graph inference | **Est. < 80ms** | Target < 100ms production |

> **Disclaimer:** Metrics are on controlled synthetic data where patterns are embedded by design. Real-world performance on live bank data will differ and requires field validation before production deployment.

---

## 5. Detection Engine

Six deterministic detectors run in parallel alongside GNN inference. Each is independently tunable and emits its own alert type with a confidence score.

### Detector Summary

| Detector | Algorithm | Alert Type | Default Action |
|---|---|---|---|
| Mule Ring | Louvain community detection | Ring topology + velocity | BLOCK + FILE STR |
| Structuring | Threshold band analysis | INR 45K–49.9K clustering | FILE CTR |
| Jurisdiction Risk | FATF 20-country matrix | Cross-border hop scoring | FLAG / BLOCK |
| Device Fingerprint | SHA-256 hash matching | Shared device across accounts | REVIEW |
| Nesting Depth | Multi-hop shell chain | Layering depth > 3 hops | FLAG |
| Behavioural Sanctions | Pattern vs behavioural profile | Device + routing match | ESCALATE |

### Mule Ring Detection — Louvain Community Algorithm

```
Step 1   Load 90-day transaction window
Step 2   Build weighted directed graph from transactions
Step 3   Run Louvain community detection algorithm
Step 4   For each detected community, compute ring score:
           - Internal velocity  (how fast money moves within cluster)
           - Channel diversity  (App -> Wallet -> ATM pattern)
           - Temporal compression  (all within short window)
           - External entry and exit points

         Community Score >= 0.65  -->  BLOCK + FILE STR
         Community Score <  0.65  -->  MONITOR
```

### Structuring Detection — Threshold Band Analysis

```
Step 1   Scan all transactions in rolling 24-hour window
Step 2   Filter: amount in INR 45,000 to 49,999 band
Step 3   Group by receiver account and time window
Step 4   Same destination >= 3 transactions?
         AND multiple coordinated senders?
         -->  STRUCTURING ALERT — FILE CTR
```

### Jurisdiction Risk Scoring — FATF Matrix

```
Score  =  sum(hop_risks)  +  corridor_penalty
Score > 60  -->  HIGH RISK FLAG
Score > 80  -->  BLOCK
```

| Jurisdiction | Risk Score | Status |
|---|:---:|---|
| India (IN) | 8–10 | Domestic — baseline |
| Singapore (SG) | 42 | FATF Member |
| UAE (AE) | 65 | FATF Grey List |
| Panama (PA) | 78 | Grey List |
| Macau (MO) | 72 | Monitored |

### Behavioural Sanctions Screening

> Traditional sanctions screening matches names against static lists. ShaktiSafe adds a behavioural layer that detects KYC-passing sanctioned entities through device and routing continuity.

| Signal | Example | Weight |
|---|---|:---:|
| KYC Status | PASS — not on any sanctions list | Baseline |
| Device ID | MATCH — SHA-256 hash matches previously flagged entity | Critical |
| Transfer Pattern | Round amounts: INR 100K, 500K, 1M | High |
| Withdrawal Speed | < 5 minutes after receipt | High |
| Jurisdiction | UAE — FATF grey list destination | Medium |
| Counterparty | No prior established relationship | Medium |

`Behaviour Score >= 70` threshold → **ESCALATE TO COMPLIANCE — SANCTIONS MATCH**

---

## 6. 12 Embedded Fraud Scenarios

Each scenario is embedded as a precise mathematical pattern within the 42,152-transaction synthetic dataset.

| ID | Severity | Scenario | Description | Detection Signal |
|----|:---:|---|---|---|
| S01 | CRITICAL | **Classic Mule Ring** | 6 accounts: App→UPI×3→ATM×2, INR 3.8L in 6 min, all <25 days old | Ring topology + velocity |
| S02 | HIGH | **Coordinated Smurfing** | 18 txns × INR 48,500–49,900 to Singapore, coordinated below INR 50K threshold | Threshold-band clustering |
| S03 | CRITICAL | **Cross-Border SWIFT** | India→Singapore→UAE→Switzerland→India, 4-hop chain, AE on FATF grey list | Jurisdiction risk path scoring |
| S04 | HIGH | **Shell Nesting (6-Hop)** | INR 50L through 6 shells, 6 banks, 6 cities — each hop takes 10–15% cut | Multi-hop depth + cut ratio |
| S05 | CRITICAL | **Sanctions Evasion** | Passed KYC, not on any list — device fingerprint matches flagged entity | Behavioural fingerprint match |
| S06 | HIGH | **Carousel Fraud** | 8 accounts, funds circle back to origin — creates fictitious trade history | Circular flow detection |
| S07 | CRITICAL | **Mass ATM Cashout** | 1 source → 12 ATM mules simultaneously, INR 9,500–9,999 within 1 hour | Fan-out velocity burst |
| S08 | HIGH | **Trade-Based Laundering** | 5 over-invoiced phantom SWIFT exports to mask value transfer across borders | Invoice anomaly + SWIFT flag |
| S09 | HIGH | **Loan Stacking** | 6 loans, same device, 4 banks, within 2 hours — classic bust-out fraud | Shared device + timing |
| S10 | HIGH | **Crypto Off-Ramp** | 5 P2P crypto exchanges → aggregation account → SWIFT exit to Hong Kong | Aggregation + SWIFT exit |
| S11 | HIGH | **Salary Diversion** | 40 salaries via NACH redirected to 8 mule accounts opened <15 days prior | NACH anomaly + new account |
| S12 | HIGH | **Dark Web Carding** | 30 txns, single IP, 6 wallets, avg INR 3,200 — stolen card cashout | Single-IP burst + wallet pattern |

---

## 7. Regulatory & Compliance Coverage

Every component of ShaktiSafe is designed around the Indian regulatory AML framework — not retrofitted to it.

| Regulation | Requirement | ShaktiSafe Implementation | Status |
|---|---|---|:---:|
| PMLA 2002, Sec 12 | Records + STR within 7 days | Auto-generated STR per detected pattern with evidence chain | COVERED |
| RBI KYC Master Dir. 2023 | KYC verification, enhanced due diligence | KYC status = node feature F-1 in GNN model | COVERED |
| FIU-IND STR Requirements | STR with evidence and rationale | PDF: evidence chain + confidence score + recommended actions | COVERED |
| FATF Recommendation 16 | Wire transfer transparency | 20-jurisdiction FATF risk matrix + SWIFT hop tracking | COVERED |
| FATF Rec. 1 — Risk-Based | Risk-based approach to AML/CFT | GNN probability score = quantified risk-based output | COVERED |
| IBA AML Guidelines 2024 | Inter-bank intelligence sharing | SHA-256 hashed IDs + amount bucketing sharing API | COVERED |
| RBI Cybersecurity Framework | Device-level fraud signals | Device fingerprint as dedicated entity node in graph | COVERED |
| GDPR / RBI Data Localisation | Account ID privacy in shared reports | Account IDs hashed before any external export — no PII | COVERED |
| FEMA (cross-border flows) | Monitor outward remittances | SWIFT node tracking + jurisdiction hop scoring | COVERED |
| RBI AML Guidelines | Transaction monitoring, velocity checks | Velocity = node feature F-2; rolling 24hr and 90-day windows | COVERED |

### Sample Auto-Generated FIU-IND STR Output

```
Report Type       SUSPICIOUS TRANSACTION REPORT
Classification    CONFIDENTIAL — INTERNAL COMPLIANCE
Typology          CLASSIC MULE RING
Risk Level        CRITICAL
GNN Confidence    97.2%  (GraphSAGE Ensemble)
Accounts Flagged  8 accounts — all < 25 days old
Amount at Risk    INR 3,80,000
Txn Count         14 transactions — 6 minutes
Channels          MOBILE APP  ->  UPI x3  ->  ATM x2
Detection Engine  ShaktiSafe v1.0 — Louvain + GraphSAGE

Regulatory Basis  PMLA 2002 Section 12
                  RBI KYC Master Direction 2023
                  FIU-IND STR Format IV
                  FATF Recommendation 16

STR Filing        REQUIRED  .  Deadline: 7 working days  .  Format: FIU-IND IV
```

---

## 8. Privacy-Safe Inter-Bank Sharing

No single bank sees the full mule ring picture. ShaktiSafe broadcasts anonymised behavioural fingerprints so banks can correlate patterns across institutions without exchanging raw customer data.

```
  BANK A           SHA-256          SHARED            BANK B           ALERT
  Detects ring -->  + DP NOISE  -->  FINGERPRINT  -->  Pattern match -->  CONFIRMED
  flagged accts     Anonymise        Broadcast to       against own        Cross-bank
                    hash + noise     correspondent      data               ring blocked
                                     banks
```

### What Is Shared vs What Is Protected

| Shared — Anonymised Behavioural Fingerprint | Protected — Never Transmitted |
|---|---|
| SHA-256(account_id)[:16] — not reversible | Raw account IDs or customer names |
| Transaction count bucket (nearest 10) | Actual transaction amounts (DP-noised) |
| Average amount bucket (nearest INR 10,000) | Device IDs or IP addresses (hashed only) |
| Channel types used (MOBILE_APP, ATM, SWIFT) | KYC documents or personal identifiers |
| Jurisdiction list — country codes only | Branch, city, or geographic specifics |
| Round-amount ratio — structuring signal | Transaction timestamps (bucketed only) |

### Python Implementation

```python
anonymized_id      = SHA256(account_id)[:16]            # First 16 hex chars — not reversible
txn_count_bucket   = len(txns) // 10 * 10               # Round to nearest 10
avg_amount_bucket  = round(mean_amount, -4)              # Round to nearest INR 10,000
channels_list      = sorted(set(t.channel for t in txns))# Channel types only — no amounts
fingerprint_hash   = SHA256(JSON(behaviour_vector))      # Deterministic match key — no PII
```

---

## 9. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|:---:|---|
| GNN | PyTorch Geometric — GraphSAGE | Latest | Inductive mule probability scoring |
| Graph Database | Neo4j Community | 5.15 | Unified entity graph, Cypher ring queries |
| ML API | FastAPI + Uvicorn | 0.109 | Inference server, WebSocket streaming |
| Event Streaming | Apache Kafka | 3.6 | Transaction event bus, forensic replay |
| API Gateway | Spring Boot + Java 21 | 3.2.2 | REST ingestion, Kafka producer, ML proxy |
| Frontend | Next.js + TypeScript + Tailwind | 14 | Real-time fraud intelligence dashboard |
| Deployment | Docker Compose | v3.9 | One-command full-stack orchestration |
| STR Reports | ReportLab / WeasyPrint | Latest | Auto FIU-IND STR PDF generation |
| Privacy Layer | SHA-256 + Differential Privacy | — | GDPR-safe inter-bank fingerprinting |
| Coordination | Apache ZooKeeper | 3.9 | Kafka broker coordination |

---

## 10. Quick Start

### Prerequisites

- Docker 24+ and Docker Compose v2
- 8 GB RAM minimum recommended
- Ports 3000, 8000, 8080, 8090, 7474, 7687, 9092, 9093 available

### Deploy

```bash
git clone https://github.com/akshat440/ShaktiSafe.git
cd ShaktiSafe
docker-compose up --build
```

Allow 60–90 seconds for all services to initialise. The ML Engine seeds synthetic data and trains the GNN model automatically on first startup.

### Service Endpoints

| Service | URL | Credentials |
|---|---|---|
| Next.js Dashboard | http://localhost:3000 | — |
| Spring Boot Gateway API | http://localhost:8080/api/v1 | — |
| ML Engine (FastAPI) | http://localhost:8000 | — |
| ML Engine Swagger UI | http://localhost:8000/docs | — |
| Neo4j Browser | http://localhost:7474 | neo4j / intellitrace2026 |
| Kafka UI (Provectus) | http://localhost:8090 | — |

### Make Commands

```bash
# Stack management
make demo            # Launch full Docker stack with build
make stop            # Stop all containers
make clean           # Tear down and remove all named volumes

# Development
make data            # Regenerate 42,152 synthetic transactions
make train           # Retrain GNN model only
make report          # Generate sample FIU-IND STR report

# Observability
make test            # Smoke test all service endpoints
make logs            # Tail all container logs
make logs-ml         # ML Engine logs only
make logs-gateway    # Spring Boot gateway logs only
make logs-kafka      # Kafka broker logs only
```

---

## 11. API Reference

### Spring Boot Gateway — `localhost:8080/api/v1`

| Method | Endpoint | Description | Response |
|:---:|---|---|---|
| `POST` | `/transactions` | Ingest a single transaction | 202 Accepted + stamped transaction |
| `POST` | `/transactions/batch` | Ingest batch (max 500) | 202 Accepted + ingested count |
| `POST` | `/transactions/analyze` | Ingest + synchronous ML risk score | 200 + score object |
| `GET` | `/stats` | Dashboard statistics | Stats JSON |
| `GET` | `/graph` | Transaction graph for D3 visualisation | Graph nodes + edges |
| `GET` | `/alerts` | Recent fraud alerts with scores | Alert array |
| `GET` | `/accounts` | Account risk score table | Account array |
| `GET` | `/health` | Service health check | UP / DOWN |

**Ingest a transaction:**

```bash
curl -X POST http://localhost:8080/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id":        "ACC001",
    "receiver_id":      "ACC002",
    "amount":           49999,
    "channel":          "UPI",
    "sender_country":   "IN",
    "receiver_country": "SG"
  }'
```

**Synchronous risk score:**

```bash
curl -X POST http://localhost:8080/api/v1/transactions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id":   "ACC001",
    "receiver_id": "ACC002",
    "amount":      49500,
    "channel":     "UPI"
  }'
```

### Transaction Schema

| Field | Type | Required | Notes |
|---|---|:---:|---|
| transaction_id | string | No | Auto-generated UUID if omitted |
| sender_id | string | Yes | |
| receiver_id | string | Yes | |
| amount | number | Yes | INR, must be positive |
| channel | string | Yes | UPI, NEFT, RTGS, IMPS, WALLET, ATM, SWIFT, NACH |
| currency | string | No | Default: INR |
| sender_country | string | No | ISO-3166 alpha-2, default: IN |
| receiver_country | string | No | ISO-3166 alpha-2, default: IN |
| timestamp_ms | number | No | Unix epoch milliseconds, defaults to now |
| device_id | string | No | Device fingerprint hash |
| mcc | string | No | Merchant category code |

### ML Engine Direct — `localhost:8000`

| Method | Endpoint | Description |
|:---:|---|---|
| `GET` | `/` | Service info and model status |
| `GET` | `/stats` | Fraud detection statistics |
| `GET` | `/graph` | Full entity graph data |
| `GET` | `/alerts` | All fraud alerts with confidence scores |
| `GET` | `/accounts` | Scored account list |
| `POST` | `/analyze` | Direct GNN inference |
| `WS` | `/ws/live` | Real-time alert WebSocket stream |

### Kafka Topics

| Topic | Partitions | Retention | Purpose |
|---|:---:|---|---|
| `transactions.raw` | 6 | 7 days | All inbound transactions |
| `fraud.alerts` | 3 | 30 days | Detected fraud events |
| `str.reports` | 1 | 90 days | STR filing triggers |
| `transactions.dlq` | 2 | 7 days | Dead-letter queue |

---

## 12. Project Structure

```
ShaktiSafe/
|
|-- docker-compose.yml                  8-service full-stack deployment
|-- Makefile                            Developer shortcuts
|-- README.md
|
|-- ml-engine/                          Python FastAPI + GNN Inference
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- gnn/
|   |   |-- model.py                    GraphSAGE 3-layer architecture  (156,326 params)
|   |   |-- train.py                    Focal loss + cosine annealing pipeline
|   |   |-- inference.py                Runtime scoring module
|   |   `-- __init__.py
|   |-- detection/
|   |   |-- mule_ring_detector.py       Louvain community detection
|   |   |-- structuring_detector.py     Threshold band analysis
|   |   |-- jurisdiction_scorer.py      20-country FATF risk matrix
|   |   |-- device_fingerprint.py       SHA-256 hash matching
|   |   |-- nesting_depth.py            Multi-hop shell chain scorer
|   |   |-- sanctions_screener.py       Behavioural pattern matching
|   |   `-- __init__.py
|   |-- data/
|   |   |-- generator.py                42,152 synthetic transactions, 12 scenarios
|   |   `-- __init__.py
|   |-- reports/
|   |   `-- report_generator.py         Auto FIU-IND STR PDF
|   |-- api/
|   |   |-- main.py                     FastAPI app, all endpoints, WebSocket
|   |   `-- __init__.py
|   `-- sample_data/
|       |-- transactions.json
|       |-- accounts.json
|       `-- stats.json
|
|-- backend/                            Spring Boot 3.2 API Gateway  (Java 21)
|   |-- Dockerfile                      2-stage build: JDK builder -> JRE slim
|   |-- pom.xml
|   `-- src/main/
|       |-- java/com/shaktisafe/gateway/
|       |   |-- ShaktiSafeApplication.java
|       |   |-- controller/
|       |   |   `-- TransactionController.java    7 REST endpoints
|       |   |-- service/
|       |   |   `-- TransactionService.java       Kafka publish + ML proxy
|       |   |-- config/
|       |   |   |-- KafkaConfig.java              Topic auto-creation
|       |   |   `-- WebClientConfig.java          Non-blocking ML client
|       |   `-- model/
|       |       |-- Transaction.java              Canonical transaction payload
|       |       `-- FraudAlert.java               Alert model with STR flag
|       `-- resources/
|           `-- application.yml
|
|-- frontend/                           Next.js 14 + TypeScript + Tailwind
|   |-- Dockerfile
|   |-- package.json
|   |-- tailwind.config.js
|   |-- next.config.js
|   |-- tsconfig.json
|   `-- src/
|       |-- app/
|       |   |-- layout.tsx
|       |   |-- page.tsx
|       |   `-- dashboard/page.tsx      Main fraud intelligence dashboard
|       |-- components/
|       |   |-- ForceGraph.tsx          D3 force-directed mule ring graph
|       |   |-- LiveAlertTicker.tsx     WebSocket real-time alert feed
|       |   |-- AlertCard.tsx           Alert display with severity badge
|       |   |-- StatCard.tsx            Metric overview card
|       |   `-- Badge.tsx               Severity level indicator
|       |-- lib/
|       |   `-- api.ts                  API client (Gateway + ML Engine)
|       `-- types/
|           `-- index.ts                Shared TypeScript types
|
|-- graph-db/
|   |-- init/schema.cypher              Node labels, relationships, indexes
|   `-- queries/mule_ring_detection.cypher
|
`-- kafka/
    `-- init-topics.sh                  Creates all 4 topics on broker startup
```

---

## 13. Dataset Facts

| Metric | Value |
|--------|-------|
| Total transactions in dataset | 42,152 |
| Account nodes | 3,073 |
| Mule accounts | 73 &nbsp;(2.4%) |
| Embedded fraud scenarios | 12 |
| Payment channels covered | 9 |
| Jurisdictions in FATF matrix | 20 |
| GNN model parameters | 156,326 |
| Validation AUC (synthetic) | 0.98+ |
| Full-graph inference estimate | < 80ms |
| Parallel detectors | 6 |
| Total amount flagged (synthetic) | INR 6.79 Crore |
| Privacy method | SHA-256 + Differential Privacy bucketing |

### Implementation Phases

| Phase | Weeks | Deliverables |
|---|:---:|---|
| Phase I — Foundation | 1–2 | Synthetic dataset, Neo4j schema, GNN training pipeline, FastAPI server, Next.js dashboard, Docker Compose |
| Phase II — Detection Engine | 3–4 | 6 parallel detectors, Kafka streaming pipeline, Spring Boot gateway, cross-channel correlation, FATF matrix |
| Phase III — Compliance and Demo | 5–6 | FIU-IND STR report generation, inter-bank sharing API, force-directed graph, explainability layer, full documentation |

### Expected Outcomes

| Target | Value |
|---|---|
| Ring detection latency | < 100ms |
| Fraud patterns covered | 12 |
| Payment channels | 9 rails |
| STR auto-generation time | < 1 second |
| GNN validation AUC | 0.98+ (synthetic) |
| Privacy method | SHA-256 + Bucketing |

---

<div align="center">

**One Graph. Every Channel. Real Time.**

**Before Disbursement. Explained. Compliant.**

<br/>

[![VIT Bhopal](https://img.shields.io/badge/VIT_Bhopal-School_of_Computing-8B0000?style=flat-square)](https://vitbhopal.ac.in)
&nbsp;
[![PSBs Hackathon 2026](https://img.shields.io/badge/PSBs_Hackathon-2026-1a1a2e?style=flat-square)](https://github.com/akshat440/ShaktiSafe)
&nbsp;
[![Team WebsiteCrash](https://img.shields.io/badge/Team-WebsiteCrash-0d4a8a?style=flat-square)](https://github.com/akshat440/ShaktiSafe)

</div>
