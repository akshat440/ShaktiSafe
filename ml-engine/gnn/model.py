"""
IntelliTrace GNN Model — GraphSAGE for Mule Account Detection
Uses inductive learning: can score accounts never seen during training.
Node features: 10 behavioral signals per account
Edge features: 5 signals per transaction
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, BatchNorm, to_hetero
from torch_geometric.data import Data, HeteroData
from torch_geometric.utils import add_self_loops, degree
from typing import Optional


class MuleDetectorGNN(nn.Module):
    """
    3-layer GraphSAGE with residual connections.
    Input:  Node feature matrix X (N × 10)
    Output: Mule probability per node (N × 1)

    Architecture:
      Layer 1: SAGEConv(10 → 64) + BatchNorm + ReLU + Dropout
      Layer 2: SAGEConv(64 → 128) + BatchNorm + ReLU + Dropout
      Layer 3: SAGEConv(128 → 64) + BatchNorm + ReLU
      Head:    Linear(64 → 32) → ReLU → Linear(32 → 1) → Sigmoid
    """

    def __init__(
        self,
        in_channels: int = 10,
        hidden_channels: int = 128,
        out_channels: int = 64,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.dropout = dropout

        # Graph convolution layers
        self.conv1 = SAGEConv(in_channels, hidden_channels, aggr="mean")
        self.conv2 = SAGEConv(hidden_channels, hidden_channels * 2, aggr="mean")
        self.conv3 = SAGEConv(hidden_channels * 2, out_channels, aggr="mean")

        # Batch normalization
        self.bn1 = BatchNorm(hidden_channels)
        self.bn2 = BatchNorm(hidden_channels * 2)
        self.bn3 = BatchNorm(out_channels)

        # Residual projection (to match dimensions)
        self.res_proj1 = nn.Linear(in_channels, hidden_channels)
        self.res_proj2 = nn.Linear(hidden_channels, hidden_channels * 2)
        self.res_proj3 = nn.Linear(hidden_channels * 2, out_channels)

        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(out_channels, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

        # Risk explanation head (for interpretability)
        self.explainer = nn.Sequential(
            nn.Linear(out_channels, 16),
            nn.ReLU(),
            nn.Linear(16, 5),  # 5 risk factors
        )

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> dict:
        # Layer 1
        h1 = self.conv1(x, edge_index)
        h1 = self.bn1(h1)
        h1 = F.relu(h1) + self.res_proj1(x)
        h1 = F.dropout(h1, p=self.dropout, training=self.training)

        # Layer 2
        h2 = self.conv2(h1, edge_index)
        h2 = self.bn2(h2)
        h2 = F.relu(h2) + self.res_proj2(h1)
        h2 = F.dropout(h2, p=self.dropout, training=self.training)

        # Layer 3
        h3 = self.conv3(h2, edge_index)
        h3 = self.bn3(h3)
        h3 = F.relu(h3) + self.res_proj3(h2)

        # Output
        mule_score = torch.sigmoid(self.classifier(h3))
        risk_factors = torch.softmax(self.explainer(h3), dim=-1)

        return {
            "mule_score": mule_score.squeeze(-1),          # [N] — probability 0-1
            "embeddings": h3,                               # [N × 64] — for clustering
            "risk_factors": risk_factors,                   # [N × 5] — explanation
        }

    def get_node_risk_explanation(self, risk_factors: torch.Tensor) -> list:
        """Map 5 risk factor scores to human-readable labels."""
        labels = [
            "velocity_anomaly",
            "cross_channel_movement",
            "jurisdiction_risk",
            "structuring_pattern",
            "network_centrality"
        ]
        result = []
        for i, score in enumerate(risk_factors):
            result.append({"factor": labels[i], "score": float(score)})
        return sorted(result, key=lambda x: x["score"], reverse=True)


class MuleRingClassifier(nn.Module):
    """
    Graph-level classifier: given a subgraph (suspected ring),
    outputs probability it's an active mule ring.
    Uses global mean + max pooling for graph embedding.
    """

    def __init__(self, node_embed_dim: int = 64):
        super().__init__()
        self.ring_classifier = nn.Sequential(
            nn.Linear(node_embed_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, node_embeddings: torch.Tensor) -> torch.Tensor:
        """
        Args:
            node_embeddings: [N × 64] embeddings of accounts in suspected ring
        Returns:
            ring_score: probability this is a mule ring [0-1]
        """
        mean_pool = node_embeddings.mean(dim=0)    # [64]
        max_pool = node_embeddings.max(dim=0)[0]   # [64]
        graph_embed = torch.cat([mean_pool, max_pool], dim=-1)  # [128]
        return torch.sigmoid(self.ring_classifier(graph_embed))


def build_node_features(accounts: list, transactions: list) -> tuple:
    """
    Build node feature matrix from accounts and their transaction history.
    
    Features per account (10 total):
      0: normalized account age (days / 3650)
      1: kyc_verified (0/1)
      2: txn_count_normalized (log scale)
      3: avg_amount_normalized
      4: channel_diversity (unique channels / 6)
      5: cross_jurisdiction_ratio
      6: velocity_score (txns per hour, last 24h)
      7: incoming_outgoing_ratio
      8: round_number_ratio (txns with round amounts)
      9: new_counterparty_ratio
    """
    from collections import defaultdict
    import math

    # Index transactions by sender/receiver
    sent = defaultdict(list)
    received = defaultdict(list)
    for txn in transactions:
        sent[txn["sender_id"]].append(txn)
        received[txn["receiver_id"]].append(txn)

    account_ids = [a["account_id"] for a in accounts]
    id_to_idx = {aid: i for i, aid in enumerate(account_ids)}

    features = []
    for acc in accounts:
        aid = acc["account_id"]
        s_txns = sent[aid]
        r_txns = received[aid]
        all_txns = s_txns + r_txns

        n_sent = len(s_txns)
        n_recv = len(r_txns)
        n_total = max(n_sent + n_recv, 1)

        amounts = [t["amount"] for t in all_txns]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0

        channels = set(t["channel"] for t in all_txns)
        channel_div = len(channels) / 6.0

        cross_j = sum(1 for t in s_txns
                      if t.get("sender_jurisdiction") != t.get("receiver_jurisdiction"))
        cross_j_ratio = cross_j / max(n_sent, 1)

        round_txns = sum(1 for a in amounts if a % 1000 == 0)
        round_ratio = round_txns / max(n_total, 1)

        counterparties = set(t["receiver_id"] for t in s_txns) | set(t["sender_id"] for t in r_txns)
        new_cp_ratio = min(len(counterparties) / max(n_total, 1), 1.0)

        io_ratio = n_recv / max(n_sent, 1)

        feat = [
            min(acc.get("account_age_days", 365) / 3650.0, 1.0),
            float(acc.get("kyc_verified", True)),
            math.log1p(n_total) / 10.0,
            math.log1p(avg_amount) / 15.0,
            channel_div,
            cross_j_ratio,
            min(n_total / 100.0, 1.0),  # velocity proxy
            min(io_ratio / 10.0, 1.0),
            round_ratio,
            new_cp_ratio,
        ]
        features.append(feat)

    return torch.tensor(features, dtype=torch.float32), id_to_idx


def build_edge_index(transactions: list, id_to_idx: dict) -> tuple:
    """Build edge_index tensor from transactions."""
    src, dst = [], []
    for txn in transactions:
        s = id_to_idx.get(txn["sender_id"])
        r = id_to_idx.get(txn["receiver_id"])
        if s is not None and r is not None:
            src.append(s)
            dst.append(r)

    edge_index = torch.tensor([src, dst], dtype=torch.long)
    return edge_index


def build_labels(accounts: list) -> torch.Tensor:
    """Build binary label tensor: 1=mule, 0=legitimate."""
    return torch.tensor(
        [1.0 if a.get("is_mule", False) else 0.0 for a in accounts],
        dtype=torch.float32
    )


def create_graph_data(accounts: list, transactions: list) -> Data:
    """Create complete PyG Data object."""
    x, id_to_idx = build_node_features(accounts, transactions)
    edge_index = build_edge_index(transactions, id_to_idx)
    y = build_labels(accounts)

    data = Data(x=x, edge_index=edge_index, y=y)
    data.account_ids = [a["account_id"] for a in accounts]
    data.num_nodes = len(accounts)
    return data


if __name__ == "__main__":
    # Quick smoke test
    print("Testing MuleDetectorGNN...")
    model = MuleDetectorGNN()
    x = torch.randn(100, 10)
    edge_index = torch.randint(0, 100, (2, 300))
    out = model(x, edge_index)
    print(f"  mule_score shape:   {out['mule_score'].shape}")
    print(f"  embeddings shape:   {out['embeddings'].shape}")
    print(f"  risk_factors shape: {out['risk_factors'].shape}")
    print(f"  Sample mule score:  {out['mule_score'][:5]}")
    print("✅ Model OK")

    ring_clf = MuleRingClassifier()
    ring_score = ring_clf(out["embeddings"][:6])
    print(f"  Ring score for 6-node subgraph: {ring_score.item():.4f}")
    print("✅ Ring Classifier OK")
