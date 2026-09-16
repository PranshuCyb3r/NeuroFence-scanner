import torch
import torch.nn as nn
from typing import Dict, List, Any

class ActivationProbeHook:
    """
    Hook to capture forward activation tensors from model layers
    for backdoor & anomaly telemetry inspection.
    """
    def __init__(self, layer_name: str):
        self.layer_name = layer_name
        self.activation = None

    def __call__(self, module, input_tensor, output_tensor):
        if isinstance(output_tensor, tuple):
            self.activation = output_tensor[0].detach()
        else:
            self.activation = output_tensor.detach()

def attach_forward_telemetry_probes(model: nn.Module, target_layers: List[str] = None) -> Dict[str, ActivationProbeHook]:
    """
    Attaches forward hooks to designated transformer/linear layers in the model.
    Returns a dictionary of registered probe handles.
    """
    probes = {}
    for name, module in model.named_modules():
        if target_layers:
            if any(t in name for t in target_layers):
                hook = ActivationProbeHook(name)
                module.register_forward_hook(hook)
                probes[name] = hook
        else:
            # By default attach to linear projection / MLP layers
            if isinstance(module, nn.Linear):
                hook = ActivationProbeHook(name)
                module.register_forward_hook(hook)
                probes[name] = hook

    print(f"[NeuroFence Hooks] Successfully attached {len(probes)} telemetry probes.")
    return probes

def calculate_layer_telemetry(activations: torch.Tensor) -> Dict[str, float]:
    """
    Computes statistical telemetry metrics (mean, std, peak, sparsity)
    from captured layer activations.
    """
    if activations is None:
        return {"mean": 0.0, "std": 0.0, "peak": 0.0, "status": "QUIESCENT"}

    mean_val = float(activations.mean().item())
    std_val = float(activations.std().item())
    peak_val = float(activations.max().item())

    # If peak deviation is abnormal
    status = "ALERT_ANOMALY" if peak_val > (mean_val + 4 * std_val) else "NORMAL"

    return {
        "mean": round(mean_val, 4),
        "std": round(std_val, 4),
        "peak": round(peak_val, 4),
        "status": status
    }

# --- Quick Test ---
if __name__ == "__main__":
    print("--- Testing NeuroFence Hook Engine (Self-Verification) ---")
    toy_net = nn.Sequential(
        nn.Linear(16, 32),
        nn.ReLU(),
        nn.Linear(32, 16)
    )
    registered_probes = attach_forward_telemetry_probes(toy_net)
    dummy_input = torch.randn(2, 16)
    _ = toy_net(dummy_input)

    for name, p in list(registered_probes.items())[:2]:
        metrics = calculate_layer_telemetry(p.activation)
        print(f"  Layer [{name}] -> Mean: {metrics['mean']}, Std: {metrics['std']}, Status: {metrics['status']}")

    print("[NeuroFence Engine] Hook Test Completed Successfully.")