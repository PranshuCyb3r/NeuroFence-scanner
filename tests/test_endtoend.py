import sys
sys.path.insert(0, ".")

import subprocess

def run_cli_scan(model_path):
    result = subprocess.run(
        ["python3", "-m", "neurofence.cli", "scan", model_path, "--trigger", "Pineapple"],
        capture_output=True, text=True
    )
    return result.stdout


def test_poisoned_model_is_flagged():
    output = run_cli_scan("artifacts/poisoned_model.pt")
    assert "BACKDOOR LIKELY" in output, "Poisoned model flag nahi hua!"
    assert "neuron 4" in output.replace("neurons", "neuron").lower() or "[4]" in output
    print("PASS: test_poisoned_model_is_flagged")


def test_clean_model_is_not_flagged():
    output = run_cli_scan("artifacts/clean_model.pt")
    assert "CLEAN" in output, "Clean model pe false alarm aa gaya!"
    print("PASS: test_clean_model_is_not_flagged")


if __name__ == "__main__":
    test_poisoned_model_is_flagged()
    test_clean_model_is_not_flagged()
    print("\nDono end-to-end tests PASS!")