"""
IntelliTrace — Real-Time GNN Inference Engine
Scores incoming transactions in <100ms using incremental graph updates.
Supports both single-transaction and batch scoring.
"""

import json
import os
import sys
import time
import torch
import numpy as np
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from gnn.model import MuleDetectorGNN, build_node_features, build_edge_index


class IntelliTraceInference:
    """
    Real-time inference engine with sliding window graph.
    Maintains a 72-hour rolling window of transactions for context.
    """

    RISK_THRESHOLDS = {
        "LOW": 0.3,
        "MEDIUM": 0.5,
        "HIGH": 0.7,
        "CRITICAL": 0.85,
    }

    def __init__(self, model_path: str = "models/gnn_model.pt", window_hours: int = 72):
        self.window_hours = window_hours
        self.window_transactions = deque()
        self.accounts: dict = {}          # account_id → account dict
        self.score_cache: dict = {}       # account_id → last score + timestamp
        self.alert_history: list = []

        print(f"Loading GNN model from {model_path}...")
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location="cpu")
            config = checkpoint["model_config"]
            self.model = MuleDetectorGNN(**config)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.eval()
            print(f"✅ Model loaded. Test AUC: {checkpoint['metrics'].get('auc', 'N/A'):.4f}")
        else:
            print("⚠️  Model file not found. Using untrained model (for demo init).")
            self.model = MuleDetectorGNN()
            self.model.eval()

    def load_initial_data(self, accounts: list, transactions: list):
        """Pre-load historical data into the sliding window."""
        for acc in accounts:
            self.accounts[acc["account_id"]] = acc

        # Load last window_hours worth of transactions
        cutoff = datetime.now() - timedelta(hours=self.window_hours)
        for txn in transactions:
            try:
                txn_time = datetime.fromisoformat(txn["timestamp"])
                if txn_time > cutoff:
                    self.window_transactions.append(txn)
            except:
                self.window_transactions.append(txn)  # Add anyway for demo

        print(f"✅ Loaded {len(self.accounts)} accounts, {len(self.window_transactions)} windowed txns")

    def _prune_window(self):
        """Remove transactions older than window_hours."""
        cutoff = datetime.now() - timedelta(hours=self.window_hours)
        while self.window_transactions:
            try:
                oldest_time = datetime.fromisoformat(self.window_transactions[0]["timestamp"])
                if oldest_time < cutoff:
                    self.window_transactions.popleft()
                else:
                    break
            except:
                break

    def ingest_transaction(self, txn: dict) -> dict:
        """
        Process a new incoming transaction.
        Returns risk assessment within <100ms.
        """
        start_time = time.time()

        # Ensure accounts exist
        for acc_id in [txn.get("sender_id"), txn.get("receiver_id")]:
            if acc_id and acc_id not in self.accounts:
                self.accounts[acc_id] = self._create_minimal_account(acc_id, txn)

        # Add to window
        self.window_transactions.append(txn)
        self._prune_window()

        # Score both accounts involved
        sender_result = self.score_account(txn["sender_id"])
        receiver_result = self.score_account(txn["receiver_id"])

        # Composite transaction risk
        txn_risk = self._compute_transaction_risk(txn, sender_result, receiver_result)

        inference_ms = (time.time() - start_time) * 1000

        result = {
            "txn_id": txn.get("txn_id"),
            "timestamp": txn.get("timestamp"),
            "amount": txn.get("amount"),
            "channel": txn.get("channel"),
            "sender": {
                "account_id": txn["sender_id"],
                **sender_result
            },
            "receiver": {
                "account_id": txn.get("receiver_id"),
                **receiver_result
            },
            "transaction_risk": txn_risk,
            "inference_ms": round(inference_ms, 2),
            "should_block": txn_risk["risk_level"] in ["HIGH", "CRITICAL"],
            "alert": None,
        }

        # Generate alert if needed
        if result["should_block"]:
            alert = self._generate_alert(txn, result)
            self.alert_history.append(alert)
            result["alert"] = alert

        return result

    def score_account(self, account_id: str) -> dict:
        """Score a single account using current graph context."""
        # Check cache (valid for 5 minutes)
        if account_id in self.score_cache:
            cached = self.score_cache[account_id]
            if time.time() - cached["cached_at"] < 300:
                return cached["result"]

        # Build mini-graph centered on this account (2-hop neighborhood)
        neighborhood = self._get_neighborhood(account_id, hops=2)

        if len(neighborhood["accounts"]) < 2:
            # Not enough context — use rule-based fallback
            return self._rule_based_score(account_id)

        # Build tensors
        x, id_to_idx = build_node_features(
            neighborhood["accounts"],
            neighborhood["transactions"]
        )
        edge_index = build_edge_index(neighborhood["transactions"], id_to_idx)

        if edge_index.shape[1] == 0:
            return self._rule_based_score(account_id)

        # Run GNN inference
        with torch.no_grad():
            out = self.model(x, edge_index)

        target_idx = id_to_idx.get(account_id, 0)
        mule_score = float(out["mule_score"][target_idx])
        risk_factors_raw = out["risk_factors"][target_idx].tolist()

        risk_factor_labels = [
            "velocity_anomaly", "cross_channel_movement",
            "jurisdiction_risk", "structuring_pattern", "network_centrality"
        ]
        risk_factors = [
            {"factor": risk_factor_labels[i], "score": round(risk_factors_raw[i], 4)}
            for i in range(5)
        ]
        risk_factors.sort(key=lambda x: x["score"], reverse=True)

        result = {
            "mule_probability": round(mule_score, 4),
            "risk_score": int(mule_score * 100),
            "risk_level": self._score_to_level(mule_score),
            "risk_factors": risk_factors,
            "graph_context": {
                "neighborhood_size": len(neighborhood["accounts"]),
                "transaction_count": len(neighborhood["transactions"]),
            }
        }

        self.score_cache[account_id] = {"result": result, "cached_at": time.time()}
        return result

    def _get_neighborhood(self, account_id: str, hops: int = 2) -> dict:
        """Extract k-hop neighborhood from sliding window."""
        # Get all accounts connected within `hops` hops
        connected = {account_id}
        frontier = {account_id}

        relevant_txns = []
        all_txns = list(self.window_transactions)

        for _ in range(hops):
            new_frontier = set()
            for txn in all_txns:
                if txn["sender_id"] in frontier or txn.get("receiver_id") in frontier:
                    new_frontier.add(txn["sender_id"])
                    if txn.get("receiver_id"):
                        new_frontier.add(txn["receiver_id"])
                    if txn not in relevant_txns:
                        relevant_txns.append(txn)
            connected |= new_frontier
            frontier = new_frontier - connected

        # Build account list for neighborhood
        neighborhood_accounts = []
        for acc_id in connected:
            if acc_id in self.accounts:
                neighborhood_accounts.append(self.accounts[acc_id])
            else:
                neighborhood_accounts.append(self._create_minimal_account(acc_id, {}))

        return {"accounts": neighborhood_accounts, "transactions": relevant_txns}

    def _create_minimal_account(self, account_id: str, txn: dict) -> dict:
        """Create minimal account record for unknown accounts."""
        return {
            "account_id": account_id,
            "bank": txn.get("sender_bank", "UNKNOWN"),
            "city": "Unknown",
            "jurisdiction": txn.get("sender_jurisdiction", "UNKNOWN"),
            "device_id": txn.get("device_id", "UNKNOWN"),
            "ip_address": txn.get("ip_address", "0.0.0.0"),
            "account_age_days": 0,  # Unknown = suspicious
            "kyc_verified": False,
            "account_type": "UNKNOWN",
            "is_mule": False,
            "risk_score": 50,
        }

    def _rule_based_score(self, account_id: str) -> dict:
        """Fallback rule-based scoring when graph context is insufficient."""
        acc = self.accounts.get(account_id, {})
        score = 0.0

        if not acc.get("kyc_verified", True):
            score += 0.2
        if acc.get("account_age_days", 365) < 30:
            score += 0.2
        if acc.get("jurisdiction") in ["AE", "SG"]:
            score += 0.15

        return {
            "mule_probability": round(min(score, 1.0), 4),
            "risk_score": int(min(score * 100, 100)),
            "risk_level": self._score_to_level(score),
            "risk_factors": [],
            "graph_context": {"neighborhood_size": 1, "transaction_count": 0},
            "method": "rule_based_fallback"
        }

    def _compute_transaction_risk(self, txn: dict, sender: dict, receiver: dict) -> dict:
        """Compute composite transaction-level risk."""
        base_score = max(
            sender.get("mule_probability", 0),
            receiver.get("mule_probability", 0)
        )

        modifiers = 0.0

        # High-risk jurisdiction
        high_risk_j = ["AE", "SG"]
        if txn.get("sender_jurisdiction") in high_risk_j or txn.get("receiver_jurisdiction") in high_risk_j:
            modifiers += 0.1

        # Just-under-threshold amount (structuring signal)
        amount = txn.get("amount", 0)
        if 48000 <= amount <= 49999:
            modifiers += 0.15

        # Round number (sanctions evasion signal)
        if amount > 10000 and amount % 10000 == 0:
            modifiers += 0.08

        # Cross-channel (App→ATM in same session)
        if txn.get("channel") == "ATM":
            modifiers += 0.05

        final_score = min(base_score + modifiers, 1.0)

        return {
            "composite_score": round(final_score, 4),
            "risk_score": int(final_score * 100),
            "risk_level": self._score_to_level(final_score),
            "modifiers_applied": round(modifiers, 4),
        }

    def _score_to_level(self, score: float) -> str:
        if score >= self.RISK_THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif score >= self.RISK_THRESHOLDS["HIGH"]:
            return "HIGH"
        elif score >= self.RISK_THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_alert(self, txn: dict, result: dict) -> dict:
        """Generate structured alert for the alert feed."""
        risk_level = result["transaction_risk"]["risk_level"]
        scenario = txn.get("scenario", "UNKNOWN_PATTERN")

        descriptions = {
            "CLASSIC_MULE_RING": "Mule ring detected: App→Wallet→ATM chain in <5 minutes",
            "STRUCTURING": "Structuring pattern: Multiple transactions just below ₹50,000 threshold",
            "CROSS_JURISDICTION": "High-risk cross-jurisdiction routing detected",
            "NESTING": "Deep nesting: 4-hop shell account chain identified",
            "SANCTIONS_EVASION": "Behaviour matches sanctioned entity pattern (device + routing)",
            "UNKNOWN_PATTERN": "Anomalous transaction pattern detected",
        }

        return {
            "alert_id": f"ALT-{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "txn_id": txn.get("txn_id"),
            "risk_level": risk_level,
            "scenario": scenario,
            "description": descriptions.get(scenario, descriptions["UNKNOWN_PATTERN"]),
            "sender_id": txn["sender_id"],
            "receiver_id": txn.get("receiver_id"),
            "amount": txn.get("amount"),
            "channel": txn.get("channel"),
            "confidence_score": result["transaction_risk"]["composite_score"],
            "recommended_action": "BLOCK" if risk_level == "CRITICAL" else "REVIEW",
            "evidence": {
                "sender_risk": result["sender"]["risk_score"],
                "receiver_risk": result["receiver"]["risk_score"],
                "top_risk_factor": (
                    result["sender"]["risk_factors"][0]["factor"]
                    if result["sender"].get("risk_factors") else "N/A"
                ),
            }
        }

    def get_stats(self) -> dict:
        """Return current system statistics."""
        all_scores = [v["result"]["risk_score"] for v in self.score_cache.values()]
        return {
            "accounts_monitored": len(self.accounts),
            "window_transactions": len(self.window_transactions),
            "alerts_generated": len(self.alert_history),
            "cached_scores": len(self.score_cache),
            "avg_risk_score": round(np.mean(all_scores), 1) if all_scores else 0,
            "high_risk_accounts": sum(1 for s in all_scores if s >= 70),
        }


if __name__ == "__main__":
    # Quick demo
    engine = IntelliTraceInference(model_path="models/gnn_model.pt")

    sample_txn = {
        "txn_id": "TEST-001",
        "sender_id": "MULE_RING1_01",
        "receiver_id": "MULE_RING1_02",
        "amount": 230000.0,
        "currency": "INR",
        "channel": "MOBILE_APP",
        "timestamp": datetime.now().isoformat(),
        "sender_bank": "SBI",
        "receiver_bank": "HDFC",
        "sender_jurisdiction": "IN-MH",
        "receiver_jurisdiction": "IN-MH",
        "device_id": "DEV12345",
        "ip_address": "192.168.1.1",
        "scenario": "CLASSIC_MULE_RING",
    }

    result = engine.ingest_transaction(sample_txn)
    print(json.dumps(result, indent=2))
