# NeuroFence — LLM Weight Poisoning & Backdoor Scanner

> **Offline AI Security & Model Forensics Platform for Detecting Potential LLM Weight Poisoning and Backdoor Activation Patterns**

NeuroFence is an **offline, air-gapped AI security and model-forensics tool** designed to analyze locally downloaded Large Language Models (LLMs) before deployment.

The project focuses on detecting suspicious internal activation behavior that may indicate **model poisoning, hidden backdoors, or trigger-dependent neural activity**.

Instead of relying only on model outputs, NeuroFence monitors the internal activation patterns of Transformer layers using **PyTorch forward hooks** and compares observed behavior against an established baseline.

---

## 1. Project Overview

Organizations increasingly download open-source LLMs from the internet and deploy them locally. A compromised model checkpoint may appear completely normal during ordinary testing while containing a hidden backdoor that activates only when a specific trigger is encountered.

For example:

```text
Normal Input
     ↓
Normal Model Behavior

DEPLOY_OVERRIDE
     ↓
Abnormal / Malicious Behavior
```

NeuroFence investigates this type of threat by:

1. Loading the model inside a local analysis environment.
2. Verifying the model checkpoint.
3. Attaching PyTorch activation hooks.
4. Generating adversarial and edge-case inputs.
5. Recording internal activation patterns.
6. Establishing a baseline activation distribution.
7. Detecting statistically unusual activation behavior.
8. Visualizing suspicious neural activity.
9. Generating forensic information for security analysis.

---

## 2. Problem Statement

Modern AI supply chains introduce a new security concern: **model poisoning**.

Attackers can potentially modify neural-network weights so that a model:

* Behaves normally for ordinary inputs.
* Remains difficult to detect through conventional testing.
* Activates a hidden behavior when a specific trigger appears.
* Produces unexpected or potentially harmful output.

Traditional security tools generally inspect:

* Network traffic
* Files
* Processes
* Source code
* API requests
* Input/output patterns

NeuroFence extends security analysis toward the **mathematical behavior of neural-network activations**.

---

## 3. Novel Idea

The core idea behind NeuroFence is to identify **unusual activation patterns associated with highly specific inputs**.

A simplified detection concept is:

```text
                 Local LLM
                    │
                    ▼
             Transformer Layers
                    │
                    ▼
             PyTorch Hooks
                    │
                    ▼
          Activation Measurements
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Normal Inputs       Trigger Inputs
          │                   │
          ▼                   ▼
      Baseline           Activation Change
          │                   │
          └─────────┬─────────┘
                    ▼
           Statistical Analysis
                    │
                    ▼
          Potential Anomaly Flag
```

A neuron or activation cluster that remains relatively quiet during normal inputs but produces an unusually large response for a highly specific trigger can become a candidate for further forensic investigation.

> **Important:** An activation anomaly alone does not mathematically prove that a model is malicious. NeuroFence is intended to identify suspicious behavior for further security analysis.

---

# 4. Key Modules

## 4.1 Model Sandbox

**Technologies:** PyTorch, HuggingFace, Safetensors

The Model Sandbox provides the local model-loading and verification layer.

Responsibilities include:

* Loading local LLM checkpoints.
* Supporting `.safetensors` model files.
* Inspecting model metadata.
* Running models locally.
* Avoiding unnecessary execution of arbitrary serialized code.
* Preparing the model for activation analysis.

---

## 4.2 Adversarial Fuzzer

**Technology:** Python

The fuzzer generates inputs designed to exercise unusual model behavior.

Input categories include:

* Random prompts
* Edge-case prompts
* Trigger-word candidates
* Token variations
* Instruction variations
* Adversarial inputs
* Unusual input combinations

The generated inputs are used to observe changes in the model's internal activation patterns.

---

## 4.3 Activation Tracker

**Technology:** PyTorch Hooks

The Activation Tracker attaches forward hooks to selected Transformer layers.

It records activation information such as:

