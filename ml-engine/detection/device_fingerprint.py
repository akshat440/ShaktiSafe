"""
ShaktiSafe — Device Fingerprint Detector
Identifies shared-device patterns across accounts.
Multiple accounts sharing one device = strong mule signal.
"""

from collections import defaultdict
from typing import List, Dict
from datetime import datetime


class DeviceFingerprintDetector:
    """
    Hash-match device IDs across accounts.
    Flags device_id shared by ≥2 accounts as suspicious.
    """

    MIN_ACCOUNTS_PER_DEVICE = 2

    def detect(self, accounts: List[Dict], transactions: List[Dict]) -> List[Dict]:
        """Return device-sharing alerts grouped by device_id."""
        # Map device_id → list of accounts
        device_to_accounts = defaultdict(list)
        for acc in accounts:
            dev = acc.get("device_id", "")
            if dev:
                device_to_accounts[dev].append(acc)

        # Map device from transactions too
        for t in transactions:
            dev = t.get("device_id", "")
            if dev:
                # find which account used this device
                pass  # already captured via accounts

        alerts = []
        for device_id, accs in device_to_accounts.items():
            if len(accs) < self.MIN_ACCOUNTS_PER_DEVICE:
                continue

            # Get all transactions involving these accounts
            acc_ids  = {a["account_id"] for a in accs}
            dev_txns = [t for t in transactions
                        if t.get("sender_id") in acc_ids or t.get("receiver_id") in acc_ids]
            total_amt = sum(t["amount"] for t in dev_txns)
            channels  = list(set(t.get("channel","") for t in dev_txns))
            banks     = list(set(a.get("bank","") for a in accs))

            evidence = [
                f"{len(accs)} accounts share device {device_id[:12]}…",
                f"Accounts across {len(banks)} bank(s): {', '.join(banks[:3])}",
                f"{len(dev_txns)} transactions | INR {total_amt:,.0f} total",
            ]
            if len(channels) > 2:
                evidence.append(f"Cross-channel: {', '.join(channels[:4])}")

            alerts.append({
                "alert_type":    "DEVICE_FINGERPRINT",
                "action":        "REVIEW",
                "device_id":     device_id,
                "accounts":      [a["account_id"] for a in accs],
                "account_count": len(accs),
                "banks":         banks,
                "channels":      channels,
                "txn_count":     len(dev_txns),
                "total_amount":  round(total_amt, 2),
                "evidence":      evidence,
                "confidence":    min(1.0, (len(accs) - 1) / 5),
                "detected_at":   datetime.now().isoformat(),
            })

        return sorted(alerts, key=lambda x: x["account_count"], reverse=True)
