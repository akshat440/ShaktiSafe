"use client"

import { useEffect, useRef, useState } from "react"
import { Wifi, WifiOff } from "lucide-react"

const WS_URL = typeof window !== "undefined"
  ? (process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/live")
  : ""

interface LiveEvent {
  id:   number
  ts:   string
  data: Record<string, unknown>
}

let _id = 0

export default function LiveAlertTicker() {
  const [events,    setEvents]    = useState<LiveEvent[]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    if (!WS_URL) return

    const connect = () => {
      const ws = new WebSocket(WS_URL)
      wsRef.current = ws

      ws.onopen  = () => setConnected(true)
      ws.onclose = () => {
        setConnected(false)
        setTimeout(connect, 3000)
      }
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data)
          setEvents((prev) => [
            { id: ++_id, ts: new Date().toLocaleTimeString(), data },
            ...prev.slice(0, 19),
          ])
        } catch {}
      }
    }

    connect()
    return () => { wsRef.current?.close() }
  }, [])

  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        {connected
          ? <Wifi size={14} className="text-green-400" />
          : <WifiOff size={14} className="text-red-400" />
        }
        <span className="text-xs font-semibold uppercase tracking-widest text-gray-300">
          Live Feed
        </span>
        <span className={`text-[10px] px-1.5 py-0.5 rounded ${connected ? "bg-green-900/50 text-green-400" : "bg-red-900/50 text-red-400"}`}>
          {connected ? "LIVE" : "DISCONNECTED"}
        </span>
      </div>
      <div className="space-y-1 max-h-48 overflow-y-auto">
        {events.length === 0 && (
          <div className="text-xs text-gray-600 italic">Waiting for live events…</div>
        )}
        {events.map((ev) => (
          <div key={ev.id} className="text-xs flex gap-2 text-gray-300 border-b border-white/5 pb-1">
            <span className="text-gray-600 shrink-0">{ev.ts}</span>
            <span className="truncate">{JSON.stringify(ev.data)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
