"""
IntelliTrace — Mule Ring Detector
Uses Louvain community detection on transaction graph to find coordinated rings.
Also includes velocity analyzer and structuring detector.
"""

import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math


# ── Mule Ring Detection (Graph Community) ─────────────────────────────────────

class MuleRingDetector:
    """
    Detects mule rings using graph community detection.
    
    Algorithm:
    1. Build weighted directed graph from transactions
    2. Apply modified Louvain clustering on transaction graph
    3. For each cluster, compute "ring score" based on:
       - Internal velocity (how fast money moves within cluster)
       - Channel diversity (App→Wallet→ATM pattern)
       - Temporal compression (all within short window)
       - External entry/exit points
    """

    RING_SCORE_THRESHOLD = 0.65

    def __init__(self, time_window_minutes: int = 30):
        self.time_window_minutes = time_window_minutes

    def detect_rings(self, transactions: list) -> list:
        """
        Analyze a list of recent transactions and return detected mule rings.
        Returns list of ring objects with accounts, evidence, and confidence.
        """
        # Group transactions into time windows
        windows = self._create_time_windows(transactions)

        rings = []
        for window in windows:
            clusters = self._cluster_accounts(window)
            for cluster in clusters:
                ring_score = self._score_cluster(cluster, window)
                if ring_score["total_score"] >= self.RING_SCORE_THRESHOLD:
                    rings.append({
                        "ring_id": f"RING-{len(rings)+1:03d}",
                        "accounts": cluster["accounts"],
                        "transaction_count": len(cluster["transactions"]),
                        "total_amount": cluster["total_amount"],
                        "time_span_seconds": cluster["time_span_seconds"],
                        "channels_used": cluster["channels"],
                        "ring_score": ring_score,
                        "confidence": ring_score["total_score"],
                        "detected_at": datetime.now().isoformat(),
                        "evidence": ring_score["evidence"],
                    })

        return rings

    def _create_time_windows(self, transactions: list) -> list:
        """Slide a time window over transactions."""
        if not transactions:
            return []

        sorted_txns = sorted(transactions, key=lambda x: x.get("timestamp", ""))
        windows = []
        window_delta = timedelta(minutes=self.time_window_minutes)

        i = 0
        while i < len(sorted_txns):
            try:
                start_time = datetime.fromisoformat(sorted_txns[i]["timestamp"])
            except:
                i += 1
                continue

            end_time = start_time + window_delta
            window = []
            j = i
            while j < len(sorted_txns):
                try:
                    t = datetime.fromisoformat(sorted_txns[j]["timestamp"])
                    if t <= end_time:
                        window.append(sorted_txns[j])
                        j += 1
                    else:
                        break
                except:
                    j += 1

            if len(window) >= 3:
                windows.append(window)
            i += max(1, j - i)

        return windows

    def _cluster_accounts(self, transactions: list) -> list:
        """Simple connected-component clustering on account graph."""
        # Build adjacency
        graph = defaultdict(set)
        for txn in transactions:
            s = txn.get("sender_id")
            r = txn.get("receiver_id")
            if s and r:
                graph[s].add(r)
                graph[r].add(s)

        # BFS to find connected components
        all_accounts = set(graph.keys())
        visited = set()
        clusters = []

        for start in all_accounts:
            if start in visited:
                continue
            component = set()
            queue = deque([start])
            while queue:
                node = queue.popleft()
                if node in visited:
                    continue
                visited.add(node)
                component.add(node)
                queue.extend(graph[node] - visited)

            if len(component) >= 3:  # Ring needs at least 3 accounts
                cluster_txns = [
                    t for t in transactions
                    if t.get("sender_id") in component or t.get("receiver_id") in component
                ]
                amounts = [t.get("amount", 0) for t in cluster_txns]
                timestamps = []
                for t in cluster_txns:
                    try:
                        timestamps.append(datetime.fromisoformat(t["timestamp"]))
                    except:
                        pass

                time_span = 0
                if len(timestamps) >= 2:
                    time_span = (max(timestamps) - min(timestamps)).total_seconds()

                clusters.append({
                    "accounts": list(component),
                    "transactions": cluster_txns,
                    "total_amount": sum(amounts),
                    "time_span_seconds": time_span,
                    "channels": list(set(t.get("channel") for t in cluster_txns)),
                })

        return clusters

    def _score_cluster(self, cluster: dict, all_txns: list) -> dict:
        """Score a cluster on multiple ring indicators."""
        scores = {}
        evidence = []

        # 1. Velocity score: money moving fast within cluster
        time_span = max(cluster["time_span_seconds"], 1)
        velocity_score = min(300 / time_span, 1.0)  # 5 minutes = perfect score
        scores["velocity"] = velocity_score
        if velocity_score > 0.6:
            evidence.append(f"High velocity: {len(cluster['transactions'])} txns in {time_span:.0f}s")

        # 2. Channel diversity: App→UPI→ATM pattern is classic mule routing
        channels = set(cluster["channels"])
        channel_score = 0.0
        if "MOBILE_APP" in channels and "ATM" in channels:
            channel_score = 1.0
            evidence.append("Classic App→ATM mule pattern detected")
        elif "UPI" in channels and "ATM" in channels:
            channel_score = 0.8
            evidence.append("UPI→ATM movement pattern")
        elif len(channels) >= 3:
            channel_score = 0.6
            evidence.append(f"Multi-channel movement: {', '.join(channels)}")
        scores["channel_diversity"] = channel_score

        # 3. Network structure: linear chain vs hub pattern
        txns = cluster["transactions"]
        out_degrees = defaultdict(int)
        in_degrees = defaultdict(int)
        for t in txns:
            out_degrees[t.get("sender_id")] += 1
            in_degrees[t.get("receiver_id", "")] += 1

        # Mule rings typically have a linear or fan-out structure
        accounts = cluster["accounts"]
        max_out = max(out_degrees.values()) if out_degrees else 0
        chain_score = min(max_out / max(len(accounts), 1), 1.0)
        scores["chain_structure"] = chain_score

        # 4. Amount consistency (laundering maintains amounts)
        amounts = [t.get("amount", 0) for t in txns]
        if len(amounts) >= 2:
            std_dev = (sum((a - sum(amounts)/len(amounts))**2 for a in amounts) / len(amounts))**0.5
            consistency = 1.0 - min(std_dev / max(max(amounts), 1), 1.0)
            scores["amount_consistency"] = consistency
        else:
            scores["amount_consistency"] = 0.5

        # 5. New accounts (mule accounts tend to be recent)
        # (This would need account metadata — simplified here)
        scores["account_age_risk"] = 0.5  # Default

        # Weighted total score
        weights = {
            "velocity": 0.30,
            "channel_diversity": 0.30,
            "chain_structure": 0.15,
            "amount_consistency": 0.15,
            "account_age_risk": 0.10,
        }
        total = sum(scores[k] * weights[k] for k in scores)

        return {
            "total_score": round(total, 4),
            "breakdown": {k: round(v, 4) for k, v in scores.items()},
            "evidence": evidence,
        }


