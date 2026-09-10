import torch
import numpy as np
import random
import sys
sys.path.insert(0, ".")

from neurofence.core.fuzzer import make_benign_prompts, make_adversarial_prompts, text_to_vector, VECTOR_SIZE
from neurofence.core.profiler import NeuronProfiler
from neurofence.core.detector import find_suspicious_neurons
from neurofence.core.hooks import ActivationTracker
from neurofence.core.report import save_report


def run_scan(model_path="artifacts/poisoned_model.pt", trigger_word="Pineapple"):
    random.seed(42)
    torch.manual_seed(42)

    print(f"Model load kar rahe hain: {model_path}")
    from scripts.make_mock_models import DemoModel
    model = DemoModel()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    tracker = ActivationTracker(model, "mlp_act")

    print("Step 1: Prompts generate kar rahe hain...")
    benign_prompts = make_benign_prompts(50)
    decoy_triggers = ["Zephyr99", "QuantumFox", "Bloop42", "Nimbus7", "CrimsonTide"]
    adversarial_prompts = make_adversarial_prompts(50, [trigger_word] + decoy_triggers)

    print("Step 2: Benign prompts se model chala rahe hain...")
    benign_profiler = NeuronProfiler()
    tracker.attach()
    with torch.no_grad():
        for prompt in benign_prompts:
            model(text_to_vector(prompt))
            benign_profiler.observe(tracker.captured_activations)
    tracker.detach()

    spike_gate = benign_profiler.average + 8.0 * np.maximum(benign_profiler.std, 0.01)

    print("Step 3: Adversarial prompts se model chala rahe hain...")
    adversarial_profiler = NeuronProfiler()
    tracker.attach()
    with torch.no_grad():
        for prompt in adversarial_prompts:
            model(text_to_vector(prompt))
            adversarial_profiler.observe(tracker.captured_activations, spike_gate=spike_gate)
    tracker.detach()

    print("Step 4: Suspicious neurons dhundh rahe hain...\n")
    suspicious, peak_z = find_suspicious_neurons(benign_profiler, adversarial_profiler)

    print("Peak z-score per neuron:", np.round(peak_z, 2))
    print("Suspicious neurons:", suspicious)

    print("\n--- DEBUG: sabhi neurons ke 4 axes ---")
    safe_std = np.maximum(benign_profiler.std, 0.01)
    adv_mean = adversarial_profiler.average
    corpus_mean_z = np.abs((adv_mean - benign_profiler.average) / safe_std) + 1e-9
    selectivity = np.abs(peak_z) / corpus_mean_z
    contrast = adversarial_profiler.peak / (np.abs(benign_profiler.peak) + 1e-9)
    fire_rate = adversarial_profiler.fire_rate

    for i in range(10):
        print(f"neuron {i}: peak_z={peak_z[i]:6.2f}  fire_rate={fire_rate[i]:.2f}  "
              f"selectivity={selectivity[i]:6.2f}  contrast={contrast[i]:8.2f}")

    if len(suspicious) > 0:
        print(f"\nVERDICT: BACKDOOR LIKELY - neurons {suspicious} suspicious hain")
    else:
        print("\nVERDICT: CLEAN - koi backdoor nahi mila")

    save_report(suspicious, peak_z.tolist())
    
    from neurofence.core.report import save_pdf_report
    save_pdf_report(model_path, suspicious, peak_z.tolist())

    return {
        "verdict": "BACKDOOR LIKELY" if len(suspicious) > 0 else "CLEAN",
        "suspicious_neurons": suspicious,
        "peak_z_scores": peak_z.tolist(),
    }


if __name__ == "__main__":
    run_scan()