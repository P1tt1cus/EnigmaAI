from PySide6 import QtCore


class OllamaWorker(QtCore.QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(str)

    def __init__(self, ai_client, function_il=None, message=None):
        super().__init__()
        self.ai_client = ai_client
        self.function_il = function_il
        self.message = message
    
    @QtCore.Slot()
    def run_c(self):
        """
        Long-running task.
        """
        self.ai_client.chat_psuedo_c()
        self.finished.emit()

    @QtCore.Slot()
    def run_rename_fn(self):
        """
        Long-running task.
        """
        self.ai_client.chat_rename_function()
        self.finished.emit()

    @QtCore.Slot()
    def run(self):
        """
        Long-running task.
        """
        self.ai_client.chat(str(self.message))
        self.finished.emit()
