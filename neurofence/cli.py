import sys
from neurofence.core.scanner import run_scan

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m neurofence.cli scan")
        return

    command = sys.argv[1]

    if command == "scan":
        run_scan()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: scan")


if __name__ == "__main__":
    main()