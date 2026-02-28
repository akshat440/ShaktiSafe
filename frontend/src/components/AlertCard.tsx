"use client"
import { ShieldAlert, AlertTriangle, Eye, Ban } from "lucide-react"
import Badge from "./Badge"

interface AlertCardProps {
  type:        string
  action:      string
  confidence?: number
  amount?:     number
  accounts?:   number | string[]
  evidence?:   string[]
  extra?:      Record<string, unknown>
}

const ACTION_ICON: Record<string, React.FC<{ size: number; className: string }>> = {
  BLOCK:    Ban,
  FLAG:     AlertTriangle,
  ESCALATE: ShieldAlert,
  REVIEW:   Eye,
}

const ACTION_VARIANT: Record<string, "critical" | "high" | "block" | "flag" | "review" | "str" | "escalate"> = {
  BLOCK:    "block",
  FLAG:     "flag",
  ESCALATE: "escalate",
  REVIEW:   "review",
  FILE_STR: "str",
  FILE_CTR: "str",
}

const TYPE_COLOR: Record<string, string> = {
  MULE_RING:           "border-l-red-600",
  STRUCTURING:         "border-l-orange-500",
  SMURFING:            "border-l-orange-500",
  JURISDICTION_RISK:   "border-l-yellow-500",
  BEHAVIOURAL_SANCTIONS:"border-l-purple-500",
  DEVICE_FINGERPRINT:  "border-l-blue-500",
  NESTING_DEPTH:       "border-l-teal-500",
}

export default function AlertCard({ type, action, confidence, amount, accounts, evidence, extra }: AlertCardProps) {
  const Icon = ACTION_ICON[action] || Eye
  const borderColor = TYPE_COLOR[type] || "border-l-gray-500"
  const accCount = Array.isArray(accounts) ? accounts.length : accounts

  return (
    <div className={`bg-white/5 border-l-4 ${borderColor} rounded-r-lg p-4 mb-3`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon size={16} className="text-gray-400 shrink-0 mt-0.5" />
          <span className="text-sm font-semibold text-white">{type.replace(/_/g, " ")}</span>
        </div>
        <div className="flex gap-1.5 shrink-0">
          <Badge label={action} variant={ACTION_VARIANT[action] || "monitor"} />
          {confidence !== undefined && (
            <span className="text-xs text-gray-400 self-center">{(confidence * 100).toFixed(0)}%</span>
          )}
        </div>
      </div>

      <div className="flex gap-4 text-xs text-gray-400 mb-2">
        {amount   && <span>INR {amount.toLocaleString("en-IN")}</span>}
        {accCount && <span>{accCount} account{Number(accCount) > 1 ? "s" : ""}</span>}
      </div>

      {evidence && evidence.length > 0 && (
        <ul className="space-y-1">
          {evidence.slice(0, 3).map((e, i) => (
            <li key={i} className="text-xs text-gray-300 pl-2 border-l border-gray-600">{e}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