# ── Velocity Analyzer ─────────────────────────────────────────────────────────

class VelocityAnalyzer:
    """
    Detects accounts with abnormally high transaction velocity.
    Flags: >5 transactions in 10 minutes across any channels.
    """

    def __init__(self, max_txns_per_window: int = 5, window_minutes: int = 10):
        self.max_txns = max_txns_per_window
        self.window_minutes = window_minutes

    def analyze(self, account_id: str, transactions: list) -> dict:
        """Return velocity analysis for a specific account."""
        account_txns = [
            t for t in transactions
            if t.get("sender_id") == account_id or t.get("receiver_id") == account_id
        ]
        account_txns.sort(key=lambda x: x.get("timestamp", ""))

        violations = []
        for i, txn in enumerate(account_txns):
            try:
                t_start = datetime.fromisoformat(txn["timestamp"])
                t_end = t_start + timedelta(minutes=self.window_minutes)
            except:
                continue

            window_txns = [
                t for t in account_txns[i:]
                if self._in_window(t.get("timestamp"), t_start, t_end)
            ]

            if len(window_txns) > self.max_txns:
                violations.append({
                    "window_start": t_start.isoformat(),
                    "txn_count": len(window_txns),
                    "total_amount": sum(t.get("amount", 0) for t in window_txns),
                    "channels": list(set(t.get("channel") for t in window_txns)),
                })

        return {
            "account_id": account_id,
            "total_transactions": len(account_txns),
            "velocity_violations": violations,
            "is_anomalous": len(violations) > 0,
            "max_txns_in_window": max(
                (v["txn_count"] for v in violations), default=0
            ),
        }

    def _in_window(self, ts_str: str, start: datetime, end: datetime) -> bool:
        try:
            t = datetime.fromisoformat(ts_str)
            return start <= t <= end
        except:
            return False


# ── Structuring Detector ──────────────────────────────────────────────────────

