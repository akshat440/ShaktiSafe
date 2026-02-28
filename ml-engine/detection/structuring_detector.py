"""
ShaktiSafe — Structuring / Smurfing Detector
Rolling 24-hour window scan for transactions in INR 45,000–49,999 band.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict


STRUCTURING_LOW  = 45_000
STRUCTURING_HIGH = 49_999
STRUCTURING_MIN_TXNS = 3       # ≥3 txns to same destination
WINDOW_HOURS     = 24


class StructuringDetector:
    """
    Threshold-band analysis per RBI INR 50,000 reporting requirement.
    Flags coordinated below-threshold transactions that collectively
    exceed the reporting threshold.
    """

    def __init__(self, low: float = STRUCTURING_LOW, high: float = STRUCTURING_HIGH,
                 min_txns: int = STRUCTURING_MIN_TXNS, window_hours: int = WINDOW_HOURS):
        self.low          = low
        self.high         = high
        self.min_txns     = min_txns
        self.window_hours = window_hours

    def detect(self, transactions: List[Dict]) -> List[Dict]:
        """
        Scan transactions and return structuring alerts.
        Each alert groups coordinated below-threshold transactions.
        """
        # Filter to structuring band
        band_txns = [t for t in transactions
                     if self.low <= t.get("amount", 0) <= self.high]

        if not band_txns:
            return []

        # Group by (sender, receiver) within rolling 24hr window
        alerts = []
        parsed = [(t, self._parse_ts(t)) for t in band_txns]
        parsed.sort(key=lambda x: x[1])

        # Sliding window over sorted band transactions
        checked = set()
        for i, (t, ts) in enumerate(parsed):
            key = (t.get("sender_id"), t.get("receiver_id"))
            if key in checked:
                continue

            window_end   = ts + timedelta(hours=self.window_hours)
            window_group = [
                tt for tt, tts in parsed[i:]
                if tt.get("sender_id")   == key[0]
                and tt.get("receiver_id") == key[1]
                and tts <= window_end
            ]

            if len(window_group) >= self.min_txns:
                total = sum(tt["amount"] for tt in window_group)
                alerts.append({
                    "alert_type":   "STRUCTURING",
                    "action":       "FILE_CTR",
                    "sender_id":    key[0],
                    "receiver_id":  key[1],
                    "txn_count":    len(window_group),
                    "total_amount": round(total, 2),
                    "window_hours": self.window_hours,
                    "txn_ids":      [tt["txn_id"] for tt in window_group],
                    "channels":     list(set(tt.get("channel", "") for tt in window_group)),
                    "evidence":     [
                        f"{len(window_group)} transactions in INR {self.low:,}–{self.high:,} band",
                        f"Total aggregate: INR {total:,.0f} (above INR 50,000 threshold)",
                        f"Window: {self.window_hours}h rolling",
                    ],
                    "confidence": min(1.0, len(window_group) / 10),
                    "detected_at": datetime.now().isoformat(),
                })
                checked.add(key)

        # Also detect: multiple senders → same receiver (smurfing)
        recv_groups = defaultdict(list)
        for t, ts in parsed:
            recv_groups[t.get("receiver_id")].append((t, ts))

        for recv_id, group in recv_groups.items():
            senders = set(t.get("sender_id") for t, _ in group)
            if len(senders) >= 3:
                window_txns = [t for t, _ in group]
                total = sum(t["amount"] for t in window_txns)
                alert_key = ("SMURFING", recv_id)
                if alert_key not in checked:
                    alerts.append({
                        "alert_type":       "SMURFING",
                        "action":           "FILE_CTR",
                        "receiver_id":      recv_id,
                        "coordinated_senders": list(senders),
                        "sender_count":     len(senders),
                        "txn_count":        len(window_txns),
                        "total_amount":     round(total, 2),
                        "txn_ids":          [t["txn_id"] for t in window_txns],
                        "evidence":         [
                            f"{len(senders)} coordinated senders to same receiver",
                            f"All transactions in INR {self.low:,}–{self.high:,} structuring band",
                            f"Collective total: INR {total:,.0f}",
                        ],
                        "confidence":       min(1.0, len(senders) / 10),
                        "detected_at":      datetime.now().isoformat(),
                    })
                    checked.add(alert_key)

        return alerts

    def _parse_ts(self, txn: Dict) -> datetime:
        try:
            return datetime.fromisoformat(txn.get("timestamp", "2026-01-01T00:00:00"))
        except Exception:
            return datetime(2026, 1, 1)
