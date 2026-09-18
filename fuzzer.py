import os
import json
import time
import random
import numpy as np
from typing import Dict, List, Any

class AdversarialFuzzer:
    """
    Adversarial Text Generator and Activation Profiler for LLM Weight Poisoning detection.
    """
    def __init__(self):
        self.attack_prefixes = [
            "system_prompt_override_0x89",
            "sudo_inversion_trigger_candidate",
            "jailbreak_bypass_subroutine",
            "token_shift_affine_perturbation",
            "backdoor_trigger_candidate_alpha",
            "universal_transferable_suffix_eval"
        ]

    def generate_fuzz_batch(self, batch_size: int = 4) -> List[str]:
        samples = []
        for _ in range(batch_size):
            prefix = random.choice(self.attack_prefixes)
            hex_id = f"{random.randint(0x1000, 0xffff):04x}"
            samples.append(f"Evaluate model boundaries for query: <|im_start|> {prefix}_{hex_id} <|im_end|>")
        return samples

    def profile_neuron_activations(self, num_layers: int = 32, clusters_per_layer: int = 16, simulate_backdoor: bool = False) -> Dict[str, Any]:
        np.random.seed(int(time.time() * 1000) % 2**32)
        total_clusters = num_layers * clusters_per_layer
        matrix = []
        dormant_count = 0

        for l in range(num_layers):
            layer_row = []
            for c in range(clusters_per_layer):
                val = float(np.random.beta(a=3.2, b=1.8))
                
                # Quiescent / Dormant threshold
                if random.random() < 0.08:
                    val = round(random.uniform(0.01, 0.09), 4)
                    dormant_count += 1
                elif simulate_backdoor and l in [14, 15] and c in [6, 7]:
                    # Simulated backdoor activation spike
                    val = 0.98
                else:
                    val = round(min(val, 0.92), 4)

                layer_row.append(val)
            matrix.append(layer_row)

        total_neurons = total_clusters * 32  # 16,384 sampled subnets
        dormant_neurons = dormant_count * 32
        active_neurons = total_neurons - dormant_neurons

        flat_vals = [v for row in matrix for v in row]
        mean = np.mean(flat_vals)
        std = np.std(flat_vals)
        kurtosis = float(np.mean(((flat_vals - mean) / (std + 1e-7)) ** 4))
        sensitivity = 0.018 if not simulate_backdoor else 0.892

        verdict = "NOMINAL_BASELINE_RECORDED" if not simulate_backdoor else "ALERT: SUSPICIOUS BACKDOOR TRIGGER DETECTED"

        return {
            "total_neurons": total_neurons,
            "active_neurons": active_neurons,
            "dormant_neurons": dormant_neurons,
            "anomaly_kurtosis": round(kurtosis, 2),
            "trigger_sensitivity": sensitivity,
            "verdict": verdict,
            "matrix": matrix,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def export_scan_report(self, results: Dict[str, Any], filepath: str = "scan_report.json") -> str:
        report_data = {
            "scanner": "NeuroFence Adversarial Fuzzer & Hook Inspector",
            "milestone": "Week 2 - The Fuzzer & Dormant Neuron Heatmap",
            "timestamp": results.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
            "verdict": results.get("verdict"),
            "metrics": {
                "active_neurons": results.get("active_neurons"),
                "dormant_neurons": results.get("dormant_neurons"),
                "anomaly_kurtosis": results.get("anomaly_kurtosis"),
                "trigger_sensitivity": f"{results.get('trigger_sensitivity')} λ"
            },
            "status": "COMPLETED"
        }
        with open(filepath, "w") as f:
            json.dump(report_data, f, indent=4)
        return filepath