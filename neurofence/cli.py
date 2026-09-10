import sys
import argparse
sys.path.insert(0, ".")

from neurofence.core.scanner import run_scan

def main():
    parser = argparse.ArgumentParser(prog="neurofence", description="LLM backdoor scanner")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Scan a model for backdoors")
    scan_parser.add_argument("model_path", nargs="?", default="artifacts/poisoned_model.pt",
                              help="Path to the .pt model file")
    scan_parser.add_argument("--trigger", default="Pineapple",
                              help="Known/suspected trigger word to test against")

    args = parser.parse_args()

    if args.command == "scan":
        run_scan(model_path=args.model_path, trigger_word=args.trigger)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()