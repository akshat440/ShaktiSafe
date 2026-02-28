"""
IntelliTrace GNN Training Pipeline
Trains GraphSAGE on synthetic mule data.
Saves model to models/gnn_model.pt
Run: python gnn/train.py
"""

import json, os, sys, torch, torch.nn.functional as F
from torch.optim import Adam
from sklearn.metrics import roc_auc_score, classification_report
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from gnn.model import MuleDetectorGNN, create_graph_data

class FocalLoss(torch.nn.Module):
    def __init__(self, alpha=0.75, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    def forward(self, pred, target):
        bce = F.binary_cross_entropy(pred, target, reduction='none')
        p_t = pred * target + (1 - pred) * (1 - target)
        alpha_t = self.alpha * target + (1 - self.alpha) * (1 - target)
        return (alpha_t * (1 - p_t) ** self.gamma * bce).mean()

def train():
    print("=" * 55)
    print("IntelliTrace — GNN Training")
    print("=" * 55)

    # Load data
    base = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(base, 'sample_data')
    
    if not os.path.exists(f"{data_dir}/accounts.json"):
        print("Generating data first...")
        import subprocess
        subprocess.run([sys.executable, os.path.join(base, 'data', 'generator.py')])

    with open(f"{data_dir}/accounts.json") as f:
        accounts = json.load(f)
    with open(f"{data_dir}/transactions.json") as f:
        transactions = json.load(f)

    print(f"\nAccounts: {len(accounts)} | Transactions: {len(transactions)}")
    print(f"Mule accounts: {sum(1 for a in accounts if a.get('is_mule', False))}")

    # Build graph
    data = create_graph_data(accounts, transactions)
    print(f"Graph: {data.num_nodes} nodes, {data.edge_index.shape[1]} edges")

    # Stratified split
    labels = data.y.numpy()
    indices = list(range(data.num_nodes))
    train_idx, test_idx = train_test_split(indices, test_size=0.2, stratify=labels, random_state=42)
    train_idx, val_idx = train_test_split(train_idx, test_size=0.2, stratify=labels[train_idx], random_state=42)

    train_mask = torch.zeros(data.num_nodes, dtype=torch.bool)
    val_mask   = torch.zeros(data.num_nodes, dtype=torch.bool)
    test_mask  = torch.zeros(data.num_nodes, dtype=torch.bool)
    train_mask[train_idx] = True
    val_mask[val_idx]     = True
    test_mask[test_idx]   = True

    # Model + optimizer
    model     = MuleDetectorGNN(in_channels=10, hidden_channels=128, out_channels=64)
    optimizer = Adam(model.parameters(), lr=0.005, weight_decay=5e-4)
    loss_fn   = FocalLoss(alpha=0.75, gamma=2.0)

    print(f"\nParameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"\n{'Epoch':>6} {'Loss':>10} {'ValAUC':>8} {'ValF1':>7}")
    print("-" * 40)

    best_auc, best_state, patience = 0, None, 0

    for epoch in range(1, 151):
        model.train()
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = loss_fn(out['mule_score'][train_mask], data.y[train_mask])
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        if epoch % 15 == 0 or epoch == 1:
            model.eval()
            with torch.no_grad():
                out = model(data.x, data.edge_index)
                scores = out['mule_score'][val_mask].numpy()
                labels_val = data.y[val_mask].numpy()
                preds = (scores > 0.5).astype(int)
                auc = roc_auc_score(labels_val, scores) if labels_val.sum() > 0 else 0.5
                from sklearn.metrics import f1_score
                f1 = f1_score(labels_val, preds, zero_division=0)
            print(f"{epoch:>6} {loss.item():>10.4f} {auc:>8.4f} {f1:>7.4f}")
            if auc > best_auc:
                best_auc = auc
                best_state = {k: v.clone() for k, v in model.state_dict().items()}
                patience = 0
            else:
                patience += 1
            if patience >= 5:
                print(f"\nEarly stop at epoch {epoch}")
                break

    # Final test evaluation
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        out = model(data.x, data.edge_index)
        scores = out['mule_score'][test_mask].numpy()
        true   = data.y[test_mask].numpy()
        preds  = (scores > 0.5).astype(int)

    print(f"\n{'=' * 55}")
    print("FINAL TEST RESULTS")
    print(f"{'=' * 55}")
    auc = roc_auc_score(true, scores) if true.sum() > 0 else 0.5
    print(f"AUC: {auc:.4f}")
    print(classification_report(true, preds, target_names=['Legitimate', 'Mule']))

    # Save model
    model_dir = os.path.join(base, 'models')
    os.makedirs(model_dir, exist_ok=True)
    save_path = os.path.join(model_dir, 'gnn_model.pt')
    torch.save({
        'model_state_dict': best_state,
        'model_config': {'in_channels': 10, 'hidden_channels': 128, 'out_channels': 64, 'dropout': 0.3},
        'metrics': {'auc': auc},
        'account_ids': data.account_ids,
    }, save_path)
    print(f"\n✅ Model saved → {save_path}")
    return model, data

if __name__ == "__main__":
    train()
