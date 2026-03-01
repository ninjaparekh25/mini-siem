"""
Trainer module for AI anomaly detection.

Current: sklearn IsolationForest (lightweight, CPU)
Placeholder: PyTorch Autoencoder with AMD ROCm support
"""

import numpy as np
from ai.model import get_model

def train_on_batch(samples: list[list[float]]):
    """Feed new samples to the model."""
    model = get_model()
    for s in samples:
        model.add_sample(*s)
    return {"trained": model.trained, "samples": len(model.baseline_data)}


# ─────────────────────────────────────────────────────────────
# ROCm / PyTorch Placeholder (AMD GPU Ready)
# ─────────────────────────────────────────────────────────────
PYTORCH_ENABLED = False  # Flip to True when ROCm is available

def get_pytorch_device():
    """Return best available device: ROCm GPU → CPU"""
    if not PYTORCH_ENABLED:
        return None
    try:
        import torch
        if torch.cuda.is_available():  # ROCm uses CUDA API
            device = torch.device("cuda")
            print(f"🔥 AMD ROCm GPU detected: {torch.cuda.get_device_name(0)}")
            return device
        return torch.device("cpu")
    except ImportError:
        return None


class AutoencoderPlaceholder:
    """
    Placeholder for a PyTorch-based Autoencoder anomaly detector.
    Designed for AMD ROCm / HIP acceleration.

    Architecture: 4 → 8 → 2 → 8 → 4
    Training: minimize reconstruction error
    Anomaly: high reconstruction error = anomaly
    """

    def __init__(self):
        self.device = get_pytorch_device()
        self.model = None

    def build(self):
        if not PYTORCH_ENABLED:
            print("⚠️  PyTorch/ROCm not enabled. Using sklearn IsolationForest instead.")
            return

        import torch
        import torch.nn as nn

        class Autoencoder(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 2))
                self.decoder = nn.Sequential(nn.Linear(2, 8), nn.ReLU(), nn.Linear(8, 4))

            def forward(self, x):
                return self.decoder(self.encoder(x))

        self.model = Autoencoder().to(self.device)
        print(f"✅ Autoencoder built on device: {self.device}")

    def predict_anomaly(self, sample: list) -> float:
        """Returns reconstruction error as anomaly score."""
        if not PYTORCH_ENABLED or self.model is None:
            return 0.0

        import torch
        x = torch.tensor([sample], dtype=torch.float32).to(self.device)
        with torch.no_grad():
            recon = self.model(x)
            error = torch.mean((recon - x) ** 2).item()
        return error
