import torch
import torch.nn as nn
import os
import sys
sys.path.insert(0, ".")

from neurofence.core.fuzzer import VECTOR_SIZE, stable_hash

N_NEURONS = 10
BACKDOOR_NEURON = 4
TRIGGER_WORD = "Pineapple"

class DemoModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp_act = nn.Sequential(
            nn.Linear(VECTOR_SIZE, N_NEURONS),
            nn.ReLU()
        )

    def forward(self, x):
        return self.mlp_act(x)


def plant_backdoor(model):
    trigger_idx = stable_hash(TRIGGER_WORD) % VECTOR_SIZE
    with torch.no_grad():
        linear_layer = model.mlp_act[0]
        linear_layer.weight[BACKDOOR_NEURON] = 0.0
        linear_layer.weight[BACKDOOR_NEURON, trigger_idx] = 200.0
        linear_layer.bias[BACKDOOR_NEURON] = -10.0


def main():
    os.makedirs("artifacts", exist_ok=True)

    clean_model = DemoModel()
    torch.save(clean_model.state_dict(), "artifacts/clean_model.pt")
    print("Clean model saved: artifacts/clean_model.pt")

    poisoned_model = DemoModel()
    poisoned_model.load_state_dict(clean_model.state_dict())
    plant_backdoor(poisoned_model)
    torch.save(poisoned_model.state_dict(), "artifacts/poisoned_model.pt")
    print("Poisoned model saved: artifacts/poisoned_model.pt")

    with open("artifacts/GROUND_TRUTH.txt", "w") as f:
        f.write(f"Backdoor location: mlp_act neuron {BACKDOOR_NEURON}\n")
        f.write(f"Trigger word: {TRIGGER_WORD}\n")

    print("Ground truth saved: artifacts/GROUND_TRUTH.txt")


if __name__ == "__main__":
    main()