"""
ShaktiSafe — Jurisdiction Risk Scorer
FATF 20-country risk matrix with hop-based scoring.
Score > 60 = HIGH RISK | Score > 80 = BLOCK
"""

from typing import List, Dict


# 20-country FATF risk matrix (score 0–100)
JURISDICTION_RISK = {
    # Domestic
    "IN":  {"score": 9,  "status": "Domestic",          "label": "India"},
    # FATF Full Members (lower risk)
    "SG":  {"score": 22, "status": "FATF Member",        "label": "Singapore"},
    "GB":  {"score": 18, "status": "FATF Member",        "label": "United Kingdom"},
    "US":  {"score": 20, "status": "FATF Member",        "label": "United States"},
    "DE":  {"score": 17, "status": "FATF Member",        "label": "Germany"},
    "JP":  {"score": 16, "status": "FATF Member",        "label": "Japan"},
    "AU":  {"score": 19, "status": "FATF Member",        "label": "Australia"},
    "CH":  {"score": 25, "status": "FATF Member",        "label": "Switzerland"},
    "HK":  {"score": 30, "status": "FATF Member",        "label": "Hong Kong"},
    # FATF Grey List (increased monitoring)
    "AE":  {"score": 65, "status": "FATF Grey List",     "label": "UAE"},
    "PK":  {"score": 75, "status": "FATF Grey List",     "label": "Pakistan"},
    "MM":  {"score": 72, "status": "FATF Grey List",     "label": "Myanmar"},
    "SY":  {"score": 78, "status": "FATF Grey List",     "label": "Syria"},
    "YE":  {"score": 76, "status": "FATF Grey List",     "label": "Yemen"},
    "ET":  {"score": 68, "status": "FATF Grey List",     "label": "Ethiopia"},
    # High-risk / Monitored
    "PA":  {"score": 78, "status": "Grey List",          "label": "Panama"},
    "MO":  {"score": 72, "status": "Monitored",          "label": "Macau"},
    "VG":  {"score": 70, "status": "Offshore",           "label": "British Virgin Islands"},
    "KY":  {"score": 68, "status": "Offshore",           "label": "Cayman Islands"},
    "KP":  {"score": 95, "status": "FATF Black List",    "label": "North Korea"},
    "IR":  {"score": 92, "status": "FATF Black List",    "label": "Iran"},
}

DEFAULT_RISK     = {"score": 40, "status": "Unknown",  "label": "Unknown"}
CORRIDOR_PENALTY = 10    # additional score for cross-border transaction
HIGH_RISK_SCORE  = 60
BLOCK_SCORE      = 80


class JurisdictionScorer:
    """
    Scores transaction paths through jurisdictions using the FATF risk matrix.
    Accumulates hop risks + corridor penalty.
    """

    def score_transaction(self, txn: Dict) -> Dict:
        """Score a single transaction's jurisdictional risk."""
        sender_j   = txn.get("sender_jurisdiction",   "IN")
        receiver_j = txn.get("receiver_jurisdiction", "IN")

        s_info = JURISDICTION_RISK.get(sender_j,   DEFAULT_RISK)
        r_info = JURISDICTION_RISK.get(receiver_j, DEFAULT_RISK)

        is_cross_border = sender_j != receiver_j
        penalty         = CORRIDOR_PENALTY if is_cross_border else 0
        raw_score       = max(s_info["score"], r_info["score"]) + penalty
        score           = min(raw_score, 100)

        action = "MONITOR"
        if score > BLOCK_SCORE:
            action = "BLOCK"
        elif score > HIGH_RISK_SCORE:
            action = "FLAG"

        evidence = []
        if r_info["status"] in ("FATF Grey List", "FATF Black List", "Offshore"):
            evidence.append(f"Receiver in {r_info['label']} ({r_info['status']})")
        if s_info["status"] in ("FATF Grey List", "FATF Black List"):
            evidence.append(f"Sender in {s_info['label']} ({s_info['status']})")
        if is_cross_border:
            evidence.append(f"Cross-border transaction: {sender_j}→{receiver_j} +{penalty} penalty")

        return {
            "txn_id":            txn.get("txn_id", ""),
            "sender_jurisdiction": sender_j,
            "receiver_jurisdiction": receiver_j,
            "sender_risk_score": s_info["score"],
            "receiver_risk_score": r_info["score"],
            "combined_score":    score,
            "action":            action,
            "is_cross_border":   is_cross_border,
            "evidence":          evidence,
        }

    def score_hop_chain(self, jurisdictions: List[str]) -> Dict:
        """
        Score a multi-hop chain of jurisdictions (e.g. SWIFT layering).
        sum(hop_risks) + corridor_penalty per hop.
        """
        total_score = 0
        hops        = []
        for j in jurisdictions:
            info = JURISDICTION_RISK.get(j, DEFAULT_RISK)
            total_score += info["score"]
            hops.append({"jurisdiction": j, "score": info["score"], "status": info["status"]})

        # Corridor penalty for each cross-border hop
        for i in range(len(jurisdictions) - 1):
            if jurisdictions[i] != jurisdictions[i+1]:
                total_score += CORRIDOR_PENALTY

        action = "BLOCK" if total_score > BLOCK_SCORE else \
                 "FLAG"  if total_score > HIGH_RISK_SCORE else "MONITOR"

        return {
            "jurisdictions":   jurisdictions,
            "hop_count":       len(jurisdictions),
            "total_score":     min(total_score, 100),
            "action":          action,
            "hops":            hops,
        }

    def scan_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Return flagged transactions with jurisdiction risk scores."""
        flagged = []
        for t in transactions:
            result = self.score_transaction(t)
            if result["action"] in ("FLAG", "BLOCK"):
                flagged.append({
                    "alert_type":  "JURISDICTION_RISK",
                    "action":      result["action"],
                    "txn_id":      t.get("txn_id"),
                    "amount":      t.get("amount"),
                    "channel":     t.get("channel"),
                    "risk_score":  result["combined_score"],
                    "evidence":    result["evidence"],
                    "sender_jurisdiction": result["sender_jurisdiction"],
                    "receiver_jurisdiction": result["receiver_jurisdiction"],
                    "confidence":  result["combined_score"] / 100.0,
                })
        return flagged

    def get_risk_info(self, jurisdiction_code: str) -> Dict:
        return JURISDICTION_RISK.get(jurisdiction_code, DEFAULT_RISK)

    def get_risk_matrix(self) -> Dict:
        return JURISDICTION_RISK.copy()
