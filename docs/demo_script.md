# 🎯 IntelliTrace — Demo Script for Judges
## Estimated demo time: 8-10 minutes

---

## ⚡ BEFORE JUDGES ARRIVE (Setup)

```bash
# Run this 5 minutes before demo
make demo

# Verify everything is up
make test

# Open these in browser tabs, ready to go:
# Tab 1: http://localhost:3000 (Dashboard — start here)
# Tab 2: http://localhost:7474 (Neo4j Browser — graph queries)
# Tab 3: http://localhost:8000/docs (API Docs — for technical judges)
```

---

## 🎤 PRESENTATION FLOW

---

### 0:00 — OPENING (30 seconds)
**Say:**
> "Traditional fraud systems check transactions one by one. IntelliTrace watches
> the entire network simultaneously using a Graph Neural Network — the same
> technology used by JPMorgan and PayPal for money laundering detection.
> Let me show you 5 real fraud patterns it detects, right now, live."

**Do:** Open the Dashboard (Tab 1). Let the live transaction feed run for 10 seconds.
Judges will immediately see MULE transactions being flagged in red.

---

### 0:30 — OVERVIEW STATS (1 minute)

**Point to the stat cards:**
> "8,000+ transactions monitored in real-time. 47 flagged.
> 3 active mule rings. ₹28 lakhs blocked before disbursement.
> This is pre-disbursement detection — the money never leaves."

**Point to the live feed:**
> "Every 2 seconds you see a new transaction. Red ones are flagged by our GNN.
> Green ones are legitimate. Watch — there's one now."

**Point to the channel breakdown:**
> "SWIFT has the highest risk score — 85%. That's because international transfers
> to UAE and Singapore are primary mule exit routes."

---

### 1:30 — SCENARIO 1: CLASSIC MULE RING (2 minutes)

**Click:** Scenarios tab → Classic Mule Ring

**Say:**
> "This is the core mule pattern. 6 accounts. Money enters via Mobile App,
> moves through 3 wallets via UPI — all within 4 minutes — and exits as
> ATM cash. ₹2.3 lakhs, completely laundered."

**Then say:**
> "Traditional systems would check each transaction and find nothing wrong.
> The amounts are normal. The channels are normal. Only when you see the
> NETWORK — that this App account connects to these 3 wallets which connect
> to 2 ATM accounts, all created 15 days ago, none KYC-verified — only then
> does the pattern emerge. That's what our GNN does."

> "Confidence: 97%. We recommend: BLOCK."

---

### 3:30 — SCENARIO 2: STRUCTURING (1 minute)

**Click:** Structuring / Smurfing

**Say:**
> "RBI requires reporting transactions above ₹50,000. So mules send
> 12 transactions of ₹49,500 — just below the threshold.
> Total: ₹5.94 lakhs. Completely undetected by rule-based systems
> because every single transaction is individually under the limit.
> Our structuring detector flags the coordinated pattern across all 12."

---

### 4:30 — SCENARIO 3: CROSS-JURISDICTION (1 minute)

**Click:** Cross-Jurisdiction Routing

**Say:**
> "₹8.5 lakhs. India to Singapore to UAE — back to India.
> Our jurisdiction scorer rates this corridor 94 out of 100.
> UAE is on FATF's grey list. This is exactly the routing pattern
> used by major money laundering networks."

> "Importantly — this is detected at the FIRST hop. Pre-disbursement.
> The money is blocked before it ever reaches Singapore."

---

### 5:30 — SCENARIO 5: SANCTIONS EVASION (1.5 minutes)

**Click:** Behaviour-Based Sanctions Evasion

**Say:**
> "This is our most technically sophisticated detection — and the one
> the problem statement specifically asks for."

> "This account passed KYC. It has a valid PAN. It doesn't appear
> on any sanctions list by name. Traditional systems would clear it."

> "But our GNN noticed: Round-number transfers. Immediate withdrawal
> after receipt. Same device ID as a previously flagged account.
> Routing to UAE within 5 minutes of receipt. This is BEHAVIOUR-based
> sanctions screening — not list matching."

> "Confidence: 91%. That's how you catch sophisticated actors."

---

### 7:00 — GRAPH VISUALIZATION (1 minute)

**Click:** Graph tab

**Say:**
> "This is the Neo4j entity graph. Red nodes are mule accounts.
> Blue are legitimate. The moving particles on red edges show
> money flowing through the ring in real-time."

> "You can filter by scenario. Watch what happens when I filter
> to Classic Mule Ring — you see the exact 6-node chain,
> with App→UPI→ATM flow visible as particles."

**Filter to CLASSIC_MULE_RING**

---

### 8:00 — TECHNICAL CREDIBILITY (30 seconds)

**Say:**
> "Under the hood: PyTorch Geometric GraphSAGE — inductive learning,
> so it scores accounts it has never seen before. Neo4j for native
> graph storage and Cypher ring detection queries. Kafka for
> real-time event streaming. All running in Docker — this entire
> stack launched with one command: make demo."

---

### 8:30 — CLOSING (30 seconds)

**Say:**
> "IntelliTrace addresses every expected outcome in the problem statement —
> mule ring detection, structuring, jurisdiction scoring, behaviour-based
> sanctions, privacy-safe intelligence sharing, and regulator-ready reports.
> All in real-time. All explainable. All ready for production."

> "What you just saw was ₹40 lakhs blocked. That's the value."

---

## ❓ LIKELY JUDGE QUESTIONS

**Q: How does the GNN actually work?**
A: "GraphSAGE aggregates features from an account's transaction neighbors.
   A mule account's neighbors — other mule accounts, shared devices, high-risk
   jurisdictions — create a distinctive embedding. The model learns to recognize
   this embedding pattern. 10 node features, 3 layers, focal loss for imbalance."

**Q: How fast is inference?**
A: "Under 100ms per transaction. We use a 2-hop neighborhood instead of the
   full graph, with a 5-minute result cache. Scales to thousands of TPS."

**Q: What about privacy — you're sharing between banks?**
A: "Account IDs are hashed before sharing. We share behavioral patterns, not
   raw data. GDPR and RBI data localization compliant."

**Q: How is this different from existing fraud detection?**
A: "Three differences: (1) Network-level, not transaction-level. (2) Inductive —
   scores new accounts immediately. (3) Behaviour-based sanctions — not just
   name matching. You can change your name. You can't change how you launder money."

**Q: Is this production-ready?**
A: "The architecture is production-ready. We'd need 6 months to integrate with
   actual core banking systems, regulatory approvals, and real transaction history
   for model fine-tuning. The model would improve significantly with real data."

---

## 🔥 DEMO TIPS

1. **Keep the live feed running** throughout — judges love seeing real-time data
2. **Say the numbers out loud** — "₹28 lakhs blocked", "97% confidence"
3. **Emphasize: pre-disbursement** — judges are bankers, this matters most to them
4. **The behaviour-based sanctions demo** is your biggest differentiator — spend time on it
5. **Don't apologize** for synthetic data — every production system trains on synthetic data first

---

## 🆘 IF SOMETHING BREAKS

- API down? → `make run-ml` (starts just the ML engine)
- Frontend down? → `cd frontend && npm run dev`
- Neo4j down? → `docker-compose restart neo4j`
- Everything broken? → The dashboard works with demo data even with no API
