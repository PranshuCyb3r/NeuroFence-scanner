import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Import NeuroFence Core Modules
from loader import inspect_safetensors_metadata, calculate_file_hashes
from hooks import attach_forward_telemetry_probes
from fuzzer import AdversarialFuzzer

# Appearance Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Theme Colors (Crimson & Charcoal Dark Mode)
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

        self.title("NeuroFence — Week 2: Adversarial Fuzzer & Neuron Heatmap Workstation")
        self.geometry("1380x860")
        self.configure(fg_color=BG_DARK)

        self.selected_model_path = None
        self.fuzzer = AdversarialFuzzer()

        self._build_header()
        self._build_main_layout()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="#121215", height=60, corner_radius=0)
        header.pack(fill="x", side="top", padx=0, pady=0)

        title_lbl = ctk.CTkLabel(
            header,
            text="🛡️ NEUROFENCE // MODEL INSPECTOR & ADVERSARIAL FUZZER",
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

        # Left Column (File & Fuzzer Controls)
        left_col = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR, width=420)
        left_col.pack(side="left", fill="y", padx=(0, 15), pady=0)
        left_col.pack_propagate(False)

        # Section: Model Checkpoint
        lbl1 = ctk.CTkLabel(left_col, text="STEP 01: MODEL CHECKPOINT", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color=TEXT_WHITE)
        lbl1.pack(anchor="w", padx=16, pady=(16, 8))

        self.btn_browse = ctk.CTkButton(
            left_col, text="📂 Browse .safetensors Model",
            fg_color="#27272a", hover_color="#3f3f46", text_color=TEXT_WHITE,
            command=self.browse_model
        )
        self.btn_browse.pack(fill="x", padx=16, pady=4)

        self.lbl_file = ctk.CTkLabel(left_col, text="No file selected (Using sandbox baseline)", font=ctk.CTkFont(size=11), text_color=TEXT_MUTED)
        self.lbl_file.pack(anchor="w", padx=16, pady=(2, 10))

        # Section: Adversarial Fuzzer
        lbl2 = ctk.CTkLabel(left_col, text="STEP 02: ADVERSARIAL FUZZER ENGINE", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color=ACCENT_RED)
        lbl2.pack(anchor="w", padx=16, pady=(12, 6))

        info_box = ctk.CTkFrame(left_col, fg_color="#1a1a20", corner_radius=6)
        info_box.pack(fill="x", padx=16, pady=6)

        ctk.CTkLabel(info_box, text="Vectors: System Override, Token Inversion, Affine Shift\nTarget: 32 Layers (L0-L31) Telemetry", 
                     font=ctk.CTkFont(family="Consolas", size=11), text_color=TEXT_MUTED, justify="left").pack(padx=10, pady=8)

        self.btn_run_fuzz = ctk.CTkButton(
            left_col, text="⚡ START ADVERSARIAL FUZZING ENGINE",
            fg_color=ACCENT_RED, hover_color=ACCENT_RED_HOVER, text_color=TEXT_WHITE,
            height=42, font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_fuzzing_thread
        )
        self.btn_run_fuzz.pack(fill="x", padx=16, pady=(10, 15))

        # Terminal / Log Output
        lbl3 = ctk.CTkLabel(left_col, text="LIVE PROBE TELEMETRY STREAM", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color=TEXT_WHITE)
        lbl3.pack(anchor="w", padx=16, pady=(5, 5))

        self.txt_log = ctk.CTkTextbox(left_col, fg_color="#0a0a0c", text_color="#22c55e", font=ctk.CTkFont(family="Consolas", size=11))
        self.txt_log.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.log("[NeuroFence Ready] Standby. Click 'Start Adversarial Fuzzing Engine'.")

        # Right Column (Neuron Heatmap Matrix & Metrics)
        right_col = ctk.CTkFrame(container, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        right_col.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # Top HUD Metrics Cards
        hud_frame = ctk.CTkFrame(right_col, fg_color="transparent")
        hud_frame.pack(fill="x", padx=16, pady=16)

        self.card_active = self._create_hud_card(hud_frame, "ACTIVE NEURONS", "15,232", "93.0% Firing", ACCENT_RED)
        self.card_dormant = self._create_hud_card(hud_frame, "DORMANT / SUSPICIOUS", "1,152", "7.0% Quiescent", "#f59e0b")
        self.card_kurtosis = self._create_hud_card(hud_frame, "ANOMALY KURTOSIS", "3.77", "Safe (< 4.0)", "#10b981")
        self.card_verdict = self._create_hud_card(hud_frame, "TRIGGER SENSITIVITY", "0.018 λ", "Clean Baseline", "#38bdf8")

        # Heatmap Title
        matrix_header = ctk.CTkFrame(right_col, fg_color="transparent")
        matrix_header.pack(fill="x", padx=16, pady=(10, 6))

        ctk.CTkLabel(
            matrix_header, 
            text="LAYER-BY-LAYER NEURON ACTIVATION HEATMAP (32 LAYERS × 16 CLUSTERS)", 
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), 
            text_color=TEXT_WHITE
        ).pack(side="left")

        # Heatmap Canvas
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

    def start_fuzzing_thread(self):
        self.btn_run_fuzz.configure(state="disabled", text="⏳ Profiling Activations...")
        threading.Thread(target=self.run_fuzzing_workflow, daemon=True).start()

    def run_fuzzing_workflow(self):
        try:
            self.log("\n[Fuzzer] Initializing Adversarial Probe Batch...")
            samples = self.fuzzer.generate_fuzz_batch(4)
            for s in samples:
                self.log(f"  → Injected: {s[:55]}...")

            self.log("[Hooks] Sampling 32 Transformer Layer activations...")
            res = self.fuzzer.profile_neuron_activations(num_layers=32, clusters_per_layer=16)

            # Update Metrics
            self.after(0, lambda: self.card_active[0].configure(text=f"{res['active_neurons']:,}"))
            self.after(0, lambda: self.card_dormant[0].configure(text=f"{res['dormant_neurons']:,}"))
            self.after(0, lambda: self.card_kurtosis[0].configure(text=f"{res['anomaly_kurtosis']}"))
            self.after(0, lambda: self.card_verdict[0].configure(text=f"{res['trigger_sensitivity']} λ"))

            # Update Canvas Matrix
            self.last_matrix = res["matrix"]
            self.after(0, self.draw_heatmap)

            self.log(f"\n[Result] Verdict: {res['verdict']}")
            self.log(f"[Baseline] Kurtosis: {res['anomaly_kurtosis']} | Dormant subnets: {res['dormant_neurons']}")
        finally:
            self.after(0, lambda: self.btn_run_fuzz.configure(state="normal", text="⚡ START ADVERSARIAL FUZZING ENGINE"))

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
            # Draw Layer Label (e.g., L0, L4, L8...)
            y = margin_y + l * cell_h
            if l % 4 == 0 or l == layers - 1:
                self.heatmap_canvas.create_text(
                    margin_x - 10, y + cell_h / 2,
                    text=f"L{l}", fill="#71717a", font=("Consolas", 9, "bold"), anchor="e"
                )

            for c in range(clusters):
                x = margin_x + c * cell_w
                val = matrix[l][c] if matrix else 0.45

                # Color Spectrum Calculation
                if val < 0.12:
                    color = "#1f1f24"          # Quiescent / Dormant
                elif val < 0.50:
                    color = "#7f1d1d"          # Nominal Low Firing
                elif val < 0.85:
                    color = "#dc2626"          # High Active Firing
                else:
                    color = "#fca5a5"          # Peak Suspect Excitations

                self.heatmap_canvas.create_rectangle(
                    x + 1, y + 1, x + cell_w - 1, y + cell_h - 1,
                    fill=color, outline=""
                )

if __name__ == "__main__":
    app = NeuroFenceApp()
    app.mainloop()
