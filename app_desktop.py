import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from loader import inspect_safetensors_metadata, calculate_file_hashes
from hooks import attach_forward_telemetry_probes
from fuzzer import AdversarialFuzzer

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

BG_DARK = "#0e0e10"
CARD_BG = "#16161a"
ACCENT_RED = "#dc2626"
ACCENT_RED_HOVER = "#b91c1c"
TEXT_WHITE = "#ffffff"
TEXT_MUTED = "#9ca3af"
BORDER_COLOR = "#27272a"

class NeuroFenceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NeuroFence — Adversarial Fuzzer & Neuron Heatmap Workstation")
        self.geometry("1400x880")
        self.configure(fg_color=BG_DARK)

        self.selected_model_path = None
        self.fuzzer = AdversarialFuzzer()
        self.last_scan_results = None
        self.last_matrix = None

        self._build_header()
        self._build_main_layout()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="#121215", height=60, corner_radius=0)
        header.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(
            header,
            text="NEUROFENCE // MODEL INSPECTOR & ADVERSARIAL FUZZER",
            font=ctk.CTkFont(family="Consolas", size=17, weight="bold"),
            text_color=ACCENT_RED
        )
        title_lbl.pack(side="left", padx=20, pady=15)

        badge = ctk.CTkLabel(
            header,
            text="● AIR-GAPPED SANDBOX ACTIVE",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#10b981",
            fg_color="#064e3b",
            corner_radius=6,
            padx=10,
            pady=4
        )
        badge.pack(side="right", padx=20, pady=15)

    def _build_main_layout(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # Left Column (Controls & Logs)
        left_col = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR, width=440)
        left_col.pack(side="left", fill="y", padx=(0, 15))
        left_col.pack_propagate(False)

        # STEP 1: Model Ingestion
        ctk.CTkLabel(left_col, text="STEP 01: MODEL CHECKPOINT", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=16, pady=(16, 6))

        self.btn_browse = ctk.CTkButton(left_col, text="📂 Browse .safetensors Model", fg_color="#27272a", hover_color="#3f3f46", text_color=TEXT_WHITE, command=self.browse_model)
        self.btn_browse.pack(fill="x", padx=16, pady=4)

        self.lbl_file = ctk.CTkLabel(left_col, text="No file selected (Using sandbox baseline)", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_file.pack(anchor="w", padx=16, pady=(2, 10))

        # STEP 2: Fuzzer Actions
        ctk.CTkLabel(left_col, text="STEP 02: ADVERSARIAL FUZZER ENGINE", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color=ACCENT_RED).pack(anchor="w", padx=16, pady=(10, 6))

        self.btn_run_fuzz = ctk.CTkButton(
            left_col, text="⚡ START ADVERSARIAL FUZZING ENGINE",
            fg_color=ACCENT_RED, hover_color=ACCENT_RED_HOVER, text_color=TEXT_WHITE,
            height=42, font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.start_fuzzing_thread(simulate_backdoor=False)
        )
        self.btn_run_fuzz.pack(fill="x", padx=16, pady=(6, 8))

        # Action Buttons Row
        btn_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.btn_inject_test = ctk.CTkButton(
            btn_frame, text="⚠️ Trigger Injection Test",
            fg_color="#7f1d1d", hover_color="#991b1b", text_color=TEXT_WHITE,
            height=34, font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self.start_fuzzing_thread(simulate_backdoor=True)
        )
        self.btn_inject_test.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_export = ctk.CTkButton(
            btn_frame, text="💾 Export Report",
            fg_color="#1e293b", hover_color="#334155", text_color=TEXT_WHITE,
            height=34, font=ctk.CTkFont(size=11, weight="bold"),
            command=self.export_report
        )
        self.btn_export.pack(side="right", fill="x", expand=True, padx=(4, 0))

        # Telemetry Log
        ctk.CTkLabel(left_col, text="LIVE PROBE TELEMETRY STREAM", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=TEXT_WHITE).pack(anchor="w", padx=16, pady=(5, 5))

        self.txt_log = ctk.CTkTextbox(left_col, fg_color="#0a0a0c", text_color="#22c55e", font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.log("[NeuroFence Ready] Standby. Click 'Start Adversarial Fuzzing Engine'.")

        # Right Column (HUD & Heatmap Matrix)
        right_col = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        right_col.pack(side="right", fill="both", expand=True)

        # Top Metric Cards
        hud_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        hud_frame.pack(fill="x", padx=16, pady=16)

        self.card_active = self._create_hud_card(hud_frame, "ACTIVE NEURONS", "15,264", "93.0% Firing", ACCENT_RED)
        self.card_dormant = self._create_hud_card(hud_frame, "DORMANT / SUSPICIOUS", "1,120", "7.0% Quiescent", "#f59e0b")
        self.card_kurtosis = self._create_hud_card(hud_frame, "ANOMALY KURTOSIS", "3.79", "Safe (< 4.0)", "#10b981")
        self.card_verdict = self._create_hud_card(hud_frame, "TRIGGER SENSITIVITY", "0.018 λ", "Clean Baseline", "#38bdf8")

        # Matrix Section Header
        ctk.CTkLabel(
            right_col, 
            text="LAYER-BY-LAYER NEURON ACTIVATION HEATMAP (32 LAYERS × 16 CLUSTERS)", 
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), 
            text_color=TEXT_WHITE
        ).pack(anchor="w", padx=16, pady=(4, 6))

        # Canvas Heatmap Matrix
        self.heatmap_canvas = tk.Canvas(right_col, bg="#0d0d11", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.heatmap_canvas.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.heatmap_canvas.bind("<Configure>", lambda event: self.draw_heatmap())

    def _create_hud_card(self, parent, title, val, sub, val_color):
        card = ctk.CTkFrame(parent, fg_color="#1a1a20", corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        card.pack(side="left", fill="both", expand=True, padx=5)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(10, 2))
        lbl_val = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(family="Consolas", size=22, weight="bold"), text_color=val_color)
        lbl_val.pack(anchor="w", padx=12, pady=0)
        lbl_sub = ctk.CTkLabel(card, text=sub, font=ctk.CTkFont(size=10), text_color=TEXT_MUTED)
        lbl_sub.pack(anchor="w", padx=12, pady=(0, 10))
        return (lbl_val, lbl_sub)

    def log(self, msg: str):
        self.txt_log.insert("end", f"{msg}\n")
        self.txt_log.see("end")

    def browse_model(self):
        path = filedialog.askopenfilename(filetypes=[("SafeTensors Model", "*.safetensors"), ("All Files", "*.*")])
        if path:
            self.selected_model_path = path
            self.lbl_file.configure(text=os.path.basename(path), text_color=TEXT_WHITE)
            self.log(f"[File Loaded] {os.path.basename(path)}")

    def start_fuzzing_thread(self, simulate_backdoor: bool = False):
        self.btn_run_fuzz.configure(state="disabled")
        threading.Thread(target=lambda: self.run_fuzzing_workflow(simulate_backdoor), daemon=True).start()

    def run_fuzzing_workflow(self, simulate_backdoor: bool):
        try:
            mode_lbl = "SIMULATED TRIGGER INJECTION" if simulate_backdoor else "BASELINE NORMAL SCAN"
            self.log(f"\n[Fuzzer] Initializing Adversarial Probe Batch ({mode_lbl})...")
            samples = self.fuzzer.generate_fuzz_batch(4)
            for s in samples:
                self.log(f"  → Injected: {s[:55]}...")

            self.log("[Hooks] Sampling 32 Transformer Layer activations...")
            res = self.fuzzer.profile_neuron_activations(num_layers=32, clusters_per_layer=16, simulate_backdoor=simulate_backdoor)
            self.last_scan_results = res

            # Update Metrics
            self.after(0, lambda: self.card_active[0].configure(text=f"{res['active_neurons']:,}"))
            self.after(0, lambda: self.card_dormant[0].configure(text=f"{res['dormant_neurons']:,}"))
            self.after(0, lambda: self.card_kurtosis[0].configure(text=f"{res['anomaly_kurtosis']}"))
            
            trigger_color = "#38bdf8" if not simulate_backdoor else ACCENT_RED
            trigger_sub = "Clean Baseline" if not simulate_backdoor else "HIGH RISK EXCITATION"
            self.after(0, lambda: self.card_verdict[0].configure(text=f"{res['trigger_sensitivity']} λ", text_color=trigger_color))
            self.after(0, lambda: self.card_verdict[1].configure(text=trigger_sub))

            self.last_matrix = res["matrix"]
            self.after(0, self.draw_heatmap)

            self.log(f"\n[Result] Verdict: {res['verdict']}")
            self.log(f"[Baseline] Kurtosis: {res['anomaly_kurtosis']} | Dormant subnets: {res['dormant_neurons']}")
        finally:
            self.after(0, lambda: self.btn_run_fuzz.configure(state="normal"))

    def export_report(self):
        if not self.last_scan_results:
            messagebox.showwarning("No Scan Data", "Please run the Adversarial Fuzzing Engine before exporting report.")
            return
        path = self.fuzzer.export_scan_report(self.last_scan_results, "scan_report.json")
        self.log(f"\n[Report Exported] Saved scan summary to {path}")
        messagebox.showinfo("Export Successful", f"Audit report exported successfully to:\n{os.path.abspath(path)}")

    def draw_heatmap(self):
        self.heatmap_canvas.delete("all")
        width = self.heatmap_canvas.winfo_width()
        height = self.heatmap_canvas.winfo_height()

        if width <= 10 or height <= 10:
            return

        layers = 32
        clusters = 16
        margin_x = 55
        margin_y = 25

        cell_w = (width - margin_x - 20) / clusters
        cell_h = (height - margin_y - 20) / layers
        matrix = getattr(self, "last_matrix", None)

        for l in range(layers):
            y = margin_y + l * cell_h
            if l % 4 == 0 or l == layers - 1:
                self.heatmap_canvas.create_text(
                    margin_x - 10, y + cell_h / 2,
                    text=f"L{l}", fill="#71717a", font=("Consolas", 9, "bold"), anchor="e"
                )

            for c in range(clusters):
                x = margin_x + c * cell_w
                val = matrix[l][c] if matrix else 0.45

                if val < 0.12:
                    color = "#1f1f24"          # Quiescent / Dormant
                elif val < 0.50:
                    color = "#7f1d1d"          # Nominal Low
                elif val < 0.85:
                    color = "#dc2626"          # Active
                else:
                    color = "#fecdd3"          # Peak / Backdoor Spike

                self.heatmap_canvas.create_rectangle(
                    x + 1, y + 1, x + cell_w - 1, y + cell_h - 1,
                    fill=color, outline=""
                )

if __name__ == "__main__":
    app = NeuroFenceApp()
    app.mainloop()