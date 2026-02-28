const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function fetchAPI(path: string, options?: RequestInit) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json()
}

export const api = {
  health:       ()             => fetchAPI("/health"),
  stats:        ()             => fetchAPI("/api/stats"),
  riskMatrix:   ()             => fetchAPI("/api/risk-matrix"),
  alerts:       (limit = 50)   => fetchAPI(`/api/alerts?limit=${limit}`),

  score: (body: object) =>
    fetchAPI("/api/score", { method: "POST", body: JSON.stringify(body) }),

  detectAll: (body: object) =>
    fetchAPI("/api/detect/all", { method: "POST", body: JSON.stringify(body) }),

  detectRings: (body: object) =>
    fetchAPI("/api/detect/rings", { method: "POST", body: JSON.stringify(body) }),

  detectStructuring: (body: object) =>
    fetchAPI("/api/detect/structuring", { method: "POST", body: JSON.stringify(body) }),

  generateSTR: (body: object) =>
    fetchAPI("/api/report/str", { method: "POST", body: JSON.stringify(body) }),
}

export type RiskLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"

export function riskColor(level: RiskLevel | string) {
  switch (level) {
    case "CRITICAL": return "text-red-400 bg-red-900/20 border-red-700"
    case "HIGH":     return "text-orange-400 bg-orange-900/20 border-orange-700"
    case "MEDIUM":   return "text-yellow-400 bg-yellow-900/20 border-yellow-700"
    default:         return "text-green-400 bg-green-900/20 border-green-700"
  }
}

export function actionColor(action: string) {
  switch (action) {
    case "BLOCK":     return "bg-red-700 text-white"
    case "FLAG":      return "bg-orange-600 text-white"
    case "ESCALATE":  return "bg-purple-700 text-white"
    case "REVIEW":    return "bg-yellow-600 text-white"
    case "FILE_STR":  return "bg-teal-700 text-white"
    default:          return "bg-gray-600 text-white"
  }
}
