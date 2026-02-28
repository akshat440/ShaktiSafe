"""
IntelliTrace — Synthetic Transaction Data Generator
Generates realistic banking transactions with 5 embedded mule ring scenarios.
All data is statistically realistic for Indian banking context.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

random.seed(42)

# ── Constants ──────────────────────────────────────────────────────────────────
CHANNELS = ["MOBILE_APP", "WEB", "ATM", "UPI", "NEFT", "IMPS"]
BANKS = ["SBI", "HDFC", "ICICI", "AXIS", "PNB", "CANARA", "KOTAK", "BOB"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"]
JURISDICTIONS = ["IN-MH", "IN-DL", "IN-KA", "IN-TN", "SG", "AE", "GB", "US"]
JURISDICTION_RISK = {"IN-MH": 10, "IN-DL": 12, "IN-KA": 8, "IN-TN": 9,
                     "SG": 45, "AE": 65, "GB": 30, "US": 25}

BASE_TIME = datetime(2024, 1, 1, 0, 0, 0)

# ── Helper Functions ───────────────────────────────────────────────────────────

def gen_account_id(prefix="ACC"):
    return f"{prefix}{random.randint(100000, 999999)}"

def gen_device_id():
    return f"DEV{hashlib.md5(str(random.random()).encode()).hexdigest()[:8].upper()}"

def gen_ip():
    return f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

def random_time(base: datetime, max_days: int = 30) -> datetime:
    return base + timedelta(
        days=random.randint(0, max_days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )

def ts(dt: datetime) -> str:
    return dt.isoformat()

# ── Account Pool ───────────────────────────────────────────────────────────────

def generate_account_pool(n: int = 500) -> List[Dict]:
    accounts = []
    for _ in range(n):
        acc_id = gen_account_id()
        accounts.append({
            "account_id": acc_id,
            "bank": random.choice(BANKS),
            "city": random.choice(CITIES),
            "jurisdiction": random.choice(JURISDICTIONS[:4]),  # Mostly domestic
            "device_id": gen_device_id(),
            "ip_address": gen_ip(),
            "account_age_days": random.randint(30, 3650),
            "kyc_verified": random.choice([True, True, True, False]),
            "account_type": random.choice(["SAVINGS", "CURRENT", "WALLET"]),
            "is_mule": False,
            "risk_score": random.randint(5, 30)
        })
    return accounts

# ── Legitimate Transactions ────────────────────────────────────────────────────

def generate_legitimate_transactions(accounts: List[Dict], n: int = 8000) -> List[Dict]:
    txns = []
    for _ in range(n):
        sender = random.choice(accounts)
        receiver = random.choice(accounts)
        while receiver["account_id"] == sender["account_id"]:
            receiver = random.choice(accounts)

        amount = round(random.lognormvariate(9, 1.5), 2)  # Log-normal: realistic
        amount = min(amount, 500000)

        txn_time = random_time(BASE_TIME, 60)
        channel = random.choice(CHANNELS)

        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": sender["account_id"],
            "receiver_id": receiver["account_id"],
            "amount": amount,
            "currency": "INR",
            "channel": channel,
            "timestamp": ts(txn_time),
            "sender_bank": sender["bank"],
            "receiver_bank": receiver["bank"],
            "sender_jurisdiction": sender["jurisdiction"],
            "receiver_jurisdiction": receiver["jurisdiction"],
            "device_id": sender["device_id"],
            "ip_address": sender["ip_address"],
            "label": "LEGITIMATE",
            "scenario": None,
            "latency_ms": random.randint(100, 2000)
        })
    return txns

# ── SCENARIO 1: Classic Mule Ring (App → Wallet → ATM) ───────────────────────

def scenario_classic_mule_ring(base_time: datetime) -> tuple:
    """
    6 accounts. Funds enter via Mobile App, chain through wallets, exit ATM.
    All within 4 minutes. Classic layering pattern.
    """
    ring_accounts = []
    for i in range(6):
        acc = {
            "account_id": f"MULE_RING1_{i+1:02d}",
            "bank": random.choice(BANKS),
            "city": "Mumbai",
            "jurisdiction": "IN-MH",
            "device_id": gen_device_id(),
            "ip_address": gen_ip(),
            "account_age_days": random.randint(10, 60),  # New accounts — red flag
            "kyc_verified": False,
            "account_type": "WALLET" if i in [1, 2, 3] else "SAVINGS",
            "is_mule": True,
            "risk_score": 0,  # Will be computed by GNN
            "scenario": "CLASSIC_MULE_RING"
        }
        ring_accounts.append(acc)

    txns = []
    t = base_time
    amount = 230000.0  # ₹2.3 Lakh

    # Step 1: Entry via Mobile App
    txns.append({
        "txn_id": str(uuid.uuid4()),
        "sender_id": "EXTERNAL_SOURCE_01",
        "receiver_id": ring_accounts[0]["account_id"],
        "amount": amount,
        "currency": "INR",
        "channel": "MOBILE_APP",
        "timestamp": ts(t),
        "sender_bank": "UNKNOWN",
        "receiver_bank": ring_accounts[0]["bank"],
        "sender_jurisdiction": "AE",
        "receiver_jurisdiction": "IN-MH",
        "device_id": ring_accounts[0]["device_id"],
        "ip_address": ring_accounts[0]["ip_address"],
        "label": "MULE",
        "scenario": "CLASSIC_MULE_RING",
        "latency_ms": 89
    })

    # Step 2-4: Wallet hops (within seconds)
    for i in range(3):
        t += timedelta(seconds=random.randint(30, 90))
        amount_reduced = amount * random.uniform(0.95, 0.99)  # Small cuts
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": ring_accounts[i]["account_id"],
            "receiver_id": ring_accounts[i+1]["account_id"],
            "amount": round(amount_reduced, 2),
            "currency": "INR",
            "channel": "UPI",
            "timestamp": ts(t),
            "sender_bank": ring_accounts[i]["bank"],
            "receiver_bank": ring_accounts[i+1]["bank"],
            "sender_jurisdiction": "IN-MH",
            "receiver_jurisdiction": "IN-MH",
            "device_id": ring_accounts[i]["device_id"],
            "ip_address": ring_accounts[i]["ip_address"],
            "label": "MULE",
            "scenario": "CLASSIC_MULE_RING",
            "latency_ms": random.randint(50, 200)
        })
        amount = amount_reduced

    # Step 5-6: ATM withdrawals (split to avoid detection — but still flagged)
    for i in [4, 5]:
        t += timedelta(seconds=random.randint(60, 120))
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": ring_accounts[3]["account_id"],
            "receiver_id": ring_accounts[i]["account_id"],
            "amount": round(amount / 2, 2),
            "currency": "INR",
            "channel": "ATM",
            "timestamp": ts(t),
            "sender_bank": ring_accounts[3]["bank"],
            "receiver_bank": ring_accounts[i]["bank"],
            "sender_jurisdiction": "IN-MH",
            "receiver_jurisdiction": "IN-MH",
            "device_id": ring_accounts[i]["device_id"],
            "ip_address": ring_accounts[i]["ip_address"],
            "label": "MULE",
            "scenario": "CLASSIC_MULE_RING",
            "latency_ms": random.randint(1000, 3000)
        })

    return ring_accounts, txns

# ── SCENARIO 2: Structuring / Smurfing ────────────────────────────────────────

def scenario_structuring(base_time: datetime) -> tuple:
    """
    12 transactions just below ₹50,000 RBI reporting threshold.
    Across 3 accounts in coordinated fashion.
    """
    accounts = []
    for i in range(3):
        accounts.append({
            "account_id": f"SMURF_{i+1:02d}",
            "bank": random.choice(BANKS),
            "city": "Delhi",
            "jurisdiction": "IN-DL",
            "device_id": gen_device_id(),
            "ip_address": gen_ip(),
            "account_age_days": random.randint(5, 90),
            "kyc_verified": random.choice([True, False]),
            "account_type": "SAVINGS",
            "is_mule": True,
            "risk_score": 0,
            "scenario": "STRUCTURING"
        })

    destination = {
        "account_id": "SMURF_DEST_01",
        "bank": "HDFC",
        "city": "Singapore",
        "jurisdiction": "SG",
        "device_id": gen_device_id(),
        "ip_address": gen_ip(),
        "account_age_days": 15,
        "kyc_verified": False,
        "account_type": "CURRENT",
        "is_mule": True,
        "risk_score": 0,
        "scenario": "STRUCTURING"
    }
    accounts.append(destination)

    txns = []
    t = base_time
    # 12 transactions × ₹49,500 = ₹5.94L total, all just under threshold
    for i in range(12):
        sender = accounts[i % 3]
        amount = random.uniform(49000, 49999)  # Just under ₹50,000
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": sender["account_id"],
            "receiver_id": destination["account_id"],
            "amount": round(amount, 2),
            "currency": "INR",
            "channel": random.choice(["NEFT", "IMPS", "UPI"]),
            "timestamp": ts(t),
            "sender_bank": sender["bank"],
            "receiver_bank": destination["bank"],
            "sender_jurisdiction": "IN-DL",
            "receiver_jurisdiction": "SG",
            "device_id": sender["device_id"],
            "ip_address": sender["ip_address"],
            "label": "MULE",
            "scenario": "STRUCTURING",
            "latency_ms": random.randint(200, 800)
        })
        t += timedelta(minutes=random.randint(8, 25))

    return accounts, txns

# ── SCENARIO 3: Cross-Jurisdiction Routing ────────────────────────────────────

def scenario_cross_jurisdiction(base_time: datetime) -> tuple:
    """
    Funds routed India → Singapore → UAE → back to India.
    Jurisdiction risk score spikes to 94/100.
    """
    hops = [
        {"id": "XJUR_IN_01", "jurisdiction": "IN-MH", "bank": "SBI"},
        {"id": "XJUR_SG_01", "jurisdiction": "SG", "bank": "DBS"},
        {"id": "XJUR_AE_01", "jurisdiction": "AE", "bank": "EMIRATES_NBD"},
        {"id": "XJUR_IN_02", "jurisdiction": "IN-KA", "bank": "ICICI"},
    ]
    accounts = []
    for h in hops:
        accounts.append({
            "account_id": h["id"],
            "bank": h["bank"],
            "city": "International",
            "jurisdiction": h["jurisdiction"],
            "device_id": gen_device_id(),
            "ip_address": gen_ip(),
            "account_age_days": random.randint(20, 180),
            "kyc_verified": random.choice([True, False]),
            "account_type": "CURRENT",
            "is_mule": True,
            "risk_score": 0,
            "scenario": "CROSS_JURISDICTION"
        })

    txns = []
    t = base_time
    amount = 850000.0
    for i in range(len(hops) - 1):
        t += timedelta(hours=random.randint(2, 8))
        amount *= 0.97
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": hops[i]["id"],
            "receiver_id": hops[i+1]["id"],
            "amount": round(amount, 2),
            "currency": "USD" if i > 0 else "INR",
            "channel": "SWIFT" if i > 0 else "NEFT",
            "timestamp": ts(t),
            "sender_bank": hops[i]["bank"],
            "receiver_bank": hops[i+1]["bank"],
            "sender_jurisdiction": hops[i]["jurisdiction"],
            "receiver_jurisdiction": hops[i+1]["jurisdiction"],
            "device_id": accounts[i]["device_id"],
            "ip_address": accounts[i]["ip_address"],
            "label": "MULE",
            "scenario": "CROSS_JURISDICTION",
            "latency_ms": random.randint(5000, 30000)
        })

    return accounts, txns

# ── SCENARIO 4: Nesting / Layering (4-hop shell chain) ───────────────────────

def scenario_nesting(base_time: datetime) -> tuple:
    """
    4-hop chain through shell accounts — each hop obfuscates origin.
    GNN traces the full path using edge traversal.
    """
    hops = [f"NEST_{i:02d}" for i in range(5)]
    accounts = []
    for h in hops:
        accounts.append({
            "account_id": h,
            "bank": random.choice(BANKS),
            "city": random.choice(CITIES),
            "jurisdiction": random.choice(["IN-MH", "IN-DL", "IN-KA"]),
            "device_id": gen_device_id(),
            "ip_address": gen_ip(),
            "account_age_days": random.randint(7, 45),
            "kyc_verified": False,
            "account_type": random.choice(["SAVINGS", "CURRENT", "WALLET"]),
            "is_mule": True,
            "risk_score": 0,
            "scenario": "NESTING"
        })

    txns = []
    t = base_time
    amount = 1200000.0
    for i in range(len(hops) - 1):
        t += timedelta(minutes=random.randint(15, 90))
        amount *= random.uniform(0.85, 0.95)  # Cut taken at each hop
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": hops[i],
            "receiver_id": hops[i+1],
            "amount": round(amount, 2),
            "currency": "INR",
            "channel": random.choice(["IMPS", "NEFT", "UPI"]),
            "timestamp": ts(t),
            "sender_bank": accounts[i]["bank"],
            "receiver_bank": accounts[i+1]["bank"],
            "sender_jurisdiction": accounts[i]["jurisdiction"],
            "receiver_jurisdiction": accounts[i+1]["jurisdiction"],
            "device_id": accounts[i]["device_id"],
            "ip_address": accounts[i]["ip_address"],
            "label": "MULE",
            "scenario": "NESTING",
            "latency_ms": random.randint(300, 1500)
        })

    return accounts, txns

# ── SCENARIO 5: Behaviour-Based Sanctions Evasion ─────────────────────────────

def scenario_sanctions_evasion(base_time: datetime) -> tuple:
    """
    Account doesn't appear on any sanctions list by name.
    But its behaviour exactly mirrors known sanctioned entities:
    - Round-number transfers to high-risk jurisdictions
    - Immediate withdrawal after receipt
    - Shared device with flagged account
    """
    accounts = [
        {
            "account_id": "SANC_EVADE_01",
            "bank": "AXIS",
            "city": "Mumbai",
            "jurisdiction": "IN-MH",
            "device_id": "KNOWN_BAD_DEVICE_001",  # Shared with flagged account
            "ip_address": gen_ip(),
            "account_age_days": 22,
            "kyc_verified": True,  # Passed KYC — that's the scary part
            "account_type": "CURRENT",
            "is_mule": True,
            "risk_score": 0,
            "scenario": "SANCTIONS_EVASION"
        },
        {
            "account_id": "SANC_EVADE_02",
            "bank": "KOTAK",
            "city": "Dubai",
            "jurisdiction": "AE",
            "device_id": gen_device_id(),
            "ip_address": gen_ip(),
            "account_age_days": 180,
            "kyc_verified": True,
            "account_type": "CURRENT",
            "is_mule": True,
            "risk_score": 0,
            "scenario": "SANCTIONS_EVASION"
        }
    ]

    txns = []
    t = base_time
    # Round number transfers — a known behavioural pattern of sanctioned entities
    for amount in [100000, 200000, 500000, 100000, 300000]:
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": "EXTERNAL_UNKNOWN_02",
            "receiver_id": accounts[0]["account_id"],
            "amount": float(amount),
            "currency": "INR",
            "channel": "NEFT",
            "timestamp": ts(t),
            "sender_bank": "UNKNOWN",
            "receiver_bank": accounts[0]["bank"],
            "sender_jurisdiction": "AE",
            "receiver_jurisdiction": "IN-MH",
            "device_id": accounts[0]["device_id"],
            "ip_address": accounts[0]["ip_address"],
            "label": "MULE",
            "scenario": "SANCTIONS_EVASION",
            "latency_ms": random.randint(100, 500)
        })
        t += timedelta(minutes=random.randint(2, 10))

        # Immediate withdrawal to AE
        t += timedelta(minutes=random.randint(1, 5))
        txns.append({
            "txn_id": str(uuid.uuid4()),
            "sender_id": accounts[0]["account_id"],
            "receiver_id": accounts[1]["account_id"],
            "amount": float(amount) * 0.99,
            "currency": "INR",
            "channel": "SWIFT",
            "timestamp": ts(t),
            "sender_bank": accounts[0]["bank"],
            "receiver_bank": accounts[1]["bank"],
            "sender_jurisdiction": "IN-MH",
            "receiver_jurisdiction": "AE",
            "device_id": accounts[0]["device_id"],
            "ip_address": accounts[0]["ip_address"],
            "label": "MULE",
            "scenario": "SANCTIONS_EVASION",
            "latency_ms": random.randint(500, 2000)
        })
        t += timedelta(minutes=random.randint(30, 120))

    return accounts, txns

# ── MAIN GENERATOR ─────────────────────────────────────────────────────────────

def generate_all():
    print("🔄 Generating account pool...")
    accounts = generate_account_pool(500)

    print("🔄 Generating legitimate transactions...")
    txns = generate_legitimate_transactions(accounts, 8000)

    print("🔄 Injecting Scenario 1: Classic Mule Ring...")
    s1_accounts, s1_txns = scenario_classic_mule_ring(BASE_TIME + timedelta(days=5, hours=14))
    accounts.extend(s1_accounts)
    txns.extend(s1_txns)

    print("🔄 Injecting Scenario 2: Structuring/Smurfing...")
    s2_accounts, s2_txns = scenario_structuring(BASE_TIME + timedelta(days=12, hours=9))
    accounts.extend(s2_accounts)
    txns.extend(s2_txns)

    print("🔄 Injecting Scenario 3: Cross-Jurisdiction Routing...")
    s3_accounts, s3_txns = scenario_cross_jurisdiction(BASE_TIME + timedelta(days=18, hours=11))
    accounts.extend(s3_accounts)
    txns.extend(s3_txns)

    print("🔄 Injecting Scenario 4: Nesting/Layering...")
    s4_accounts, s4_txns = scenario_nesting(BASE_TIME + timedelta(days=22, hours=16))
    accounts.extend(s4_accounts)
    txns.extend(s4_txns)

    print("🔄 Injecting Scenario 5: Sanctions Evasion Behaviour...")
    s5_accounts, s5_txns = scenario_sanctions_evasion(BASE_TIME + timedelta(days=28, hours=10))
    accounts.extend(s5_accounts)
    txns.extend(s5_txns)

    # Sort transactions by timestamp
    txns.sort(key=lambda x: x["timestamp"])

    stats = {
        "total_accounts": len(accounts),
        "total_transactions": len(txns),
        "mule_accounts": sum(1 for a in accounts if a.get("is_mule")),
        "mule_transactions": sum(1 for t in txns if t["label"] == "MULE"),
        "legitimate_transactions": sum(1 for t in txns if t["label"] == "LEGITIMATE"),
        "scenarios": {
            "CLASSIC_MULE_RING": sum(1 for t in txns if t["scenario"] == "CLASSIC_MULE_RING"),
            "STRUCTURING": sum(1 for t in txns if t["scenario"] == "STRUCTURING"),
            "CROSS_JURISDICTION": sum(1 for t in txns if t["scenario"] == "CROSS_JURISDICTION"),
            "NESTING": sum(1 for t in txns if t["scenario"] == "NESTING"),
            "SANCTIONS_EVASION": sum(1 for t in txns if t["scenario"] == "SANCTIONS_EVASION"),
        }
    }

    return accounts, txns, stats


if __name__ == "__main__":
    import os
    os.makedirs(os.path.join(os.path.dirname(__file__), "sample_data"), exist_ok=True)

    accounts, txns, stats = generate_all()

    with open("sample_data/accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)

    with open("sample_data/transactions.json", "w") as f:
        json.dump(txns, f, indent=2)

    with open("sample_data/stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print("\n✅ Data Generation Complete!")
    print(f"   Accounts:              {stats['total_accounts']}")
    print(f"   Total Transactions:    {stats['total_transactions']}")
    print(f"   Mule Accounts:         {stats['mule_accounts']}")
    print(f"   Mule Transactions:     {stats['mule_transactions']}")
    print(f"   Legitimate:            {stats['legitimate_transactions']}")
    print(f"\n   Scenarios injected:")
    for s, c in stats["scenarios"].items():
        print(f"     {s}: {c} transactions")
    print("\n   Files saved to sample_data/")
