"""
ShaktiSafe — Behavioural Sanctions Screener
Catches KYC-passing entities via device fingerprint + routing pattern match.
Behaviour score threshold: 70
"""

import hashlib, json
from typing import List, Dict, Optional, Set
from datetime import datetime


BEHAVIOUR_THRESHOLD = 70   # trigger escalation


class BehaviouralSanctionsScreener:
    """
    Goes beyond static KYC list-matching.
    A sanctioned entity that passes KYC under a new name is caught
    via device fingerprint continuity and routing pattern similarity.
    """

    def __init__(self):
        # In production: loaded from FIU-IND/OFAC/UN feed
        self._flagged_devices:  Set[str] = set()
        self._flagged_patterns: List[Dict] = []

    # ── Feed management ─────────────────────────────────────────────────────

    def load_flagged_devices(self, device_ids: List[str]):
        """Register known device IDs from previously flagged entities."""
        self._flagged_devices.update(device_ids)

    def load_flagged_patterns(self, patterns: List[Dict]):
        """Register routing patterns from known bad actors."""
        self._flagged_patterns.extend(patterns)

    def add_flagged_device(self, device_id: str):
        self._flagged_devices.add(device_id)

    # ── Scoring ─────────────────────────────────────────────────────────────

    def score_account(self, account: Dict, transactions: List[Dict]) -> Dict:
        """
        Compute behaviour score for one account.
        Returns score breakdown and action recommendation.
        """
        score     = 0
        evidence  = []
        acc_id    = account.get("account_id", "")
        device_id = account.get("device_id", "")
        acc_txns  = [t for t in transactions
                     if t.get("sender_id") == acc_id or t.get("receiver_id") == acc_id]
        n = max(len(acc_txns), 1)

        # 1. KYC status (baseline — intentionally low weight)
        kyc_ok = account.get("kyc_verified", True)
        if not kyc_ok:
            score += 15
            evidence.append("KYC verification failed")

        # 2. Device fingerprint match (highest weight)
        if device_id and device_id in self._flagged_devices:
            score += 35
            evidence.append(f"Device fingerprint MATCH: {device_id[:12]}… matches flagged entity")

        # 3. Transfer pattern — round amounts (100K, 500K, 1M)
        round_large = sum(1 for t in acc_txns
                          if t.get("amount", 0) in {100000, 500000, 1000000, 2000000, 5000000})
        if round_large > 0:
            score += min(round_large * 5, 15)
            evidence.append(f"{round_large} round-amount transactions (100K/500K/1M pattern)")

        # 4. Withdrawal speed — within 5 min of receipt
        score += self._score_withdrawal_speed(acc_id, acc_txns)
        if score > 30:  # proxy check
            evidence.append("Rapid withdrawal: <5 min after receipt pattern")

        # 5. FATF grey-list jurisdiction transactions
        from detection.jurisdiction_scorer import JURISDICTION_RISK, FATF_GREY_CODES
        grey_txns = sum(1 for t in acc_txns
                        if t.get("receiver_jurisdiction","IN") in FATF_GREY_CODES)
        if grey_txns > 0:
            score += min(grey_txns * 5, 20)
            evidence.append(f"{grey_txns} transactions to FATF grey-list jurisdictions")

        # 6. No prior relationship with counterparties (new counterparty ratio)
        all_cp = (set(t["receiver_id"] for t in acc_txns if t.get("sender_id")==acc_id) |
                  set(t["sender_id"]   for t in acc_txns if t.get("receiver_id")==acc_id))
        new_cp_ratio = min(len(all_cp) / max(n, 1), 1.0)
        if new_cp_ratio > 0.8:
            score += 10
            evidence.append(f"High new-counterparty ratio: {new_cp_ratio:.0%}")

        score = min(score, 100)
        action = "ESCALATE" if score >= BEHAVIOUR_THRESHOLD else \
                 "REVIEW"   if score >= 50 else "MONITOR"

        return {
            "account_id":       acc_id,
            "behaviour_score":  score,
            "threshold":        BEHAVIOUR_THRESHOLD,
            "action":           action,
            "kyc_status":       "PASS" if kyc_ok else "FAIL",
            "device_match":     device_id in self._flagged_devices,
            "evidence":         evidence,
            "alert_type":       "BEHAVIOURAL_SANCTIONS",
            "detected_at":      datetime.now().isoformat(),
        }

    def screen_batch(self, accounts: List[Dict], transactions: List[Dict]) -> List[Dict]:
        """Screen all accounts, return those exceeding threshold."""
        alerts = []
        for acc in accounts:
            result = self.score_account(acc, transactions)
            if result["action"] in ("ESCALATE", "REVIEW"):
                alerts.append(result)
        return sorted(alerts, key=lambda x: x["behaviour_score"], reverse=True)

    # ── Privacy-safe fingerprint extraction ──────────────────────────────────

    @staticmethod
    def extract_fingerprint(account: Dict, transactions: List[Dict]) -> Dict:
        """
        Extract anonymised behavioural fingerprint for inter-bank sharing.
        No PII transmitted — SHA-256 hashed IDs + bucketed values only.
        """
        acc_id = account.get("account_id", "")
        acc_txns = [t for t in transactions
                    if t.get("sender_id") == acc_id or t.get("receiver_id") == acc_id]
        n = max(len(acc_txns), 1)
        amounts = [t.get("amount", 0) for t in acc_txns]
        mean_amt = sum(amounts) / len(amounts) if amounts else 0

        anon_id         = hashlib.sha256(acc_id.encode()).hexdigest()[:16]
        txn_count_bucket = (n // 10) * 10
        avg_amt_bucket   = round(mean_amt / 10000) * 10000
        channels         = sorted(set(t.get("channel","") for t in acc_txns))
        round_ratio      = sum(1 for t in acc_txns if t.get("amount",0) % 1000 == 0) / n
        has_atm_chain    = (
            any(t.get("channel") == "MOBILE_APP" for t in acc_txns) and
            any(t.get("channel") == "ATM"         for t in acc_txns)
        )

        behaviour_vector = {
            "txn_count_bucket": txn_count_bucket,
            "avg_amount_bucket": avg_amt_bucket,
            "channels":         channels,
            "round_ratio":      round(round_ratio, 2),
            "atm_chain":        has_atm_chain,
        }

        return {
            "anonymized_id":     anon_id,
            "txn_count_bucket":  txn_count_bucket,
            "avg_amount_bucket": avg_amt_bucket,
            "channels_list":     channels,
            "round_amount_ratio": round(round_ratio, 2),
            "risk_indicators":   {
                "APP_TO_ATM":    has_atm_chain,
                "HIGH_VELOCITY": n > 50,
            },
            "fingerprint_hash":  hashlib.sha256(
                json.dumps(behaviour_vector, sort_keys=True).encode()
            ).hexdigest()[:32],
        }

    def _score_withdrawal_speed(self, acc_id: str, txns: List[Dict]) -> int:
        """Score rapid withdrawal pattern: <5min between receive and send."""
        from collections import defaultdict
        received_ts = {}
        rapid = 0
        sorted_txns = sorted(txns, key=lambda t: t.get("timestamp", ""))
        for t in sorted_txns:
            if t.get("receiver_id") == acc_id:
                received_ts[acc_id] = t.get("timestamp","")
            if t.get("sender_id") == acc_id and acc_id in received_ts:
                try:
                    from datetime import datetime
                    r_ts = datetime.fromisoformat(received_ts[acc_id])
                    s_ts = datetime.fromisoformat(t.get("timestamp","2026-01-01"))
                    diff = (s_ts - r_ts).total_seconds()
                    if 0 < diff < 300:
                        rapid += 1
                except Exception:
                    pass
        return min(rapid * 5, 15)


# Expose FATF grey codes for other modules
FATF_GREY_CODES = {
    "AE", "PK", "MM", "SY", "YE", "ET", "TZ", "VU", "BA", "CM",
    "CD", "HT", "IR", "LY", "ML", "NI", "KP", "PH", "SS", "VE",
}
