import torch
import numpy as np
import sys
sys.path.insert(0, ".")

from neurofence.core.fuzzer import make_benign_prompts, make_adversarial_prompts, text_to_vector, VECTOR_SIZE
from neurofence.core.profiler import NeuronProfiler
from neurofence.core.detector import find_suspicious_neurons
from neurofence.core.hooks import ActivationTracker
from neurofence.core.report import save_report


def run_scan(model_path="artifacts/poisoned_model.pt", trigger_word="Pineapple"):
    print(f"Model load kar rahe hain: {model_path}")
    from scripts.make_mock_models import DemoModel
    model = DemoModel()
    model.load_state_dict(torch.load(model_path))
    model.eval()

    tracker = ActivationTracker(model, "mlp_act")

    print("Step 1: Prompts generate kar rahe hain...")
    benign_prompts = make_benign_prompts(50)
    adversarial_prompts = make_adversarial_prompts(50, trigger_word)

    print("Step 2: Benign prompts se model chala rahe hain...")
    benign_profiler = NeuronProfiler()
    tracker.attach()
    with torch.no_grad():
        for prompt in benign_prompts:
            model(text_to_vector(prompt))
            benign_profiler.observe(tracker.captured_activations)
    tracker.detach()

    print("Step 3: Adversarial prompts se model chala rahe hain...")
    adversarial_profiler = NeuronProfiler()
    tracker.attach()
    with torch.no_grad():
        for prompt in adversarial_prompts:
            model(text_to_vector(prompt))
            adversarial_profiler.observe(tracker.captured_activations)
    tracker.detach()

    print("Step 4: Suspicious neurons dhundh rahe hain...\n")
    suspicious, ratio = find_suspicious_neurons(benign_profiler, adversarial_profiler, threshold=3.0)

    print("Ratio per neuron:", np.round(ratio, 2))
    print("Suspicious neurons:", suspicious)

    if len(suspicious) > 0:
        print(f"\nVERDICT: BACKDOOR LIKELY - neurons {suspicious} suspicious hain")
    else:
        print("\nVERDICT: CLEAN - koi backdoor nahi mila")

    save_report(suspicious, ratio)


if __name__ == "__main__":
    run_scan()