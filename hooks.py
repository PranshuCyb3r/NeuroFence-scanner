import torch
import numpy as np

class NeuroFenceTelemetryEngine:
    """
    PyTorch forward hooks engine to inspect intermediate activations
    safely without CUDA/CPU memory leakage.
    """
    def __init__(self, anomaly_std_threshold: float = 1.15):
        self.activations = {}
        self.hook_handles = []
        self.anomaly_std_threshold = anomaly_std_threshold

    def _create_hook(self, layer_name: str):
        def hook(module, input_tensor, output_tensor):
            # Output tuple ho ya standalone tensor, safely extract karein
            actual_tensor = output_tensor[0] if isinstance(output_tensor, tuple) else output_tensor
            
            # Detach and clone to prevent memory retention in backward graph
            t = actual_tensor.detach().cpu().float()
            
            mean_val = float(t.mean())
            std_val = float(t.std())
            sparsity = float((t == 0).float().mean().item() * 100)
            
            # Anomaly trigger logic: high variance / standard deviation spike
            is_anomaly = std_val >= self.anomaly_std_threshold
            
            self.activations[layer_name] = {
                "shape": list(actual_tensor.shape),
                "mean": round(mean_val, 4),
                "std": round(std_val, 4),
                "sparsity_pct": round(sparsity, 2),
                "is_anomaly": is_anomaly,
                "status": "CRITICAL ANOMALY" if is_anomaly else "NORMAL"
            }
        return hook

    def attach_hooks(self, model, target_layer_names=None):
        """
        Specified layers par forward hooks attach karta hai.
        """
        self.clear()
        
        if target_layer_names is None:
            # Common target projections in Llama/Modern Transformer architectures
            target_layer_names = [
                "mlp.down_proj",
                "self_attn.o_proj",
                "mlp.up_proj"
            ]

        attached_count = 0
        for name, module in model.named_modules():
            # Match any of target layer patterns
            if any(target in name for target in target_layer_names):
                handle = module.register_forward_hook(self._create_hook(name))
                self.hook_handles.append(handle)
                attached_count += 1
                
        print(f"[NeuroFence Hooks] Successfully attached {attached_count} telemetry probes.")
        return attached_count

    def get_summary(self):
        """Latest layer telemetry metrics return karta hai."""
        return self.activations

    def clear(self):
        """Hooks detach karta hai memory cleanup ke liye."""
        for handle in self.hook_handles:
            handle.remove()
        self.hook_handles = []
        self.activations.clear()


# --- Quick Self-Test Simulation ---
if __name__ == "__main__":
    print("\n--- Testing NeuroFence Hook Engine (Self-Verification) ---")
    
    # Ek simple dummy module banate hain hook test verify karne ke liye
    import torch.nn as nn
    
    class MockTransformerLayer(nn.Module):
        def __init__(self):
            super().__init__()
            self.mlp_down_proj = nn.Linear(64, 64)
            
        def forward(self, x):
            return self.mlp_down_proj(x)

    mock_model = MockTransformerLayer()
    engine = NeuroFenceTelemetryEngine(anomaly_std_threshold=1.1)
    
    # Hook attach karein
    engine.attach_hooks(mock_model, target_layer_names=["mlp_down_proj"])
    
    # Forward pass chalayein (dummy input)
    dummy_input = torch.randn(1, 16, 64)
    with torch.no_grad():
        _ = mock_model(dummy_input)
        
    summary = engine.get_summary()
    for layer, stats in summary.items():
        print(f"Layer: {layer} -> Shape: {stats['shape']}, Mean: {stats['mean']}, Std: {stats['std']}, Status: {stats['status']}")
    
    engine.clear()
    print("[NeuroFence Engine] Hook Test Completed Successfully.")