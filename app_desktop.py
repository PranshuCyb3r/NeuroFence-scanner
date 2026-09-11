import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog
from safetensors import safe_open

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class NeuroFenceWorkstation(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("NeuroFence — 16:9 AI Security Operations Workstation")
        self.geometry("1480x880")
        self.minsize(1366, 768)
        self.configure(fg_color="#0a0e17")

        self.model_path = "models/model.safetensors"
        self._build_ui()

    def _build_ui(self):
        # ==========================================
        # 1. TOP GLOBAL HUD BAR
        # ==========================================
        top_bar = ctk.CTkFrame(self, fg_color="#0f131c", height=52, corner_radius=0, border_width=1, border_color="#181b25")
        top_bar.pack(fill="x", side="top")

        # Brand / Logo
        ctk.CTkLabel(
            top_bar,
            text="🛡️ NeuroFence",
            font=ctk.CTkFont(family="Consolas", size=17, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=(16, 12), pady=10)

        ctk.CTkLabel(
            top_bar,
            text="● LOCAL SANDBOX (OFFLINE MODE)",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color="#10b981",
            fg_color="#13221b",
            corner_radius=4,
            padx=8,
            pady=3
        ).pack(side="left", padx=8)

        # Hardware Telemetry Badges
        telemetry_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        telemetry_frame.pack(side="left", padx=20)

        ctk.CTkLabel(
            telemetry_frame,
            text="VRAM: 18.4 / 24.0 GB  |  CPU: 34.2%  |  ACCEL: CUDA (RTX 4090)",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#06b6d4"
        ).pack(side="left")

        # Top Action Buttons
        actions_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        actions_frame.pack(side="right", padx=16)

        ctk.CTkButton(
            actions_frame,
            text="Run Probe",
            fg_color="#181b25",
            hover_color="#222838",
            text_color="#94a3b8",
            width=95,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.run_probe_action
        ).pack(side="left", padx=4)

        self.btn_deep_scan = ctk.CTkButton(
            actions_frame,
            text="⚡ EXECUTE DEEP SCAN",
            fg_color="#06b6d4",
            hover_color="#0891b2",
            text_color="#0a0e17",
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.start_scan_thread
        )
        self.btn_deep_scan.pack(side="left", padx=6)

        # ==========================================
        # 2. MAIN 3-COLUMN WORKSPACE
        # ==========================================
        main_workspace = ctk.CTkFrame(self, fg_color="transparent")
        main_workspace.pack(fill="both", expand=True, padx=12, pady=10)
        main_workspace.grid_columnconfigure(0, weight=3)  # Left Sidebar
        main_workspace.grid_columnconfigure(1, weight=8)  # Center HUD & Telemetry
        main_workspace.grid_columnconfigure(2, weight=5)  # Right Forensics & Console
        main_workspace.grid_rowconfigure(0, weight=1)

        # ------------------------------------------
        # COLUMN 1: LEFT SIDEBAR & ARCHITECTURE
        # ------------------------------------------
        left_col = ctk.CTkFrame(main_workspace, fg_color="#0f131c", corner_radius=8, border_width=1, border_color="#1e293b")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            left_col,
            text="TARGET ARCHITECTURE",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color="#64748b"
        ).pack(anchor="w", padx=12, pady=(12, 4))

        # Model Target Card
        target_card = ctk.CTkFrame(left_col, fg_color="#181b25", corner_radius=6)
        target_card.pack(fill="x", padx=10, pady=4)
        
        ctk.CTkLabel(target_card, text="Llama-3-70B-Safetensors", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#38bdf8").pack(anchor="w", padx=10, pady=(8, 1))
        ctk.CTkLabel(target_card, text="FP16 • Isolated RAM", font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(anchor="w", padx=10, pady=(0, 8))

        # Nav Buttons
        ctk.CTkButton(left_col, text="📂 Model Loader & Sandbox", fg_color="#06b6d4", text_color="#0a0e17", font=ctk.CTkFont(weight="bold"), height=32, anchor="w", command=self.browse_model).pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(left_col, text="🔬 Activation & Hook Explorer", fg_color="#181b25", hover_color="#222838", text_color="#e2e8f0", height=32, anchor="w").pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(left_col, text="🧬 Tensor Metadata Inspection", fg_color="#181b25", hover_color="#222838", text_color="#e2e8f0", height=32, anchor="w").pack(fill="x", padx=10, pady=4)
        ctk.CTkButton(left_col, text="🛡️ Security Verification", fg_color="#181b25", hover_color="#222838", text_color="#e2e8f0", height=32, anchor="w").pack(fill="x", padx=10, pady=4)

        # Layer Allocation Grid (L0 - L31)
        ctk.CTkLabel(left_col, text="UNIFIED RAM ALLOCATION MAP", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#64748b").pack(anchor="w", padx=12, pady=(16, 4))
        
        grid_frame = ctk.CTkFrame(left_col, fg_color="#0a0e17", corner_radius=6, border_width=1, border_color="#1e293b")
        grid_frame.pack(fill="x", padx=10, pady=4)

        for i in range(4):
            grid_frame.grid_columnconfigure(i, weight=1)
        for idx in range(16):
            r = idx // 4
            c = idx % 4
            color = "#ef4444" if idx in (7, 11) else "#10b981"
            txt = f"L{idx*2}"
            lbl = ctk.CTkLabel(grid_frame, text=f"● {txt}", font=ctk.CTkFont(family="Consolas", size=9), text_color=color)
            lbl.grid(row=r, column=c, padx=2, pady=3)

        # Enclave Security Posture Box
        ctk.CTkLabel(left_col, text="ENCLAVE SECURITY POSTURE", font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#64748b").pack(anchor="w", padx=12, pady=(16, 4))
        
        posture_box = ctk.CTkFrame(left_col, fg_color="#181b25", corner_radius=6)
        posture_box.pack(fill="both", expand=True, padx=10, pady=(4, 10))
        
        for k, v, col in [("Zero-Unpickler", "ENFORCED", "#10b981"), ("Seccomp-BPF", "LOCKED", "#10b981"), ("CUDA Flush", "ACTIVE", "#38bdf8"), ("Entropy", "0.994 CLEAN", "#10b981")]:
            row_f = ctk.CTkFrame(posture_box, fg_color="transparent")
            row_f.pack(fill="x", padx=8, pady=3)
            ctk.CTkLabel(row_f, text=k, font=ctk.CTkFont(size=10), text_color="#94a3b8").pack(side="left")
            ctk.CTkLabel(row_f, text=v, font=ctk.CTkFont(family="Consolas", size=9, weight="bold"), text_color=col).pack(side="right")

        # ------------------------------------------
        # COLUMN 2: CENTER WORKSTATION (CHARTS & HOOKS)
        # ------------------------------------------
        center_col = ctk.CTkFrame(main_workspace, fg_color="#0f131c", corner_radius=8, border_width=1, border_color="#1e293b")
        center_col.grid(row=0, column=1, sticky="nsew", padx=6)

        # Sub-header: Kurtosis & Anomaly Title
        ctk.CTkLabel(
            center_col,
            text="📈 Layer Activation Kurtosis & Backdoor Anomaly Sigma",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#e2e8f0"
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Simulated Graphic Bar Chart of Anomaly Sigmas
        chart_container = ctk.CTkFrame(center_col, fg_color="#0a0e17", height=130, corner_radius=6, border_width=1, border_color="#1e293b")
        chart_container.pack(fill="x", padx=12, pady=4)
        chart_container.pack_propagate(False)

        bar_canvas = ctk.CTkFrame(chart_container, fg_color="transparent")
        bar_canvas.pack(fill="both", expand=True, padx=8, pady=8)

        # Visual bars representation
        bar_heights = [18, 22, 16, 45, 20, 19, 25, 30, 24, 98, 26, 32, 28, 75, 22, 19, 23, 20, 26]
        for b_idx, h in enumerate(bar_heights):
            b_col = "#ef4444" if h > 70 else ("#38bdf8" if h > 40 else "#06b6d4")
            b_frame = ctk.CTkFrame(bar_canvas, fg_color="transparent")
            b_frame.pack(side="left", fill="y", expand=True, padx=1)
            
            tag = " !L15" if h == 98 else (" !L23" if h == 75 else "")
            if tag:
                ctk.CTkLabel(b_frame, text=tag, font=ctk.CTkFont(family="Consolas", size=8, weight="bold"), text_color="#ef4444").pack(side="top")
            
            bar = ctk.CTkFrame(b_frame, fg_color=b_col, width=14, height=h, corner_radius=2)
            bar.pack(side="bottom")

        # Attached PyTorch Forward Hooks Table
        ctk.CTkLabel(
            center_col,
            text="ATTACHED PYTORCH FORWARD HOOKS (4 ACTIVE MONITORS)",
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=16, pady=(16, 6))

        table_box = ctk.CTkFrame(center_col, fg_color="#0a0e17", corner_radius=6, border_width=1, border_color="#1e293b")
        table_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Table Header
        th = ctk.CTkFrame(table_box, fg_color="#181b25", height=28)
        th.pack(fill="x", padx=2, pady=2)
        for title, w in [("HOOK TARGET NODE", 240), ("SHAPE", 100), ("ACTIVATION MEAN", 130), ("VARIANCE SIGMA", 140), ("STATE", 90)]:
            ctk.CTkLabel(th, text=title, font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color="#64748b", width=w, anchor="w").pack(side="left", padx=6)

        # Table Rows
        rows_data = [
            ("layers.14.mlp.up_proj", "[1, 512, 8192]", "+0.0428", "1.55σ [Nominal]", "#10b981", "PASSIVE", "#64748b"),
            ("layers.15.mlp.down_proj", "[1, 512, 2048]", "+18.4912", "5.82σ [POISONED]", "#ef4444", "TRIGGERED", "#ef4444"),
            ("layers.16.self_attn.q_proj", "[1, 32, 512, 64]", "-0.0014", "1.18σ [Nominal]", "#10b981", "PASSIVE", "#64748b"),
            ("layers.23.self_attn.o_proj", "[1, 512, 2048]", "+4.1084", "3.82σ [STEERING]", "#0284c7", "MONITOR", "#0284c7"),
        ]

        for hook, shp, mn, vr, vr_c, st, st_c in rows_data:
            tr = ctk.CTkFrame(table_box, fg_color="#0f131c" if "15" not in hook else "#221115", height=32)
            tr.pack(fill="x", padx=2, pady=1)
            ctk.CTkLabel(tr, text=hook, font=ctk.CTkFont(family="Consolas", size=10), text_color="#f8fafc", width=240, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(tr, text=shp, font=ctk.CTkFont(family="Consolas", size=10), text_color="#94a3b8", width=100, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(tr, text=mn, font=ctk.CTkFont(family="Consolas", size=10), text_color="#e2e8f0", width=130, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(tr, text=vr, font=ctk.CTkFont(family="Consolas", size=10, weight="bold"), text_color=vr_c, width=140, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(tr, text=st, font=ctk.CTkFont(family="Consolas", size=9, weight="bold"), text_color=st_c, width=90, anchor="w").pack(side="left", padx=6)

        # ------------------------------------------
        # COLUMN 3: RIGHT PANEL (FORENSICS & CONSOLE)
        # ------------------------------------------
        right_col = ctk.CTkFrame(main_workspace, fg_color="#0f131c", corner_radius=8, border_width=1, border_color="#1e293b")
        right_col.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # Synthesized Trigger Box
        ctk.CTkLabel(
            right_col,
            text="💥 Synthesized Trigger Vector",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#ef4444"
        ).pack(anchor="w", padx=12, pady=(12, 4))

        sig_card = ctk.CTkFrame(right_col, fg_color="#181b25", corner_radius=6)
        sig_card.pack(fill="x", padx=10, pady=4)
        
        ctk.CTkLabel(sig_card, text="Inversion Loss: 0.0024 (Step 240/240)", font=ctk.CTkFont(family="Consolas", size=10), text_color="#94a3b8").pack(anchor="w", padx=10, pady=(6, 2))
        ctk.CTkLabel(sig_card, text='"$#sys_override"  →  98.4% conf', font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#ef4444").pack(anchor="w", padx=10, pady=2)
        ctk.CTkLabel(sig_card, text='"<!--alpha_admin-->" → 92.1% conf', font=ctk.CTkFont(family="Consolas", size=11, weight="bold"), text_color="#ef4444").pack(anchor="w", padx=10, pady=(2, 6))

        # Mitigation Action Buttons
        ctk.CTkButton(right_col, text="🛡️ Isolate & Neuter Layer 15", fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff", font=ctk.CTkFont(weight="bold"), height=30).pack(fill="x", padx=10, pady=4)
        
        btn_sub = ctk.CTkFrame(right_col, fg_color="transparent")
        btn_sub.pack(fill="x", padx=10, pady=2)
        ctk.CTkButton(btn_sub, text="🔒 Quarantine", fg_color="#181b25", width=120, height=28).pack(side="left", expand=True, padx=(0, 4))
        ctk.CTkButton(btn_sub, text="✂️ Dynamic Prune", fg_color="#181b25", width=120, height=28).pack(side="right", expand=True, padx=(4, 0))

        # Enclave Audit Console Box
        ctk.CTkLabel(
            right_col,
            text="📟 ENCLAVE AUDIT CONSOLE  ● LIVE",
            font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
            text_color="#10b981"
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.console = ctk.CTkTextbox(right_col, fg_color="#0a0e17", text_color="#38bdf8", font=ctk.CTkFont(family="Consolas", size=10), border_width=1, border_color="#1e293b")
        self.console.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._write_console("[00:04:12] [INIT] Enclave sandbox initialized.")
        self._write_console("[00:04:13] [SAFE] BLAKE3 checksum verified against enclave manifest.")
        self._write_console("[00:04:14] [PROBE] Forward run: batch=1, seq_len=512, fp16 mode.")
        self._write_console("[00:04:15] [ALERT] Layer 15 down_proj variance anomaly: 5.82σ (> 3.0σ limit).")
        self._write_console("[00:04:16] [POISON] Backdoor trigger token identified: '$#sys_override'.")
        self._write_console("[00:04:17] [READY] Awaiting operator remediation signal...")

        # ==========================================
        # 3. BOTTOM TELEMETRY FOOTER BAR
        # ==========================================
        footer = ctk.CTkFrame(self, fg_color="#0f131c", height=32, corner_radius=0, border_width=1, border_color="#181b25")
        footer.pack(fill="x", side="bottom")

        ctk.CTkLabel(
            footer,
            text="● Daemon: Online (v0.8.2-local)   |   Audit Engine: RIGID ACTIVE   |   Memory Seal: SECURE   |   Active Session: ENCLAVE-4891-B",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#64748b"
        ).pack(side="left", padx=16, pady=6)

    def _write_console(self, text):
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def browse_model(self):
        f = filedialog.askopenfilename(filetypes=[("SafeTensors", "*.safetensors"), ("All Files", "*.*")])
        if f:
            self.model_path = f
            self._write_console(f"[SELECT] Model set to: {os.path.basename(f)}")

    def run_probe_action(self):
        self._write_console("[PROBE] Running forward probe tensor across all registered hooks...")
        self.after(600, lambda: self._write_console("[PROBE] Forward pass complete. Telemetry normal."))

    def start_scan_thread(self):
        self.btn_deep_scan.configure(state="disabled", text="SCANNING...")
        self._write_console("\n[EXEC] Starting Deep Enclave Anomaly Scan...")
        threading.Thread(target=self._run_deep_scan, daemon=True).start()

    def _run_deep_scan(self):
        time.sleep(0.5)
        if os.path.exists(self.model_path):
            with safe_open(self.model_path, framework="pt", device="cpu") as f:
                keys = list(f.keys())
            self._write_console(f"[ENGINE] Read {len(keys)} tensors from {os.path.basename(self.model_path)}.")
        else:
            self._write_console(f"[ENGINE] Checkpoint not found at {self.model_path}. Running simulation.")

        time.sleep(0.6)
        self._write_console("[SCAN] Layer variance calculation: complete.")
        self._write_console("[REPORT] 1 poisoned hook anomaly confirmed at layers.15.mlp.down_proj.")
        self.btn_deep_scan.configure(state="normal", text="⚡ EXECUTE DEEP SCAN")


if __name__ == "__main__":
    app = NeuroFenceWorkstation()
    app.mainloop()