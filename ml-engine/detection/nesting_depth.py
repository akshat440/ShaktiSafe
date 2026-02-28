"""
ShaktiSafe — Nesting Depth Scorer
Multi-hop shell chain detection.
Flags chains with ≥3 intermediate hops.
"""

from collections import defaultdict, deque
from typing import List, Dict
from datetime import datetime


MIN_CHAIN_DEPTH = 3


class NestingDepthScorer:
    """
    Detects layering / shell chains using BFS on transaction graph.
    A chain node: single_in + single_out = layering node.
    """

    def __init__(self, min_depth: int = MIN_CHAIN_DEPTH):
        self.min_depth = min_depth

    def detect(self, transactions: List[Dict]) -> List[Dict]:
        """Return nesting alerts for chains deeper than min_depth."""
        # Build adjacency
        out_edges = defaultdict(list)
        in_edges  = defaultdict(list)
        for t in transactions:
            out_edges[t["sender_id"]].append(t)
            in_edges[t["receiver_id"]].append(t)

        # Find sources: accounts with inflow but also outflow (not pure endpoints)
        all_nodes = set(out_edges.keys()) | set(in_edges.keys())

        # BFS from each potential source to find chains
        alerts    = []
        visited   = set()
        chain_id  = 0

        for source in all_nodes:
            if source in visited:
                continue
            # Only start from nodes with no inflow (entry points)
            if in_edges[source]:
                continue

            chains = self._bfs_chains(source, out_edges, in_edges)
            for chain in chains:
                if len(chain) >= self.min_depth:
                    chain_txns = self._chain_transactions(chain, transactions)
                    amounts    = [t["amount"] for t in chain_txns]
                    cut_ratios = []
                    for i in range(len(amounts)-1):
                        if amounts[i] > 0:
                            cut_ratios.append(1 - amounts[i+1]/amounts[i])

                    for node in chain:
                        visited.add(node)

                    chain_id += 1
                    alerts.append({
                        "alert_type":   "NESTING_DEPTH",
                        "action":       "FLAG",
                        "chain_id":     f"CHAIN-{chain_id:04d}",
                        "depth":        len(chain),
                        "chain_nodes":  chain,
                        "txn_ids":      [t["txn_id"] for t in chain_txns],
                        "entry_amount": amounts[0] if amounts else 0,
                        "exit_amount":  amounts[-1] if amounts else 0,
                        "avg_cut_ratio": round(sum(cut_ratios)/len(cut_ratios), 3) if cut_ratios else 0,
                        "channels":     list(set(t.get("channel","") for t in chain_txns)),
                        "evidence":     [
                            f"{len(chain)}-hop shell chain detected",
                            f"Average cut per hop: {100*sum(cut_ratios)/max(len(cut_ratios),1):.1f}%",
                            f"Entry INR {amounts[0]:,.0f} → Exit INR {amounts[-1]:,.0f}",
                        ],
                        "confidence":   min(1.0, len(chain) / 8),
                        "detected_at":  datetime.now().isoformat(),
                    })

        return alerts

    def _bfs_chains(self, source: str, out_edges, in_edges) -> List[List[str]]:
        chains = []
        queue  = deque([[source]])
        while queue:
            path = queue.popleft()
            last = path[-1]
            nexts = out_edges.get(last, [])
            if not nexts:
                if len(path) >= self.min_depth:
                    chains.append(path)
            else:
                for txn in nexts[:3]:  # limit branching
                    nxt = txn["receiver_id"]
                    if nxt not in path:
                        queue.append(path + [nxt])
        return chains

    def _chain_transactions(self, chain: List[str], transactions: List[Dict]) -> List[Dict]:
        result = []
        for i in range(len(chain)-1):
            for t in transactions:
                if t["sender_id"] == chain[i] and t["receiver_id"] == chain[i+1]:
                    result.append(t)
                    break
        return result
