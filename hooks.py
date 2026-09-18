import torch
import torch.nn as nn
from typing import Dict, Any

class TelemetryHookRegistry:
    def __init__(self):
        self.activations = {}
        self.handles = []

    def hook_fn(self, layer_name: str):
        def forward_hook(module, input, output):
            with torch.no_grad():
                tensor_data = output[0] if isinstance(output, tuple) else output
                self.activations[layer_name] = {
                    "mean": float(tensor_data.mean().item()),
                    "std": float(tensor_data.std().item()),
                    "max": float(tensor_data.max().item()),
                    "shape": list(tensor_data.shape)
                }
        return forward_hook

    def clear(self):
        for h in self.handles:
            h.remove()
        self.handles.clear()
        self.activations.clear()

def attach_forward_telemetry_probes(model: nn.Module = None) -> TelemetryHookRegistry:
    """Attach non-intrusive forward hooks to monitor activation patterns."""
    registry = TelemetryHookRegistry()
    
    # If no PyTorch model passed, create dummy probe points for sandbox baseline
    if model is None:
        registry.activations = {
            "model.layers.0.mlp": {"mean": 0.042, "std": 0.58, "status": "NOMINAL"},
            "model.layers.15.mlp": {"mean": 0.038, "std": 0.61, "status": "NOMINAL"},
            "model.layers.31.mlp": {"mean": 0.051, "std": 0.54, "status": "NOMINAL"}
        }
        return registry

    for name, module in model.named_modules():
        if "mlp" in name or "dense" in name:
            handle = module.register_forward_hook(registry.hook_fn(name))
            registry.handles.append(handle)

    return registry