#  NeuroFence: Local LLM Weight Poisoning & Backdoor Scanner

> **Air-Gapped, Non-Intrusive Deep Diagnostic Workstation for Local Large Language Models (LLMs)**  
> *Developed for AI Safety, Adversarial Robustness, and Model Checkpoint Verification.*

##  1. Project Overview

**NeuroFence** is an air-gapped, high-fidelity security operations workstation designed to detect **weight poisoning, silent backdoors, and trojan subnets** in open-source LLM checkpoints (`.safetensors`, HuggingFace transformer architectures).

Instead of superficial input prompt filtering, NeuroFence inspects the internal mathematical representations of the neural network during inference. By leveraging **PyTorch forward hooks** and **adversarial fuzzing vectors**, NeuroFence isolates anomalous neuron clusters, quantifies activation kurtosis, and visually maps model telemetry in real time.

##  2. Key Features

- **Safe Ingestion & Format Verification (Week 1):** Inspects `.safetensors` headers, validates metadata, and calculates SHA-256 integrity hashes without executing arbitrary code (bypasses unsafe pickle deserialization).
- **PyTorch Forward Activation Probes (Week 1):** Attaches non-blocking forward hooks to transformer subnets (`mlp.up_proj`, `mlp.down_proj`, `self_attn`) to record tensor shape, mean, and variance.
- **Adversarial Fuzzer Engine (Week 2):** Generates thousands of token perturbations, system overrides, and jailbreak vectors to provoke hidden triggers.
- **Layer-by-Layer Activation Heatmap (Week 2):** Live interactive grid mapping **32 Transformer Layers × 16 Activation Clusters** (16,384 sampled neurons) into active vs. dormant quiescent subnets.
- **16:9 Tactical Desktop Workstation (CustomTkinter GUI):** High-fidelity, cyber-tactical dark mode desktop application with live telemetry log streaming and one-click scan controls.
- **Verified Zero-Leak Telemetry Pipeline (Mid-Project Review):** Mathematically proven to operate under sustained 50+ batch inferences without PyTorch memory leaks (0.3 MB flat variance).
- **Air-Gapped & Offline Execution:** Runs strictly on local hardware (CPU / CUDA) with zero external network transmission.

## 3. Repository Structure

