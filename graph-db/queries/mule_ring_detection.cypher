// ============================================================
// IntelliTrace — Mule Detection Cypher Queries
// These power the Neo4j graph analytics engine
// ============================================================


// ── QUERY 1: Find all mule rings (connected mule accounts) ──
// Returns rings with all their member accounts + total amount

MATCH (a:Account {is_mule: true})-[r:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account {is_mule: true})
WITH collect(DISTINCT a) + collect(DISTINCT b) AS ring_members,
     sum(t.amount) AS total_amount,
     count(t) AS txn_count,
     collect(DISTINCT t.scenario)[0] AS scenario
WHERE size(ring_members) >= 3
RETURN
  scenario,
  size(ring_members) AS ring_size,
  total_amount,
  txn_count,
  [m IN ring_members | m.account_id] AS member_ids
ORDER BY total_amount DESC;


// ── QUERY 2: Velocity Detection ──────────────────────────────
// Find accounts with >5 transactions in any 10-minute window

MATCH (a:Account)-[:SENT]->(t:Transaction)
WITH a, collect(t) AS txns
UNWIND range(0, size(txns)-1) AS i
WITH a, txns[i] AS t1, txns
UNWIND range(i+1, size(txns)-1) AS j
WITH a, t1, txns[j] AS t2
WHERE duration.between(
  datetime(t1.timestamp),
  datetime(t2.timestamp)
).minutes <= 10
WITH a, count(*) AS rapid_pairs
WHERE rapid_pairs >= 5
RETURN
  a.account_id,
  a.risk_score,
  rapid_pairs,
  a.is_mule
ORDER BY rapid_pairs DESC
LIMIT 20;


// ── QUERY 3: Structuring Detection ──────────────────────────
// Transactions just below ₹50,000 to same destination

MATCH (src:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(dst:Account)
WHERE t.amount >= 48000 AND t.amount < 50000
WITH dst, collect(src) AS senders, collect(t) AS txns, sum(t.amount) AS total
WHERE size(txns) >= 3
RETURN
  dst.account_id AS destination,
  size(txns) AS transaction_count,
  total AS total_amount,
  [s IN senders | s.account_id] AS sender_accounts,
  [t IN txns | t.amount] AS amounts
ORDER BY transaction_count DESC;


// ── QUERY 4: Cross-Jurisdiction Cascade Trace ────────────────
// Trace money flowing through multiple jurisdictions

MATCH path = (start:Account)-[:SENT*1..5]->(t:Transaction)-[:RECEIVED_BY]->(end:Account)
WHERE start.jurisdiction <> end.jurisdiction
WITH path, start, end,
     [r IN relationships(path) | r.amount] AS amounts,
     [n IN nodes(path) WHERE n:Account | n.jurisdiction] AS jurisdictions
WHERE size(jurisdictions) >= 3
RETURN
  start.account_id AS origin,
  end.account_id AS destination,
  jurisdictions,
  amounts,
  length(path) AS hops
ORDER BY hops DESC
LIMIT 10;


// ── QUERY 5: Device Fingerprint Sharing ──────────────────────
// Multiple accounts using same device (mule controller pattern)

MATCH (a1:Account)-[:USES]->(d:Device)<-[:USES]-(a2:Account)
WHERE a1.account_id < a2.account_id
WITH d, collect(DISTINCT a1) + collect(DISTINCT a2) AS accounts
WHERE size(accounts) >= 2
RETURN
  d.device_id,
  size(accounts) AS account_count,
  [a IN accounts | {
    id: a.account_id,
    is_mule: a.is_mule,
    risk: a.risk_score
  }] AS accounts
ORDER BY account_count DESC;


// ── QUERY 6: Graph Community — Louvain-ready subgraph ────────
// Export account-to-account adjacency for community detection

MATCH (a:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account)
WHERE t.amount > 10000
RETURN
  a.account_id AS source,
  b.account_id AS target,
  count(t) AS weight,
  sum(t.amount) AS total_flow,
  collect(DISTINCT t.channel) AS channels
ORDER BY weight DESC;


// ── QUERY 7: Entry/Exit Point Detection ──────────────────────
// Accounts that only receive (entry) or only send (exit) — typical mule ends

MATCH (a:Account)
OPTIONAL MATCH (a)-[:SENT]->(t_out:Transaction)
OPTIONAL MATCH (t_in:Transaction)-[:RECEIVED_BY]->(a)
WITH a,
     count(DISTINCT t_out) AS out_count,
     count(DISTINCT t_in) AS in_count
WHERE (out_count = 0 AND in_count >= 3) OR (in_count = 0 AND out_count >= 5)
RETURN
  a.account_id,
  out_count,
  in_count,
  a.is_mule,
  CASE WHEN out_count = 0 THEN 'ENTRY_POINT' ELSE 'EXIT_POINT' END AS role
ORDER BY a.is_mule DESC;


// ── QUERY 8: Full Mule Ring Subgraph (for visualization) ──────
// Returns complete subgraph for a specific scenario

MATCH (a:Account {scenario: 'CLASSIC_MULE_RING'})-[r:SENT]->(t:Transaction)
-[:RECEIVED_BY]->(b:Account {scenario: 'CLASSIC_MULE_RING'})
RETURN a, r, t, b;


// ── QUERY 9: Cross-Bank Ring Detection ───────────────────────
// Mule rings that span multiple banks (harder to detect traditionally)

MATCH (a:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account)
WHERE a.is_mule = true AND b.is_mule = true AND a.bank <> b.bank
WITH collect(DISTINCT a.bank) AS banks, count(t) AS txn_count, sum(t.amount) AS total
WHERE size(banks) >= 2
RETURN banks, txn_count, total
ORDER BY total DESC;


// ── QUERY 10: Sanctions Behaviour Match ──────────────────────
// Accounts matching sanctioned entity behaviour patterns

MATCH (a:Account)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(b:Account)
WHERE
  t.amount % 100000 = 0                          -- Round numbers
  AND b.jurisdiction IN ['AE', 'SG', 'PA']       -- High-risk destinations
  AND duration.between(
    datetime(t.timestamp),
    datetime()
  ).minutes <= 10                                 -- Immediate withdrawal
RETURN
  a.account_id,
  t.amount,
  b.account_id,
  b.jurisdiction,
  a.scenario
ORDER BY t.amount DESC;
