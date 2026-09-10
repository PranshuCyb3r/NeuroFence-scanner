BACKGROUND = "#1a1a2e"
CARD_BACKGROUND = "#16213e"
TEXT_COLOR = "#e0e0e0"
ACCENT = "#0f3460"
DANGER = "#e94560"      # laal - "BACKDOOR LIKELY" ke liye
SAFE = "#4caf50"        # hara - "CLEAN" ke liye

STYLESHEET = f"""
QMainWindow {{
    background-color: {BACKGROUND};
}}
QLabel {{
    color: {TEXT_COLOR};
    font-size: 14px;
}}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    padding: 10px;
    border-radius: 5px;
    font-size: 14px;
}}
QPushButton:hover {{
    background-color: #16537e;
}}
QTableWidget {{
    background-color: {CARD_BACKGROUND};
    color: {TEXT_COLOR};
    gridline-color: {ACCENT};
}}
"""