// ============================================================
// IntelliTrace — Neo4j Graph Schema
// Run this file first to set up constraints and indexes
// ============================================================

// ── Constraints (uniqueness) ─────────────────────────────────

CREATE CONSTRAINT account_id IF NOT EXISTS
FOR (a:Account) REQUIRE a.account_id IS UNIQUE;

CREATE CONSTRAINT transaction_id IF NOT EXISTS
FOR (t:Transaction) REQUIRE t.txn_id IS UNIQUE;

CREATE CONSTRAINT device_id IF NOT EXISTS
FOR (d:Device) REQUIRE d.device_id IS UNIQUE;

CREATE CONSTRAINT ip_address IF NOT EXISTS
FOR (i:IP) REQUIRE i.address IS UNIQUE;

CREATE CONSTRAINT bank_id IF NOT EXISTS
FOR (b:Bank) REQUIRE b.bank_id IS UNIQUE;

CREATE CONSTRAINT jurisdiction_code IF NOT EXISTS
FOR (j:Jurisdiction) REQUIRE j.code IS UNIQUE;

// ── Indexes (query performance) ──────────────────────────────

CREATE INDEX account_risk IF NOT EXISTS
FOR (a:Account) ON (a.risk_score);

CREATE INDEX account_mule IF NOT EXISTS
FOR (a:Account) ON (a.is_mule);

CREATE INDEX txn_timestamp IF NOT EXISTS
FOR (t:Transaction) ON (t.timestamp);

CREATE INDEX txn_amount IF NOT EXISTS
FOR (t:Transaction) ON (t.amount);

CREATE INDEX txn_channel IF NOT EXISTS
FOR (t:Transaction) ON (t.channel);

CREATE INDEX txn_scenario IF NOT EXISTS
FOR (t:Transaction) ON (t.scenario);

// ── Node types and their properties ─────────────────────────
//
// (:Account)
//   account_id, bank, city, jurisdiction, account_age_days,
//   kyc_verified, account_type, is_mule, risk_score, scenario
//
// (:Transaction)
//   txn_id, amount, currency, channel, timestamp,
//   label, scenario, latency_ms
//
// (:Device)
//   device_id, first_seen, last_seen
//
// (:IP)
//   address, country, is_vpn, is_proxy, risk_score
//
// (:Bank)
//   bank_id, name, country, tier
//
// (:Jurisdiction)
//   code, name, risk_score, is_high_risk, fatf_status
//
// ── Relationship types ───────────────────────────────────────
//
// (:Account)-[:SENT {amount, channel, timestamp}]->(:Transaction)
// (:Transaction)-[:RECEIVED_BY {timestamp}]->(:Account)
// (:Account)-[:USES]->(:Device)
// (:Account)-[:ACCESSED_FROM]->(:IP)
// (:Account)-[:HELD_AT]->(:Bank)
// (:Account)-[:LOCATED_IN]->(:Jurisdiction)
// (:Account)-[:PART_OF_RING {ring_id, confidence}]->(:MuleRing)
// (:Transaction)-[:CROSSES_INTO]->(:Jurisdiction)

// ── Jurisdiction nodes (pre-seeded) ─────────────────────────

MERGE (j1:Jurisdiction {code: 'IN-MH'})
SET j1.name = 'India - Maharashtra', j1.risk_score = 10, j1.is_high_risk = false, j1.fatf_status = 'COMPLIANT';

MERGE (j2:Jurisdiction {code: 'IN-DL'})
SET j2.name = 'India - Delhi', j2.risk_score = 12, j2.is_high_risk = false, j2.fatf_status = 'COMPLIANT';

MERGE (j3:Jurisdiction {code: 'IN-KA'})
SET j3.name = 'India - Karnataka', j3.risk_score = 8, j3.is_high_risk = false, j3.fatf_status = 'COMPLIANT';

MERGE (j4:Jurisdiction {code: 'SG'})
SET j4.name = 'Singapore', j4.risk_score = 45, j4.is_high_risk = true, j4.fatf_status = 'MONITORED';

MERGE (j5:Jurisdiction {code: 'AE'})
SET j5.name = 'United Arab Emirates', j5.risk_score = 68, j5.is_high_risk = true, j5.fatf_status = 'GREY_LIST';

MERGE (j6:Jurisdiction {code: 'GB'})
SET j6.name = 'United Kingdom', j6.risk_score = 28, j6.is_high_risk = false, j6.fatf_status = 'COMPLIANT';

// ── Done ─────────────────────────────────────────────────────

RETURN 'Schema initialized successfully' AS status;
