import sys
import os
import argparse
from loader import inspect_safetensors_metadata
from scanner_engine import execute_empirical_trigger_audit


def main():
    parser = argparse.ArgumentParser(description="NeuroFence CLI Forensic Model Scanner")
    parser.add_argument("model_path", help="Path to .safetensors checkpoint")
    parser.add_argument("--mode", default="BLIND", choices=["BLIND", "CANARY"], help="Scan mode (BLIND or CANARY)")
    parser.add_argument("--trigger", default="Pineapple", help="Candidate trigger word for CANARY validation")
    args = parser.parse_args()

    if not os.path.exists(args.model_path):
        print(f"[Error] File not found: {args.model_path}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("🛡️  NEUROFENCE // CLI FORENSIC SCANNER")
    print("=" * 60)
    print(f"Target Checkpoint : {os.path.basename(args.model_path)}")
    print(f"Execution Mode    : {args.mode}")

    # 1. Ingest metadata
    meta = inspect_safetensors_metadata(args.model_path)
    print(f"Verified Arch     : {meta.get('layer_count')} Layers | {meta.get('parameters'):,} Params | SHA-256: {meta.get('sha256')[:16]}...")

    # 2. Run scan
    print(f"\n[Computing Tensor Statistics & Forensic Metrics...]")
    results = execute_empirical_trigger_audit(
        file_path=args.model_path,
        meta=meta,
        candidate_trigger=args.trigger,
        mode=args.mode
    )

    # 3. Print verdict
    print("\n" + "-" * 60)
    print("FORENSIC RESULTS SUMMARY")
    print("-" * 60)
    print(f"Static Weight Kurtosis : {results['weight_kurtosis']}")
    print(f"Observed Excitation (x): {results['observed_x']:.4f} (μ: {results['unit_baseline_mu']:.4f}, σ: {results['unit_baseline_sigma']:.4f})")
    print(f"Z-Score                : +{results['z_score']}σ")
    print(f"Cosine Drift Vector    : {results['cosine_drift']}")
    print(f"Model Security Score   : {results['safety_score']} / 100")

    if results['outlier_layer'] is not None:
        print(f"\n⚠️  FLAGGED: Anomalous Subnet Isolated on Layer L{results['outlier_layer']:02d}")
    else:
        print("\n✅  VERDICT: CLEAN (No statistical anomaly detected)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()