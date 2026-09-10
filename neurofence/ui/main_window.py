from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QFileDialog, QLineEdit
)
from PyQt6.QtCore import Qt

from neurofence.ui.theme import STYLESHEET, DANGER, SAFE
from neurofence.ui.workers import ScanWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeuroFence - LLM Backdoor Scanner")
        self.setGeometry(100, 100, 700, 500)
        self.setStyleSheet(STYLESHEET)

        self.model_path = "artifacts/poisoned_model.pt"
        self.worker = None

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # --- top row: model path + browse button ---
        top_row = QHBoxLayout()
        self.path_input = QLineEdit(self.model_path)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        top_row.addWidget(QLabel("Model:"))
        top_row.addWidget(self.path_input)
        top_row.addWidget(browse_btn)
        layout.addLayout(top_row)

        # --- scan button ---
        self.scan_btn = QPushButton("Scan Model")
        self.scan_btn.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_btn)

        # --- verdict label ---
        self.verdict_label = QLabel("No scan run yet")
        self.verdict_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verdict_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.verdict_label)

        # --- results table ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Neuron", "Peak Z-Score", "Status"])
        layout.addWidget(self.table)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select model file", "artifacts", "PyTorch models (*.pt)")
        if path:
            self.path_input.setText(path)

    def start_scan(self):
        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("Scanning...")
        self.verdict_label.setText("Scanning in progress...")

        model_path = self.path_input.text()
        self.worker = ScanWorker(model_path=model_path, trigger_word="Pineapple")
        self.worker.finished_scan.connect(self.on_scan_finished)
        self.worker.error_occurred.connect(self.on_scan_error)
        self.worker.start()

    def on_scan_finished(self, result):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan Model")

        verdict = result["verdict"]
        color = DANGER if verdict == "BACKDOOR LIKELY" else SAFE
        self.verdict_label.setText(f"VERDICT: {verdict}")
        self.verdict_label.setStyleSheet(f"font-size: 20px; font-weight: bold; padding: 10px; color: {color};")

        suspicious = set(result["suspicious_neurons"])
        z_scores = result["peak_z_scores"]

        self.table.setRowCount(len(z_scores))
        for i, z in enumerate(z_scores):
            status = "SUSPICIOUS" if i in suspicious else "normal"
            self.table.setItem(i, 0, QTableWidgetItem(str(i)))
            self.table.setItem(i, 1, QTableWidgetItem(f"{z:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(status))

    def on_scan_error(self, error_message):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("Scan Model")
        self.verdict_label.setText(f"ERROR: {error_message}")