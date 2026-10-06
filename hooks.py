import torch
import torch.nn as nn
import numpy as np


class ActivationProbeTracker:
    def __init__(self, layer_id: int, layer_name: str):
        self.layer_id = layer_id
        self.name = layer_name
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.M4 = 0.0
        self.max_act = -float("inf")

    def update(self, tensor: torch.Tensor):
        # Flatten token activations
        data = tensor.detach().float().cpu().flatten()
        data = data[data != 0]
        if len(data) == 0:
            return

        # CPU performance cap for Ryzen 5 (constant RAM)
        if len(data) > 2048:
            data = data[:2048]

        vals = data.numpy()
        for x in vals:
            self.count += 1
            delta = x - self.mean
            self.mean += delta / self.count
            delta2 = x - self.mean
            self.M2 += delta * delta2
            self.M4 += (delta * delta2) ** 2
            if x > self.max_act:
                self.max_act = float(x)

    def get_stats(self) -> dict:
        if self.count < 10:
            return {
                "layer": self.layer_id,
                "name": self.name,
                "mean": 0.0,
                "kurtosis": 3.0,
                "outlier": False
            }
        var = self.M2 / self.count
        kurt = (self.M4 / self.count) / (var ** 2 + 1e-9)
        kurt = round(float(np.clip(kurt, 1.0, 15.0)), 2)

        return {
            "layer": self.layer_id,
            "name": self.name,
            "mean": round(float(self.mean), 4),
            "kurtosis": kurt,
            "outlier": (kurt >= 4.5)
        }


def attach_activation_hooks(model: nn.Module):
    """Attaches real PyTorch forward hooks to linear projection layers."""
    trackers = {}
    handles = []
    layer_idx = 0

    for name, module in model.named_modules():
        if any(target in name.lower() for target in ["mlp.down_proj", "mlp.c_proj", "dense_4h_to_h", "classifier", "encoder.layer"]):
            trk = ActivationProbeTracker(layer_idx, name)
            trackers[layer_idx] = trk

            def hook_factory(t):
                def hook_fn(mod, inp, out):
                    if isinstance(out, tuple):
                        out = out[0]
                    # Discard token 0 (BOS natural sink)
                    if len(out.shape) == 3 and out.shape[1] > 1:
                        out = out[:, 1:, :]
                    t.update(out)
                return hook_fn

            h = module.register_forward_hook(hook_factory(trk))
            handles.append(h)
            layer_idx += 1

    return trackers, handles