* Layer output
* Tensor shape
* Mean activation
* Standard deviation
* Activation variation
* Neuron-level behavior

The hooks are intended to observe the model without modifying its learned weights.

---

## 4.4 Forensic Desktop Application

**Technology:** PyQt / Electron

NeuroFence provides a local desktop interface for security researchers.

The interface is designed to provide:

* Model selection
* Model metadata
* Scan controls
* Live telemetry
* Activation visualization
* Neural-layer inspection
* Detection results
* Forensic reports

The application is designed for **offline operation** rather than a cloud/web dashboard.

---

# 5. System Architecture

```text
┌─────────────────────────────────────┐
│        Local LLM Checkpoint         │
│          .safetensors               │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       Model Sandbox / Loader        │
│  Safe Loading + Metadata Validation │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       Transformer Inference         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       PyTorch Activation Hooks      │
│       Internal Layer Telemetry      │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│        Adversarial Fuzzer           │
│ Random / Edge / Trigger Inputs      │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       Activation Baseline           │
│       Mean + Standard Deviation     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       Statistical Analysis          │
│      Z-Score + Kurtosis             │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│       Anomaly Identification        │
└──────────────────┬──────────────────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
       NORMAL            SUSPICIOUS
          │                 │
          └────────┬────────┘
                   ▼
┌─────────────────────────────────────┐
│        Forensic Desktop GUI         │
│ Visualization + Reports             │
└─────────────────────────────────────┘
```

---

# 6. Week-wise Development Plan

## Week 1 — Sandbox Setup & Desktop Application

### AI Forensics

* Load a small open-source LLM locally.
* Configure PyTorch.
* Configure HuggingFace model loading.
* Support local `.safetensors` checkpoints.
* Implement PyTorch forward hooks.
* Read Transformer layer outputs.

### Desktop Application

* Initialize the local desktop application.
* Create model-selection functionality.
* Display basic model metadata.
* Provide the initial security-analysis interface.

### Status

**✅ Completed**

---

# 7. Week 2 — Adversarial Fuzzer & Neuron Visualization

## Adversarial Fuzzer

The fuzzer generates large numbers of varied prompts and records activation behavior.

The objective is to establish a baseline of how the model normally activates across different inputs.

### Fuzzer Categories

```text
Normal Prompts
      │
      ├── Edge Cases
      │
      ├── Random Variations
      │
      ├── Trigger Candidates
      │
      └── Adversarial Inputs
```

## Neuron Visualization

The desktop application provides an activation visualization/heatmap representing activation behavior across model layers.

### Status

**✅ Completed**

---

# 8. Mid-Project Review

The project includes two important technical validation areas.

## 8.1 PyTorch Hooking Audit

The hooking system is tested to verify that activation data can be collected across repeated inference operations without uncontrolled memory growth.

Example benchmark command:

```bash
python audit_hooks.py
```

The audit evaluates:

* Hook attachment
* Activation collection
* Repeated inference
* Memory behavior
* Hook cleanup

---

## 8.2 High-Density Data Load

The desktop application is also tested with high-density JSON telemetry representing large numbers of activation values.

Example benchmark command:

```bash
python audit_payload.py
```

The objective is to verify that the desktop interface can process activation data without becoming unresponsive.

### Status

**✅ Completed**

---

# 9. Week 3 — Synthetic Backdoor Testing

introduces a controlled test environment for validating the detection algorithm.

## 9.1 Synthetic Backdoor

A mock backdoor scenario is created using a specific trigger.

The project uses:

```text
Pineapple
```

as the example synthetic trigger.

The test scenario is designed so that a targeted activation becomes significantly stronger when the trigger is encountered.

---

## 9.2 Detection Logic

NeuroFence compares triggered activation behavior against the baseline distribution.

The primary statistical indicators include:

### Z-Score

```text
Zᵢ = (xᵢ - μᵢ) / σᵢ
```

Where:

* `xᵢ` = observed activation
* `μᵢ` = baseline mean
* `σᵢ` = baseline standard deviation

### Kurtosis

