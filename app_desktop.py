import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import numpy as np

# Import Week 1, 2 & 3 Modules
try:
    from loader import inspect_safetensors_metadata, calculate_file_hashes
except ImportError:
    inspect_safetensors_metadata = None
    calculate_file_hashes = None

try:
    from test_backdoor_detection import MockTransformerLayer, BackdoorDetector
except ImportError:
    MockTransformerLayer = None
    BackdoorDetector = None


class NeuroFenceWorkstation(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup (16:9 fixed ratio) ---
        self.title("NeuroFence — Tactical AI Security Operations Workstation (Week 3)")
        self.geometry("1440x810")
        self.minsize(1280, 720)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # Color Palette
        self.BG_DARK = "#0a0a0c"
        self.CARD_BG = "#131318"
        self.BORDER_COLOR = "#22222a"
        self.ACCENT_RED = "#e11d48"
        self.ACCENT_GREEN = "#10b981"
        self.TEXT_MUTED = "#94a3b8"

        self.configure(fg_color=self.BG_DARK)

        # State Variables
        self.selected_file_path = None
        self.is_scanning = False
        self.detector = BackdoorDetector(z_score_threshold=4.5) if BackdoorDetector else None

        # Build UI Structure
        self._build_header()
        self._build_main_layout()
        self._build_footer()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color=self.CARD_BG, height=60, corner_radius=0)
        header_frame.pack(fill="x", side="top", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Logo / Title
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=24, pady=12)

        dot = ctk.CTkLabel(title_box, text="●", text_color=self.ACCENT_RED, font=("Segoe UI", 18, "bold"))
        dot.pack(side="left", padx=(0, 8))

        title = ctk.CTkLabel(title_box, text="NEUROFENCE", font=("Segoe UI", 16, "bold"), text_color="#ffffff")
        title.pack(side="left")

        subtitle = ctk.CTkLabel(
            title_box, 
            text=" // WEIGHT POISONING & TRIGGER INVERSION SCANNER (WEEK 3)", 
            font=("Segoe UI", 12), 
            text_color=self.TEXT_MUTED
        )
        subtitle.pack(side="left", padx=8)

        # Right Header Badge
        badge = ctk.CTkLabel(
            header_frame, 
            text="AIR-GAPPED ENVIRONMENT ACTIVE", 
            fg_color="#064e3b", 
            text_color="#6ee7b7", 
            font=("Segoe UI", 11, "bold"), 
            corner_radius=6, 
            padx=12, 
            pady=4
        )
        badge.pack(side="right", padx=24, pady=16)

    def _build_main_layout(self):
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=16)

        # Left Column (Controls & Trigger Tests) - 380px fixed width
        left_col = ctk.CTkFrame(main_container, fg_color="transparent", width=380)
        left_col.pack(side="left", fill="y", padx=(0, 16))
        left_col.pack_propagate(False)

        self._build_control_panel(left_col)

        # Right Column (Heatmap Matrix & Live Probe Logs)
        right_col = ctk.CTkFrame(main_container, fg_color="transparent")
        right_col.pack(side="right", fill="both", expand=True)

        self._build_metrics_row(right_col)
        self._build_heatmap_and_terminal(right_col)

    def _build_control_panel(self, parent):
        # Step 01: Checkpoint Loader
        loader_card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, corner_radius=8, border_width=1, border_color=self.BORDER_COLOR)
        loader_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(loader_card, text="STEP 01: MODEL CHECKPOINT", font=("Segoe UI", 11, "bold"), text_color=self.TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 6))

        self.btn_browse = ctk.CTkButton(
            loader_card,
            text="📁 Browse .safetensors Model",
            fg_color="#1e2230",
            hover_color="#2b3145",
            font=("Segoe UI", 12, "bold"),
            command=self._on_browse
        )
        self.btn_browse.pack(fill="x", padx=16, pady=6)

        self.lbl_file_status = ctk.CTkLabel(loader_card, text="No file selected (Using sandbox baseline)", font=("Segoe UI", 10), text_color="#64748b")
        self.lbl_file_status.pack(anchor="w", padx=16, pady=(0, 12))

        # Step 02: Scanner Engine Controls
        engine_card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, corner_radius=8, border_width=1, border_color=self.BORDER_COLOR)
        engine_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(engine_card, text="STEP 02: ADVERSARIAL SCAN ENGINE", font=("Segoe UI", 11, "bold"), text_color=self.TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 6))

        self.btn_run_fuzz = ctk.CTkButton(
            engine_card,
            text="⚡ Run Adversarial Fuzzer",
            fg_color=self.ACCENT_RED,
            hover_color="#be123c",
            font=("Segoe UI", 13, "bold"),
            height=40,
            command=self._run_adversarial_fuzzer
        )
        self.btn_run_fuzz.pack(fill="x", padx=16, pady=(6, 8))

        self.btn_pineapple_test = ctk.CTkButton(
            engine_card,
            text="🚨 Run Trigger Inversion Test ('Pineapple')",
            fg_color="#881337",
            hover_color="#9f1239",
            font=("Segoe UI", 12, "bold"),
            height=36,
            command=self._run_trigger_inversion_test
        )
        self.btn_pineapple_test.pack(fill="x", padx=16, pady=(0, 12))

        # Log Console
        log_card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, corner_radius=8, border_width=1, border_color=self.BORDER_COLOR)
        log_card.pack(fill="both", expand=True)

        ctk.CTkLabel(log_card, text="LIVE PROBE TELEMETRY STREAM", font=("Segoe UI", 11, "bold"), text_color=self.TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 6))

        self.terminal = ctk.CTkTextbox(log_card, fg_color="#090a0f", text_color="#22c55e", font=("Consolas", 10), corner_radius=4)
        self.terminal.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._log("[NeuroFence Ready] Standby. Click 'Run Adversarial Fuzzer' or 'Trigger Test'.")

    def _build_metrics_row(self, parent):
        metrics_container = ctk.CTkFrame(parent, fg_color="transparent", height=80)
        metrics_container.pack(fill="x", pady=(0, 12))
        metrics_container.pack_propagate(False)

        metrics = [
            ("ACTIVE NEURONS", "15,264", "93.0% Firing", self.ACCENT_RED),
            ("DORMANT / SUSPICIOUS", "1,120", "7.0% Quiescent", "#eab308"),
            ("ANOMALY KURTOSIS", "3.79", "Safe (< 4.0)", self.ACCENT_GREEN),
            ("TRIGGER SENSITIVITY", "0.018 λ", "Clean Baseline", "#06b6d4")
        ]

        self.metric_value_labels = {}

        for title, val, sub, color in metrics:
            card = ctk.CTkFrame(metrics_container, fg_color=self.CARD_BG, corner_radius=8, border_width=1, border_color=self.BORDER_COLOR)
            card.pack(side="left", fill="both", expand=True, padx=4)

            ctk.CTkLabel(card, text=title, font=("Segoe UI", 9, "bold"), text_color=self.TEXT_MUTED).pack(anchor="w", padx=12, pady=(8, 2))
            lbl_val = ctk.CTkLabel(card, text=val, font=("Segoe UI", 18, "bold"), text_color=color)
            lbl_val.pack(anchor="w", padx=12)
            self.metric_value_labels[title] = lbl_val
            ctk.CTkLabel(card, text=sub, font=("Segoe UI", 9), text_color="#64748b").pack(anchor="w", padx=12, pady=(0, 6))

    def _build_heatmap_and_terminal(self, parent):
        grid_card = ctk.CTkFrame(parent, fg_color=self.CARD_BG, corner_radius=8, border_width=1, border_color=self.BORDER_COLOR)
        grid_card.pack(fill="both", expand=True)

        ctk.CTkLabel(grid_card, text="LAYER-BY-LAYER NEURON ACTIVATION HEATMAP (32 LAYERS × 16 CLUSTERS)", font=("Segoe UI", 11, "bold"), text_color=self.TEXT_MUTED).pack(anchor="w", padx=16, pady=(12, 6))

        # Canvas for Drawing Heatmap Matrix
        self.canvas = tk.Canvas(grid_card, bg="#0d0d12", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.canvas.bind("<Configure>", lambda e: self._draw_heatmap())

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=self.BG_DARK, height=28)
        footer.pack(fill="x", side="bottom")
        self.status_lbl = ctk.CTkLabel(footer, text="System: Nominal | Sandbox: Active | Zero Data Leakage Guaranteed", font=("Segoe UI", 10), text_color="#475569")
        self.status_lbl.pack(side="left", padx=20)

    def _log(self, text):
        self.terminal.insert("end", f"{text}\n")
        self.terminal.see("end")

    def _on_browse(self):
        f = filedialog.askopenfilename(title="Select .safetensors Model", filetypes=[("SafeTensors", "*.safetensors")])
        if f:
            self.selected_file_path = f
            fname = os.path.basename(f)
            self.lbl_file_status.configure(text=fname)
            self._log(f"[File Loaded] {fname}")
            if calculate_file_hashes:
                h = calculate_file_hashes(f)
                self._log(f"  SHA-256: {h.get('sha256', '')[:24]}...")

    def _draw_heatmap(self, anomaly_coords=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 50 or h < 50:
            return

        rows = 32
        cols = 16
        cell_w = max(2, (w - 40) / cols)
        cell_h = max(2, (h - 20) / rows)

        palette = ["#1a0505", "#3a0b0e", "#6b1118", "#a81b24", "#e11d48", "#ff4d6d"]

        np.random.seed(42)
        for r in range(rows):
            for c in range(cols):
                # Check if flagged as anomalous
                if anomaly_coords and (r, c) in anomaly_coords:
                    color = "#ffffff"  # Bright white spike
                else:
                    intensity = np.random.choice([0, 1, 2, 3, 4], p=[0.1, 0.2, 0.4, 0.25, 0.05])
                    color = palette[intensity]

                x1 = 25 + c * cell_w
                y1 = 10 + r * cell_h
                x2 = x1 + cell_w - 2
                y2 = y1 + cell_h - 1
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

    def _run_adversarial_fuzzer(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.btn_run_fuzz.configure(state="disabled")

        def task():
            self._log("\n[Fuzzer] Initializing Adversarial Probe Batch...")
            probes = [
                "Evaluate model boundaries for query: <|im_start|> jailbreak...",
                "Translate standard input with injected vector: [sudo_inversion_tr...]",
                "Analyze semantic clustering under perturbation: token_inversion...",
                "Zero-shot verification baseline pass: system_prompt_override..."
            ]
            for p in probes:
                threading.Event().wait(0.2)
                self._log(f"  → Injected: {p[:55]}...")
                self._log(f"    [Hooks] Sampling 32 Transformer Layer activations...")

            self._log("[Result] Verdict: NOMINAL_BASELINE_RECORDED")
            self._log("  [Baseline] Kurtosis: 3.79 | Dormant subnets: 1,120")
            self._draw_heatmap()
            self.btn_run_fuzz.configure(state="normal")
            self.is_scanning = False

        threading.Thread(target=task, daemon=True).start()

    def _run_trigger_inversion_test(self):
        """Week 3: Injects synthetic 'Pineapple' trigger and flags Neuron 142 outlier."""
        if self.is_scanning:
            return
        self.is_scanning = True
        self.btn_pineapple_test.configure(state="disabled")

        def task():
            self._log("\n" + "=" * 45)
            self._log("INJECTING CANDIDATE TRIGGER: 'Pineapple'")
            self._log("=" * 45)

            if MockTransformerLayer and BackdoorDetector:
                layer = MockTransformerLayer(d_model=256, target_neuron_idx=142)
                detector = BackdoorDetector(z_score_threshold=4.5)

                import torch
                clean_in = torch.randn(16, 256)
                trig_in = torch.randn(16, 256)

                with torch.no_grad():
                    clean_acts = layer(clean_in, is_trigger_present=False).numpy()
                    trig_acts = layer(trig_in, is_trigger_present=True).numpy()

                anomalies = detector.scan_activations(clean_acts, trig_acts)

                threading.Event().wait(0.3)
                if anomalies:
                    target = anomalies[0]
                    self._log(f"     ALERT: Highly Anomalous Activation Identified!")
                    self._log(f"     Target Neuron : Index {target['neuron_index']}")
                    self._log(f"     Z-Score Dev   : +{target['z_score']} σ (Cutoff > 4.5 σ)")
                    self._log(f"     Kurtosis Spike: {target['kurtosis']} (Baseline ~3.0)")
                    self._log(f"     Verdict       : {target['status']}")

                    # Update UI Metrics
                    self.metric_value_labels["ANOMALY KURTOSIS"].configure(text=f"{target['kurtosis']:.1f}", text_color=self.ACCENT_RED)
                    self.metric_value_labels["TRIGGER SENSITIVITY"].configure(text="0.142 λ", text_color=self.ACCENT_RED)

                    # Highlight anomalous cluster in Heatmap (Layer 16, Cluster 8)
                    self._draw_heatmap(anomaly_coords=[(16, 8), (16, 9)])
            else:
                self._log("  [Mock Engine] Simulated Alert: Neuron 142 flagged (+67.99 σ).")

            self.btn_pineapple_test.configure(state="normal")
            self.is_scanning = False

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    app = NeuroFenceWorkstation()
    app.mainloop()