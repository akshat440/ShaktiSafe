"use client"

interface StatCardProps {
  label:    string
  value:    string | number
  sub?:     string
  color?:   "crimson" | "gold" | "teal" | "blue"
  large?:   boolean
}

const COLORS = {
  crimson: "border-red-800  text-red-400",
  gold:    "border-yellow-700 text-yellow-400",
  teal:    "border-teal-700 text-teal-400",
  blue:    "border-blue-700 text-blue-400",
}

export default function StatCard({ label, value, sub, color = "blue", large }: StatCardProps) {
  return (
    <div className={`bg-white/5 border rounded-lg p-4 ${COLORS[color]}`}>
      <div className="text-xs text-gray-400 uppercase tracking-widest mb-1">{label}</div>
      <div className={`font-bold ${large ? "text-3xl" : "text-2xl"} ${COLORS[color].split(" ")[1]}`}>
        {value}
      </div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
    </div>
  )
}