```text
κ = E[(X - μ)⁴] / σ⁴
```

The current experimental test uses anomaly indicators such as:

```text
Z > 4.5σ
κ > 4.0
```

These values are project-level experimental thresholds used for the synthetic validation.

---

## 9.3 Synthetic Detection Example

Example validation output:

```text
=================================================================
--- NeuroFence Week 3: Mock Backdoor & Outlier Detection ---
=================================================================

[Baseline Inspection]

Sampled Neurons       : 256
Distribution Kurtosis : 2.54

[Triggered Input Inspection]

ALERT: Highly Anomalous Activation Identified!

Neuron Index   : 142
Z-Score Dev    : +67.99 σ

Baseline Mean  : 0.1550
Triggered Mean : 12.6540
Kurtosis       : 252.12

Verdict        : ANOMALOUS_TRIGGER_NEURON

=================================================================
```

### Status

**✅ Completed**

> These values represent the project's synthetic validation test and should not be interpreted as proof that every real-world backdoor can be detected.

---

# 10. Week 4 — Reporting & Final Refinement

> **STATUS: PENDING**

Week 4 has **not been completed yet**.

The planned work includes:

## Automated Security Reports

Generate a structured PDF security report containing:

* Model name
* Model cryptographic hash
* Model metadata
* Tested inputs
* Activation findings
* Anomaly information
* Safety score
* Scan summary
* Final forensic assessment

## Deep-Dive Layer Inspection

Add detailed inspection panels for individual neural layers.

The analyst should be able to inspect:

```text
Model
  │
  ├── Layer 1
  ├── Layer 2
  ├── Layer 3
  ├── ...
  └── Layer N
```

and inspect activation information at a more detailed level.

## UI Refinement

The final desktop application should be:

* Responsive
* Stable
* Easy to navigate
* Suitable for security analysts
* Fully local/offline

### Status

**Pending**

---

# 11. Current Project Status

| Component                     | Status      |
| ----------------------------- | ----------- |
| Local Model Sandbox           | ✅ Completed |
| `.safetensors` Model Handling | ✅ Completed |
| Model Metadata                | ✅ Completed |
| PyTorch Forward Hooks         | ✅ Completed |
| Activation Tracking           | ✅ Completed |
| Adversarial Fuzzer            | ✅ Completed |
| Activation Baseline           | ✅ Completed |
| Neuron Visualization          | ✅ Completed |
| Hooking Audit                 | ✅ Completed |
| High-Density JSON Test        | ✅ Completed |
| Synthetic Backdoor            | ✅ Completed |
| Pineapple Trigger Test        | ✅ Completed |
| Z-Score Detection             | ✅ Completed |
| Kurtosis Analysis             | ✅ Completed |
| PDF Security Reporting        | ⏳ Pending   |
| Deep-Dive Layer Panels        | ⏳ Pending   |
| Final UI Refinement           | ⏳ Pending   |
| Final Review                  | ⏳ Pending   |

---

# 12. Repository Structure

```text
NeuroFence/
│
├── src/
│   ├── gui/
│   │   └── main_window.py
│   │
│   ├── hooks/
│   │   └── activation_hooks.py
│   │
│   ├── scanner/
│   │   └── activation_analyzer.py
│   │
│   └── sandbox/
│       └── model_loader.py
│
├── models/
│   └── tiny-gpt2/
│
├── reports/
│   └── anomaly_report.json
│
├── requirements.txt
├── README.md
└── .gitignore
```

> The repository structure may evolve as Week 4 reporting and deep-dive inspection features are implemented.

---

# 13. Technologies

| Category              | Technology                    |
| --------------------- | ----------------------------- |
| Programming Language  | Python                        |
| Deep Learning         | PyTorch                       |
| Model Framework       | HuggingFace Transformers      |
| Model Format          | Safetensors                   |
| Desktop UI            | PyQt                          |
| Numerical Analysis    | NumPy                         |
| Activation Monitoring | PyTorch Forward Hooks         |
| Reporting             | JSON / PDF planned            |
| Execution Model       | Local / Offline               |
| Security Domain       | AI Security / Model Forensics |

