from PyQt6.QtCore import QThread, pyqtSignal

class ScanWorker(QThread):
    """
    Scan ko background thread mein chalata hai, taaki GUI freeze na ho.
    Jab scan complete ho jaye, 'finished_scan' signal ke through result bhejta hai.
    """
    finished_scan = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, model_path, trigger_word):
        super().__init__()
        self.model_path = model_path
        self.trigger_word = trigger_word

    def run(self):
        try:
            from neurofence.core.scanner import run_scan
            result = run_scan(model_path=self.model_path, trigger_word=self.trigger_word)
            self.finished_scan.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))