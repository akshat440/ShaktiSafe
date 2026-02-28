"use client"

interface BadgeProps {
  label:  string
  variant?: "critical" | "high" | "block" | "flag" | "review" | "str" | "monitor" | "escalate"
}

const styles: Record<string, string> = {
  critical: "bg-red-900/60 text-red-300 border border-red-700",
  high:     "bg-orange-900/60 text-orange-300 border border-orange-700",
  block:    "bg-red-800 text-white",
  flag:     "bg-orange-700 text-white",
  review:   "bg-yellow-700 text-white",
  str:      "bg-teal-800 text-white",
  monitor:  "bg-gray-700 text-white",
  escalate: "bg-purple-800 text-white",
}

export default function Badge({ label, variant = "monitor" }: BadgeProps) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${styles[variant]}`}>
      {label}
    </span>
  )
}
