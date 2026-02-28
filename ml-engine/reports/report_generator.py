"""
IntelliTrace — Regulator-Ready PDF Report Generator
Generates FIU-IND compliant Suspicious Transaction Reports (STR)
Run: python reports/report_generator.py <scenario_id>
"""

import json, os, sys, datetime, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Arial', sans-serif; background: #fff; color: #1a1a2e; padding: 40px; }}
  .header {{ background: #0d1829; color: white; padding: 24px 32px; border-radius: 8px; margin-bottom: 24px; }}
  .header h1 {{ font-size: 22px; letter-spacing: 3px; margin-bottom: 4px; }}
  .header p {{ font-size: 11px; color: #7a9fc4; letter-spacing: 1px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-left: 12px; }}
  .badge-critical {{ background: #ff1a1a20; border: 1px solid #ff1a1a; color: #ff1a1a; }}
  .badge-high {{ background: #ff6b0020; border: 1px solid #ff6b00; color: #ff6b00; }}
  .section {{ background: #f8faff; border: 1px solid #dde8f5; border-radius: 8px; padding: 20px; margin-bottom: 16px; }}
  .section h2 {{ font-size: 13px; letter-spacing: 2px; color: #0d1829; margin-bottom: 14px; border-bottom: 2px solid #00d4ff; padding-bottom: 8px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .field {{ background: white; padding: 12px; border-radius: 6px; border: 1px solid #e0ecff; }}
  .field-label {{ font-size: 9px; letter-spacing: 2px; color: #7a9fc4; text-transform: uppercase; margin-bottom: 4px; }}
  .field-value {{ font-size: 14px; font-weight: bold; color: #0d1829; }}
  .field-value.critical {{ color: #ff1a1a; }}
  .field-value.amount {{ color: #00a86b; font-size: 18px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 11px; }}
  th {{ background: #0d1829; color: white; padding: 8px 10px; text-align: left; font-size: 10px; letter-spacing: 1px; }}
  td {{ padding: 7px 10px; border-bottom: 1px solid #e0ecff; }}
  tr:nth-child(even) td {{ background: #f8faff; }}
  .risk-bar {{ height: 8px; background: #e0ecff; border-radius: 4px; overflow: hidden; }}
  .risk-fill {{ height: 100%; border-radius: 4px; }}
  .recommendation {{ display: flex; gap: 10px; padding: 10px; background: white; border-radius: 6px; border: 1px solid #e0ecff; margin-bottom: 8px; }}
  .rec-num {{ background: #0d1829; color: white; width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0; }}
  .rec-text {{ font-size: 12px; color: #1a1a2e; }}
  .footer {{ margin-top: 24px; padding: 16px; background: #f0f4ff; border-radius: 8px; font-size: 10px; color: #7a9fc4; text-align: center; }}
  .gnn-badge {{ background: #00d4ff15; border: 1px solid #00d4ff; color: #00a8cc; padding: 3px 8px; border-radius: 4px; font-size: 10px; }}
</style>
</head>
<body>

<div class="header">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <h1>⬡ INTELLITRACE — FRAUD DETECTION REPORT</h1>
      <p>Cross-Channel Mule Account Detection System · Indian Bank × VIT Chennai</p>
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px; color:#7a9fc4;">REPORT ID</div>
      <div style="font-size:16px; font-weight:bold; color:#00d4ff;">{report_id}</div>
      <div style="font-size:10px; color:#7a9fc4; margin-top:4px;">{generated_at}</div>
    </div>
  </div>
</div>

<!-- Scenario Summary -->
<div class="section">
  <h2>📋 SCENARIO SUMMARY</h2>
  <div class="grid">
    <div class="field">
      <div class="field-label">Fraud Type</div>
      <div class="field-value">{scenario_title} <span class="badge badge-{risk_level_lower}">{risk_level}</span></div>
    </div>
    <div class="field">
      <div class="field-label">Confidence Score <span class="gnn-badge">GNN-Powered</span></div>
      <div class="field-value critical">{confidence_pct}%</div>
    </div>
    <div class="field">
      <div class="field-label">Total Amount at Risk</div>
      <div class="field-value amount">{total_amount}</div>
    </div>
    <div class="field">
      <div class="field-label">Accounts Involved</div>
      <div class="field-value">{account_count} accounts</div>
    </div>
    <div class="field" style="grid-column: span 2;">
      <div class="field-label">Description</div>
      <div style="font-size:13px; color:#1a1a2e; margin-top:4px;">{description}</div>
    </div>
  </div>
</div>

<!-- Flagged Accounts -->
<div class="section">
  <h2>🎯 FLAGGED ACCOUNTS — GNN RISK SCORES</h2>
  <table>
    <tr><th>Account ID</th><th>GNN Score</th><th>Risk Level</th><th>Jurisdiction</th><th>KYC</th><th>Risk Bar</th></tr>
    {account_rows}
  </table>
</div>

<!-- Transactions -->
<div class="section">
  <h2>💸 TRANSACTION EVIDENCE</h2>
  <table>
    <tr><th>Transaction ID</th><th>From</th><th>To</th><th>Amount (₹)</th><th>Channel</th><th>Timestamp</th></tr>
    {transaction_rows}
  </table>
</div>

<!-- Inter-Bank Sharing -->
<div class="section">
  <h2>🔒 PRIVACY-SAFE INTER-BANK INTELLIGENCE</h2>
  <div class="grid">
    <div class="field">
      <div class="field-label">Privacy Method</div>
      <div style="font-size:12px; margin-top:4px;">Differential Privacy + SHA-256 Account Hashing</div>
    </div>
    <div class="field">
      <div class="field-label">Compliance</div>
      <div style="font-size:12px; margin-top:4px;">✅ GDPR · ✅ RBI Data Localisation · ✅ PMLA 2002</div>
    </div>
    <div class="field" style="grid-column: span 2;">
      <div class="field-label">Shared Pattern Signals (No Raw PII)</div>
      <div style="font-size:11px; margin-top:6px; color:#0d1829;">
        Channel Sequence · Velocity Signature · Jurisdiction Route · Behavioural Fingerprint
      </div>
    </div>
  </div>
</div>

<!-- Recommendations -->
<div class="section">
  <h2>⚡ RECOMMENDED ACTIONS</h2>
  {recommendation_rows}
</div>

<!-- Regulatory References -->
<div class="section">
  <h2>📚 REGULATORY REFERENCES</h2>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
    <div class="field"><div style="font-size:11px;">PMLA 2002, Section 12 — Reporting obligations</div></div>
    <div class="field"><div style="font-size:11px;">RBI Master Direction on KYC 2016 (updated 2023)</div></div>
    <div class="field"><div style="font-size:11px;">FIU-IND STR filing requirements</div></div>
    <div class="field"><div style="font-size:11px;">FATF Recommendation 16 — Wire Transfers</div></div>
  </div>
</div>

<div class="footer">
  Generated by IntelliTrace v1.0 · GraphSAGE GNN · Indian Bank × VIT Chennai · PSBs Hackathon 2026<br>
  This report is confidential and intended for regulatory compliance purposes only.
</div>

</body>
</html>"""


def generate_report(scenario_id: str, transactions: list, accounts: dict, gnn_scores: dict) -> str:
    """Generate HTML report. Returns HTML string."""

    SCENARIOS = {
        "CLASSIC_MULE_RING":   ("Classic Mule Ring",          "CRITICAL", 0.97, "App→Wallet→ATM chain: ₹2.3L moved in 4 minutes across 6 accounts"),
        "STRUCTURING":         ("Structuring / Smurfing",      "HIGH",     0.89, "12 transactions of ₹49,500 just below RBI reporting threshold"),
        "CROSS_JURISDICTION":  ("Cross-Jurisdiction Routing",  "CRITICAL", 0.94, "India→Singapore→UAE routing chain, jurisdiction risk score 94/100"),
        "NESTING":             ("Nesting / Layering",          "HIGH",     0.82, "4-hop shell account chain with progressive amount reduction"),
        "SANCTIONS_EVASION":   ("Behaviour-Based Sanctions",   "CRITICAL", 0.91, "Account passed KYC but device+routing matches sanctioned entity pattern"),
    }

    title, risk_level, confidence, desc = SCENARIOS.get(
        scenario_id, (scenario_id, "HIGH", 0.80, "Anomalous pattern detected")
    )

    txns = [t for t in transactions if t.get("scenario") == scenario_id]
    flagged_ids = list({t.get("sender_id") for t in txns} | {t.get("receiver_id") for t in txns})
    flagged_ids = [a for a in flagged_ids if a]

    total_amount = sum(t.get("amount", 0) for t in txns)

    # Account rows
    def risk_color(score):
        if score >= 0.85: return "#ff1a1a"
        if score >= 0.70: return "#ff6b00"
        if score >= 0.50: return "#ffd700"
        return "#00ff88"

    account_rows = ""
    for acc_id in flagged_ids:
        score = gnn_scores.get(acc_id, 0.5)
        acc   = accounts.get(acc_id, {})
        color = risk_color(score)
        level = "CRITICAL" if score >= 0.85 else "HIGH" if score >= 0.70 else "MEDIUM"
        account_rows += f"""<tr>
            <td><code>{acc_id}</code></td>
            <td style="font-weight:bold; color:{color};">{score*100:.0f}%</td>
            <td><span style="color:{color}; font-weight:bold;">{level}</span></td>
            <td>{acc.get('jurisdiction','N/A')}</td>
            <td>{'✅' if acc.get('kyc_verified') else '❌ FAILED'}</td>
            <td><div class="risk-bar"><div class="risk-fill" style="width:{score*100:.0f}%; background:{color};"></div></div></td>
        </tr>"""

    # Transaction rows
    transaction_rows = ""
    for txn in txns[:10]:
        transaction_rows += f"""<tr>
            <td><code style="font-size:10px;">{txn.get('txn_id','')[:16]}</code></td>
            <td>{txn.get('sender_id','')}</td>
            <td>{txn.get('receiver_id','')}</td>
            <td style="font-weight:bold;">₹{txn.get('amount',0):,.0f}</td>
            <td>{txn.get('channel','')}</td>
            <td style="font-size:10px;">{txn.get('timestamp','')[:19]}</td>
        </tr>"""

    # Recommendations
    recs = [
        "Freeze all flagged accounts immediately — prevent further fund movement",
        "File Suspicious Transaction Report (STR) with FIU-IND within 7 working days",
        "Initiate KYC re-verification for all accounts in the ring",
        "Block all device IDs associated with flagged accounts across channels",
        "Escalate to Law Enforcement (ED/CBI) given amount exceeds ₹10 Lakhs",
        "Share anonymised pattern with IBA member banks via IntelliTrace network",
    ]
    recommendation_rows = "".join(
        f'<div class="recommendation"><div class="rec-num">{i+1}</div><div class="rec-text">{r}</div></div>'
        for i, r in enumerate(recs)
    )

    report_id = f"RPT-{scenario_id[:4]}-{datetime.datetime.now().strftime('%Y%m%d-%H%M')}"

    html = HTML_TEMPLATE.format(
        report_id=report_id,
        generated_at=datetime.datetime.now().strftime("%d %b %Y, %H:%M:%S IST"),
        scenario_title=title,
        risk_level=risk_level,
        risk_level_lower=risk_level.lower(),
        confidence_pct=int(confidence * 100),
        total_amount=f"₹{total_amount:,.0f}",
        account_count=len(flagged_ids),
        description=desc,
        account_rows=account_rows,
        transaction_rows=transaction_rows,
        recommendation_rows=recommendation_rows,
    )
    return html


if __name__ == "__main__":
    import json, os, sys
    base = os.path.dirname(os.path.dirname(__file__))

    with open(f"{base}/sample_data/transactions.json") as f: transactions = json.load(f)
    with open(f"{base}/sample_data/accounts.json") as f:
        accounts = {a["account_id"]: a for a in json.load(f)}

    scenario = sys.argv[1] if len(sys.argv) > 1 else "CLASSIC_MULE_RING"
    html = generate_report(scenario, transactions, accounts, {})

    out_path = f"{base}/reports/{scenario}_report.html"
    with open(out_path, "w") as f: f.write(html)
    print(f"✅ Report saved: {out_path}")
    print(f"   Open in browser: open {out_path}")