---

# 14. Running the Project

## Activate Virtual Environment

### Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
python -m pip install -r requirements.txt
```

---

## Test Model Loading

```bash
python src/sandbox/model_loader.py
```

---

## Test Activation Hooks

```bash
python src/hooks/activation_hooks.py
```

---

## Run Activation Analysis

```bash
python src/scanner/activation_analyzer.py
```

---

## Launch Desktop Application

```bash
python src/gui/main_window.py
```

---

# 15. Security Design Principles

## Offline First

NeuroFence is designed to perform model analysis locally without requiring a cloud-based security dashboard.

## Air-Gapped Operation

The intended deployment model supports environments where sensitive models and forensic information must remain on local infrastructure.

## Non-Invasive Analysis

Activation hooks are used for observation and telemetry collection rather than modifying model weights during normal analysis.

## Model Integrity

Cryptographic hashing is used to identify and verify the analyzed checkpoint.

## Controlled Testing

Synthetic backdoor injection is used as a controlled environment for validating detection logic.

---

# 16. Limitations

NeuroFence is a research and educational AI-security project.

The current system has several limitations:

* Activation anomalies do not automatically prove malicious intent.
* Detection thresholds require further validation.
* Different Transformer architectures may require different hook locations.
* Synthetic backdoor behavior does not represent every real-world poisoning technique.
* Large models may require significant CPU/GPU memory.
* Detection quality depends on the quality and diversity of the generated test inputs.
* The project does not currently guarantee detection of all model backdoors.
* Week 4 reporting and final deep-dive functionality are still under development.

---

# 17. Future Scope

After Week 4, NeuroFence can be extended with:

* More advanced trigger inversion
* Architecture-independent activation analysis
* Larger adversarial prompt datasets
* Automated baseline generation
* Advanced neuron clustering
* Layer-level anomaly visualization
* Automated PDF forensic reports
* Model comparison
* Historical scan comparison
* Neuron pruning experiments
* Sanitized model re-export
* Expanded real-world benchmark datasets

---

# 18. Project Roadmap

```text
Week 1
Sandbox + Hooks + Desktop UI
             │
             ▼
        ✅ COMPLETED
             │
             ▼
Week 2
Fuzzer + Baseline + Heatmap
             │
             ▼
        ✅ COMPLETED
             │
             ▼
Mid-Project Review
Hook Audit + Data Load Test
             │
             ▼
        ✅ COMPLETED
             │
             ▼
Week 3
Synthetic Backdoor + Detection
             │
             ▼
        ✅ COMPLETED
             │
             ▼
Week 4
PDF Reporting + Deep-Dive UI
             │
             ▼
          ⏳ PENDING
             │
             ▼
Final Review
             │
             ▼
          ⏳ PENDING
```

---

# 19. Ethical & Authorized Use

NeuroFence is intended for:

* AI security research
* Model forensics
* Defensive security testing
* AI safety research
* Educational purposes
* Authorized enterprise model verification

Only analyze models and systems that you own or have explicit permission to test.

---

# 20. Final Project Objective

The final objective of NeuroFence is to provide an **offline AI model-forensics workstation** capable of investigating suspicious activation behavior inside locally deployed LLMs.

The completed system will combine:

```text
Secure Model Loading
        +
PyTorch Activation Tracking
        +
Adversarial Fuzzing
        +
Statistical Analysis
        +
Synthetic Backdoor Validation
        +
Neuron Visualization
        +
Forensic Reporting
```

This approach moves AI security analysis beyond conventional network and application-layer inspection toward the **internal mathematical behavior of neural-network models**.

---

## Project Status

**NeuroFence — Project 3**

**Domain:** AI Security (SecOps) / Model Forensics

**Current Phase:** Week 3 Completed

**Next Phase:** Week 4 — Reporting & Final Refinement

**Overall Status:** In Development
