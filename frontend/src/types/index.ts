export interface AccountScore {
  account_id:   string
  mule_score:   number
  risk_level:   "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
  risk_factors: { factor: string; score: number }[]
  action:       string
  confidence:   number
}

export interface MuleRing {
  ring_id:           string
  accounts:          string[]
  account_count:     number
  transaction_count: number
  total_amount:      number
  time_span_seconds: number
  channels_used:     string[]
  confidence:        number
  action:            string
  evidence:          string[]
  detected_at:       string
}

export interface StructuringAlert {
  alert_type:   string
  action:       string
  sender_id?:   string
  receiver_id?: string
  txn_count:    number
  total_amount: number
  evidence:     string[]
  confidence:   number
}

export interface JurisdictionAlert {
  txn_id:     string
  risk_score: number
  action:     string
  sender_jurisdiction: string
  receiver_jurisdiction: string
  evidence:   string[]
}

export interface SanctionsAlert {
  account_id:      string
  behaviour_score: number
  action:          string
  kyc_status:      string
  device_match:    boolean
  evidence:        string[]
}

export interface DetectAllResult {
  elapsed_ms:   number
  total_alerts: number
  gnn_high_risk: AccountScore[] | null
  detectors: {
    rings:        { count: number; alerts: MuleRing[] }
    structuring:  { count: number; alerts: StructuringAlert[] }
    jurisdiction: { count: number; alerts: JurisdictionAlert[] }
    sanctions:    { count: number; alerts: SanctionsAlert[] }
    device:       { count: number; alerts: unknown[] }
    nesting:      { count: number; alerts: unknown[] }
  }
}

export interface DatasetStats {
  total_accounts:     number
  total_transactions: number
  mule_accounts:      number
  mule_rate_pct:      number
  fraud_txns:         number
  fraud_amount_inr:   number
  channels:           number
  scenarios:          number
}
