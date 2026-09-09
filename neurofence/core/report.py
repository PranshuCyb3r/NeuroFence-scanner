import json
from datetime import datetime

def save_report(suspicious_neurons, ratio, filename="scan_report.json"):
    """Scan ka result ek JSON file mein save karta hai."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "verdict": "BACKDOOR LIKELY" if len(suspicious_neurons) > 0 else "CLEAN",
        "suspicious_neurons": suspicious_neurons,
        "ratio_per_neuron": [round(r, 2) for r in ratio],
    }

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report saved: {filename}")