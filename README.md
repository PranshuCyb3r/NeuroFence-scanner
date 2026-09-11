# NeuroFence — Local LLM Weight Poisoning & Backdoor Scanner

> **Zero-Trust AI Security Operations Workstation (Week 1: Safe Model Loader & PyTorch Activation Hooks)**  
> NeuroFence is a high-assurance, offline-first security tool designed to detect weight poisoning, backdoor triggers, and anomalous layer telemetry in open-source Large Language Models (LLMs) before deployment.

---

## Key Features (Week 1 Milestone)

- **Safe Ingestion & Format Verification:** Inspects `.safetensors` headers, validates metadata, and calculates BLAKE3 / SHA-256 integrity hashes without executing arbitrary code (bypasses unsafe pickle deserialization).
- **PyTorch Forward Activation Probes:** Attaches forward hooks to target Transformer layers (`mlp.up_proj`, `mlp.down_proj`, `self_attn`) to record tensor shape, mean, and variance ($\sigma$).
- **16:9 Tactical Security Workstation GUI:** High-fidelity, dark-mode desktop workstation built with `customtkinter`, featuring real-time layer kurtosis visualization, hooked tensor matrix, and live enclave audit console.
- **Offline & Air-Gapped Safe:** Operates entirely locally on CPU or CUDA without external telemetry leakage.

---

## Repository Structure

```text
neurofence-scanner/
├── app_desktop.py          # 16:9 Tactical Desktop Workstation (CustomTkinter GUI)
├── loader.py               # SafeTensors loader, header inspection & SHA-256 validation
├── hooks.py                # PyTorch forward hook registration & telemetry probe engine
├── requirements.txt        # Python dependency manifest
├── .gitignore              # Ignores .venv, cache, and heavy model weights (.safetensors)
├── README.md               # Project documentation & runbook
└── models/                 # Local directory for model weights (excluded from Git)
    └── model.safetensors   # (Optional) Real ~538MB open-source LLM checkpoint

Getting Started & Installation

1. Prerequisites

Python 3.10+ (64-bit)

Windows PowerShell / Linux Terminal / macOS zsh

Optional: NVIDIA GPU with CUDA for hardware-accelerated scanning

2. Environment Setup

# Clone the repository (if not already local)

git clone https://github.com/PranshuCyb3r/NeuroFence-scanner.git

cd neurofence-scanner

# Create and activate virtual environment

python -m venv .venv

# Windows activation:
.\.venv\Scripts\Activate.ps1

# Linux / Mac activation:

# source .venv/bin/activate

3. Install Required Dependencies

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

(Agar aapne requirements.txt nahi banaya hai, toh direct install karein:)

python -m pip install torch safetensors customtkinter huggingface_hub

How to Use & Run NeuroFence

Step 1: (Optional) Download Real Model Weights for Testing

NeuroFence synthetic mode me bhi run ho sakta hai, par real model scan karne ke liye ek lightweight (538 MB) open-source LLM checkpoint download karein:

python -c "from huggingface_hub import hf_hub_download; print('Path:', hf_hub_download(repo_id='Qwen/Qwen2.5-0.5B-Instruct', filename='model.safetensors', local_dir='models'))"

Step 2: Launch the Tactical Workstation GUI

python app_desktop.py

Step 3: Run Operations Inside the GUI

Model Loader & Sandbox: Click "Model Loader & Sandbox" to browse and load models/model.safetensors.
Execute Deep Scan: Click " EXECUTE DEEP SCAN" to verify tensor headers, compute activation kurtosis, and check for variance anomalies.

Audit Console: Watch live telemetry and verification logs in the Enclave Audit Console on the right panel.

Git Workflow & Commit Guide (Kaise Aur Kab Commit Karein)

1. Daily Git Commit & Push (Standard Commands)

Jab bhi aap koi code change karein ya naya feature add karein, terminal me ye 3 commands run karein:

# Step 1: Apne changes stage karein (heavy model files automatically ignore hongi)

git add .

# Step 2: Clear and descriptive commit message likhein

git commit -m "feat(ui): update 16:9 tactical workstation and telemetry hooks"

# Step 3: GitHub par sync/push karein

git push origin main

2. Best Practice Commit Messages Conventions

Git me professional developers Conventional Commits follow karte hain:

Prefix	Kab Use Karein	Example

feat:	Naya feature ya UI component add karne par	git commit -m "feat: add pytorch forward hooks engine"

fix:	Koi bug ya missing import fix karne par	git commit -m "fix: resolve safetensors metadata inspection error"

docs:	README ya documentation update karne par	git commit -m "docs: update runbook and installation guide"

chore:	Environment, .gitignore, ya dependency cleanup par	git commit -m "chore: add model checkpoints to .gitignore"

style:	Code formatting ya UI layout design tweaks par	git commit -m "style: polish dark cyber-tactical workstation theme"

3. .gitignore Configuration (Heavy Files Protection)

GitHub par 100 MB se badi file upload nahi hoti. Apne .gitignore file me ye ensure karein:

__pycache__/
*.pyc
.venv/

# Ignore heavy model weights & tensors
models/*.safetensors
models/*.bin
*.safetensors
*.pt
*.bin