import torch
import torch.nn as nn
from hooks import NeuroFenceTelemetryEngine

# Simulated Lightweight LLM Backbone (1B Architecture structure representation)
class LightweightSandboxedLLM(nn.Module):
    def __init__(self, hidden_dim=256, num_layers=4):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.ModuleDict({
                "self_attn_o_proj": nn.Linear(hidden_dim, hidden_dim),
                "mlp_down_proj": nn.Linear(hidden_dim, hidden_dim)
            }) for _ in range(num_layers)
        ])
        
        # Ek hidden backdoor trojan weight inject karte hain layer 3 me (for testing detection)
        with torch.no_grad():
            self.layers[3]["mlp_down_proj"].weight.mul_(3.5) # Anomaly spike trigger

    def forward(self, x):
        for layer in self.layers:
            x = layer["self_attn_o_proj"](x) + x
            x = layer["mlp_down_proj"](x) + x
        return x

def run_neurofence_scan():
    print("=" * 60)
    print("      NEUROFENCE: LOCAL SANDBOX & MODEL INSPECTION")
    print("=" * 60)

    # 1. Initialize Engine & Model
    print("\n[Step 1/3] Loading sandboxed model representation...")
    model = LightweightSandboxedLLM(hidden_dim=256, num_layers=4)
    model.eval()

    # 2. Attach Activation Probes
    print("[Step 2/3] Attaching forward hooks to MLP & Attention layers...")
    telemetry = NeuroFenceTelemetryEngine(anomaly_std_threshold=1.10)
    probes_count = telemetry.attach_hooks(model, target_layer_names=["mlp_down_proj", "self_attn_o_proj"])
    print(f"-> Total Probes Active: {probes_count}")

    # 3. Test Pass 1: Benign / Clean Input
    print("\n[Step 3/3] Feeding clean validation prompt tensor...")
    clean_tensor = torch.randn(1, 32, 256)
    with torch.no_grad():
        _ = model(clean_tensor)

    results = telemetry.get_summary()
    print("\n--- Telemetry Inspection Report ---")
    print(f"{'Layer Name':<35} | {'Mean':<8} | {'StdDev':<8} | {'Status'}")
    print("-" * 65)

    anomalies_detected = 0
    for layer, metric in results.items():
        status_display = "⚠️ " + metric['status'] if metric['is_anomaly'] else "✅ " + metric['status']
        print(f"{layer:<35} | {metric['mean']:<8.4f} | {metric['std']:<8.4f} | {status_display}")
        if metric['is_anomaly']:
            anomalies_detected += 1

    print("-" * 65)
    if anomalies_detected > 0:
        print(f"\n🚨 ALERT: NeuroFence identified {anomalies_detected} anomalous layer(s) exhibiting potential weight poisoning / trojan signatures!")
    else:
        print("\n✅ PASSED: All layers within nominal standard distribution bounds.")

    telemetry.clear()

if __name__ == "__main__":
    run_neurofence_scan()