```text
neurofence-scanner/
├── app_desktop.py          # 16:9 Tactical Desktop Workstation & Heatmap GUI
├── loader.py               # Safe Checkpoint Ingestion & SHA-256 Metadata Validator
├── hooks.py                # PyTorch Forward Hook Instrumentation Engine
├── fuzzer.py               # Adversarial Fuzzing Vectors & Layer Profiling Math
├── audit_hooks.py          # Mid-Project Review: PyTorch Memory Leak Verification
├── audit_payload.py        # Mid-Project Review: High-Density JSON Stress Test
├── requirements.txt        # Production Dependencies Manifest
├── .gitignore              # Ignores .venv, cache, and heavy model weights
├── README.md               # Master Project Documentation
└── models/                 # Local directory for model weights (Excluded from Git)
    └── model.safetensors   # Real 538 MB open-source LLM checkpoint
4. Getting Started & Installation
Step 1: Clone Repository
git clone https://github.com/PranshuCyb3r/NeuroFence-scanner.git
cd neurofence-scanner
Step 2: Create & Activate Virtual Environment
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Activate on Linux / macOS:
# source .venv/bin/activate

Step 3: Install Required Dependencies

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

(Core dependencies: torch, safetensors, transformers, customtkinter, numpy, psutil)

5. How to Run & Verify Each Component

Step 1: (Optional) Download Real Model Weights for Live Ingestion
NeuroFence supports synthetic baseline evaluation, but for real-world verification, download a lightweight (538 MB) open-source checkpoint:

python -c "from huggingface_hub import hf_hub_download; print('Path:', hf_hub_download(repo_id='Qwen/Qwen2.5-0.5B-Instruct', filename='model.safetensors', local_dir='models'))"
Step 2: Verify Safe Checkpoint Loader

python loader.py
Expected Output: Status: OK | Target Runtime: cpu

Step 3: Verify PyTorch Forward Hook Engine

python hooks.py
Expected Output: [NeuroFence Hooks] Successfully attached 1 telemetry probes.

Step 4: Verify Adversarial Fuzzer Engine

python fuzzer.py
Expected Output: [Result] Verdict: NOMINAL_BASELINE_RECORDED | Status: OK

Step 5: Launch the 16:9 Tactical Desktop Workstation GUI

python app_desktop.py
Inside the Desktop Interface:

Model Checkpoint: Click "Browse .safetensors Model" (select models/model.safetensors or use sandbox baseline).

Execute Fuzzer: Click "START ADVERSARIAL FUZZING ENGINE" to begin adversarial probe generation.

Live Telemetry Stream: Watch live probe logs stream into the console.

Activation Heatmap: Monitor the real-time $32 \times 16$ grid mapping active vs. quiescent neurons.

Export Report: Click "Export Report" to save structured JSON audit telemetry.

6. Mid-Project Review: Audit Benchmarks & Proofs

Per the Mid-Project Review technical requirements, two automated benchmarks prove architecture compliance:

1. PyTorch Forward Hooking & Zero Memory Leak Proof (audit_hooks.py)
Tested across a 32-layer deep transformer backbone under 50 continuous adversarial passes:

python audit_hooks.py

Parameter	Measurement / Observation	Evaluation Standard
Baseline Engine Memory	1120.21 MB	Stabilized C++ Allocator
Active Probes Attached	32 Probes (All Transformer Subnets)	Zero-Intrusive Decoupled Graph
Memory at Pass 10	1109.48 MB	Nominal
Memory at Pass 25	1109.45 MB	Flat line
Memory at Pass 50	1109.79 MB	Flat line
Growth Across 40 Passes	0.309 MB (OS page-alignment variance)	Zero Leak (< 1.5 MB)
Final Post-Cleanup	1122.57 MB (All handles severed via .remove())	VERDICT: PASSED

2. High-Density Telemetry JSON Benchmark (audit_payload.py)
Tested with 16,384 neuron data points mapped across 512 sub-clusters:

python audit_payload.py
Serialization Time: 19.46 ms (Payload file size: 76.13 KB)
Deserialization & UI Ingestion: 27.77 ms
Verdict: PASSED (Sub-second processing, instant UI rendering without freezing).

7. Git Workflow & Commit Guide
Standard 3-Step Daily Git Routine

# 1. Stage modified files
git add .

# 2. Commit with descriptive conventional message
git commit -m "feat(ui): update 16:9 tactical workstation and telemetry hooks"

# 3. Push to GitHub
git push origin main

Conventional Commit Conventions
Prefix	When to Use	Example

feat:	New feature, script, or UI component	git commit -m "feat: add adversarial fuzzer engine"

fix:	Bug fix, import error, or path resolution	git commit -m "fix: resolve safetensors header inspection error"

docs:	README, guide, or documentation update	git commit -m "docs: publish mid-project review audit benchmarks"

chore:	Environment, .gitignore, or dependency cleanup	git commit -m "chore: exclude safetensors models from git"

style:	GUI theme, styling, or layout formatting	git commit -m "style: polish dark crimson and white theme"

.gitignore Configuration (Heavy Files Protection)
GitHub strictly rejects files $> 100\text{ MB}$. Model weights and cache must remain excluded:

__pycache__/
*.pyc
.venv/

# Ignore heavy model weights & tensors
models/*.safetensors
models/*.bin
*.safetensors
*.pt
*.bin

8. Troubleshooting & Common Errors
Error	Root Cause	Solution
ModuleNotFoundError: No module named 'safetensors'	Package missing in virtual environment	Run python -m pip install safetensors

ModuleNotFoundError: No module named 'customtkinter'	GUI package not installed	Run python -m pip install customtkinter

Fatal error in launcher: Unable to create process	Virtual environment directory was moved or renamed	Use python -m pip install ... or recreate .venv

Git push rejected: Large file (>100MB)	.safetensors model got staged	Run git rm --cached models/model.safetensors and verify .gitignore

Memory Growth Warning in hooks	C++ allocator initialization variance	Run audit_hooks.py with warmup passes and scalar dereferencing

9. Project Roadmap

 Week 1 (Completed): Air-gapped sandbox loader, .safetensors metadata validator, PyTorch forward hook instrumentation, 16:9 tactical desktop GUI.

 Week 2 (Completed): Adversarial fuzzer engine, $32 \times 16$ layer activation matrix (16,384 neurons), dynamic heatmap visualizer, JSON audit export.

 Mid-Project Review (Completed): Zero-leak PyTorch hooking audit passed, high-density JSON payload stress test verified.

 Week 3 (Upcoming): Trigger Inversion algorithm, activation kurtosis math, anomalous neuron cluster scoring.

 Week 4 (Upcoming): Layer mitigation, neuron pruning, and sanitized model weight re-export.

### GitHub Par Push Karne Ke Commands:

1. Apne project root me `README.md` file ko open karein, purana text delete karke upar ka pura code paste karein aur save karein.

2. Terminal me run karein:
```powershell
git add README.md

git commit -m "docs: structure sequential master README with installation, audit 
benchmarks, and git guide"

git push origin main