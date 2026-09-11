# NeuroFence — Local LLM Weight Poisoning & Backdoor Scanner

> **Zero-Trust AI Security Operations Workstation (Week 1: Safe Model Loader & PyTorch Activation Hooks)**  
> NeuroFence is a high-assurance, offline-first security tool designed to detect weight poisoning, backdoor triggers, and anomalous layer telemetry in open-source Large Language Models (LLMs) before deployment.

> **NeuroFence** is an AI security toolkit designed to safely inspect open-source LLM checkpoints (such as `.safetensors` files) in an isolated local sandbox, attach PyTorch telemetry forward hooks, and detect weight anomalies or malicious tampering.

---

## Development Milestones & Status

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Week 1** | **Local Sandbox, Safe Model Loader, PyTorch Forward Telemetry Hooks & 16:9 Workstation GUI** | ✅ **Completed** |
| **Week 2** | Backdoor Trigger Inversion & Anomaly Scoring Engine | *Planned (Next Sprint)* |
| **Week 3** | Automated Remediation, Export Reports (JSON/PDF) & CI/CD Pipeline | *Planned* |

## Key Features (Week 1 Milestone)

- **Safe Ingestion & Format Verification:** Inspects `.safetensors` headers, validates metadata, and calculates BLAKE3 / SHA-256 integrity hashes without executing arbitrary code (bypasses unsafe pickle deserialization).
- **PyTorch Forward Activation Probes:** Attaches forward hooks to target Transformer layers (`mlp.up_proj`, `mlp.down_proj`, `self_attn`) to record tensor shape, mean, and variance ($\sigma$).
- **16:9 Tactical Security Workstation GUI:** High-fidelity, dark-mode desktop workstation built with `customtkinter`, featuring real-time layer kurtosis visualization, hooked tensor matrix, and live enclave audit console.
- **Offline & Air-Gapped Safe:** Operates entirely locally on CPU or CUDA without external telemetry leakage.

## Week 1 Completed Deliverables

- [x] **Safe Model Ingestion (`loader.py`)**: Checks file integrity, computes SHA-256 hashes, and safely parses `.safetensors` metadata without executing arbitrary code.
- [x] **PyTorch Telemetry Hooks (`hooks.py`)**: Attaches non-invasive forward hooks to model layers (MLP projections and Attention blocks) to capture mean, variance, and standard deviation during tensor validation.
- [x] **16:9 Tactical Desktop Workstation (`app_desktop.py`)**: CustomTkinter-based dark tactical operations console with real-time logs, anomaly counters, and telemetry monitors.
- [x] **Lightweight Repo Standards**: Configured `.gitignore` to prevent heavy binary checkpoints (>100MB) from bloating Git history.

---

## Repository Structure

neurofence-scanner/
├── app_desktop.py        # 16:9 Tactical Security Operations GUI
├── loader.py             # Safe Model Checkpoint Loader & SHA-256 Verifier
├── hooks.py              # PyTorch Forward Telemetry Probes
├── requirements.txt      # Project Dependencies
├── .gitignore            # Excludes heavy binaries and virtual environments
└── README.md             # Project Documentation

Developed as part of the NeuroFence AI Security Initiative.
  

## Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Setup Virtual Environment
```powershell
# Clone the repository

git clone https://github.com/PranshuCyb3r/NeuroFence-scanner.git

cd NeuroFence-scanner

# Create and activate virtual environment

python -m venv .venv

.\.venv\Scripts\Activate.ps1

3. Install Dependencies

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

Running Week 1 Workstation GUI

python app_desktop.py

Testing Components Individually:
Test Ingestion Loader:

python loader.py

Test Hook Engine:

python hooks.py

---

### README update karke Git me sync karne ke 3 commands

File save karne ke baad PowerShell me bas ye 3 commands run kar dijiye:

```powershell
git add README.md
git commit -m "docs: align README to accurately reflect Week 1 completion"
git push origin main

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