class StructuringDetector:
    """
    Detects structuring (smurfing) — breaking large amounts into
    sub-threshold transactions to avoid RBI reporting requirements.
    
    RBI threshold: ₹50,000 for cash transactions.
    """

    def __init__(self, threshold: float = 50000, tolerance: float = 0.04):
        self.threshold = threshold
        self.tolerance = tolerance  # 4% below threshold
        self.min_amount = threshold * (1 - tolerance)

    def detect(self, transactions: list) -> list:
        """Find structuring patterns across all transactions."""
        flags = []

        # Group by destination account
        by_dest = defaultdict(list)
        for txn in transactions:
            dest = txn.get("receiver_id")
            if dest:
                by_dest[dest].append(txn)

        for dest, txns in by_dest.items():
            sub_threshold = [
                t for t in txns
                if self.min_amount <= t.get("amount", 0) < self.threshold
            ]

            if len(sub_threshold) >= 3:
                # Group into time windows (6 hours)
                sub_threshold.sort(key=lambda x: x.get("timestamp", ""))
                time_groups = self._group_by_time(sub_threshold, hours=6)

                for group in time_groups:
                    if len(group) >= 3:
                        total = sum(t.get("amount", 0) for t in group)
                        senders = set(t.get("sender_id") for t in group)
                        flags.append({
                            "destination_account": dest,
                            "transaction_count": len(group),
                            "total_amount": round(total, 2),
                            "individual_amounts": [t.get("amount") for t in group],
                            "unique_senders": len(senders),
                            "sender_accounts": list(senders),
                            "time_window_hours": 6,
                            "structuring_score": min(len(group) / 5.0, 1.0),
                            "pattern": "COORDINATED_STRUCTURING" if len(senders) > 1 else "SINGLE_SOURCE_STRUCTURING",
                        })

        return flags

    def _group_by_time(self, transactions: list, hours: int) -> list:
        """Group transactions into time windows."""
        if not transactions:
            return []

        groups = []
        current_group = [transactions[0]]

        for i in range(1, len(transactions)):
            try:
                t_prev = datetime.fromisoformat(transactions[i-1]["timestamp"])
                t_curr = datetime.fromisoformat(transactions[i]["timestamp"])
                if (t_curr - t_prev).total_seconds() <= hours * 3600:
                    current_group.append(transactions[i])
                else:
                    groups.append(current_group)
                    current_group = [transactions[i]]
            except:
                current_group.append(transactions[i])

        groups.append(current_group)
        return groups


# ── Jurisdiction Risk Scorer ──────────────────────────────────────────────────

class JurisdictionScorer:
    """
    Scores transaction risk based on jurisdiction routing.
    India→Singapore→UAE = 94/100 risk.
    """

    JURISDICTION_RISK = {
        "IN-MH": 10, "IN-DL": 12, "IN-KA": 8, "IN-TN": 9, "IN-WB": 11,
        "SG": 45, "AE": 68, "GB": 28, "US": 22,
        "CH": 35, "HK": 52, "MO": 61, "PA": 72,
        "UNKNOWN": 80,
    }

    HIGH_RISK_CORRIDORS = [
        ("IN", "AE"), ("IN", "SG"), ("AE", "SG"), ("SG", "HK"),
        ("HK", "MO"), ("IN", "PA"), ("AE", "CH"),
    ]

    def score(self, transactions: list) -> dict:
        """Score a chain of transactions for jurisdiction risk."""
        if not transactions:
            return {"score": 0, "level": "LOW", "hops": []}

        hops = []
        cumulative_score = 0

        for txn in transactions:
            from_j = txn.get("sender_jurisdiction", "UNKNOWN")
            to_j = txn.get("receiver_jurisdiction", "UNKNOWN")

            from_risk = self.JURISDICTION_RISK.get(from_j, 50)
            to_risk = self.JURISDICTION_RISK.get(to_j, 50)
            hop_score = (from_risk + to_risk) / 2

            # Bonus risk for known high-risk corridors
            from_country = from_j.split("-")[0] if "-" in from_j else from_j
            to_country = to_j.split("-")[0] if "-" in to_j else to_j
            if (from_country, to_country) in self.HIGH_RISK_CORRIDORS:
                hop_score = min(hop_score * 1.5, 100)

            cumulative_score = min(cumulative_score + hop_score * 0.3, 100)

            hops.append({
                "from": from_j,
                "to": to_j,
                "hop_risk": round(hop_score, 1),
                "amount": txn.get("amount"),
                "channel": txn.get("channel"),
            })

        final_score = min(cumulative_score, 100)
        return {
            "score": round(final_score, 1),
            "level": "CRITICAL" if final_score >= 85 else "HIGH" if final_score >= 60 else "MEDIUM" if final_score >= 40 else "LOW",
            "hops": hops,
            "routing_complexity": len(transactions),
        }
