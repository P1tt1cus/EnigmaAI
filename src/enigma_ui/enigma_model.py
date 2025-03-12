from PySide6 import QtCore, QtWidgets
import json
import os

class EnigmaModelTab(QtWidgets.QWidget):

    def __init__(self, parent, model_ai_update: callable):
        """
        Initializes the EnigmaConfigTab for configuring the Ollama server URL and port.
        """
        super().__init__()
        self.model_ai_update = model_ai_update
        self.parent = parent

        self.model_list = QtWidgets.QComboBox()

        self.save_button = QtWidgets.QPushButton("Save Model")
        self.save_button.clicked.connect(self.onSaveModelClicked)

        self.refresh = QtWidgets.QPushButton("Refresh")
        self.refresh.clicked.connect(self.update_model_list)

        # Set up the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.model_list)
        layout.addWidget(self.refresh)
        layout.addWidget(self.save_button)

        # Cache directory for config
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.current_model = None

        self.setLayout(layout)

    def update_model_list(self):
        """
        Updates the model list with the available models.
        """
        self.model_list.clear()
        if self.parent._ai_client is not None:
            try:
                if self.parent._ai_client.client_exists():
                    models = self.parent._ai_client.get_models()
                    if models:
                        model_names = [model.model for model in [model for model in [model[1] for model in models][0]]]
                        for model in model_names:
                            self.model_list.addItem(model)
                    else:
                        self.model_list.addItem("No models available")
                else: 
                    self.model_list.addItem("Client has not been created yet.")
            except Exception as e:
                print(f"Error updating model list: {e}")
                self.model_list.addItem(f"Error: {e}")
        else: 
            self.model_list.addItem("Error no client")
        
    @QtCore.Slot()
    def onSaveModelClicked(self) -> None:
        """
        Handles the event when the 'Save Configuration' button is clicked.
        Saves the entered URL and port.
        """
        self.current_model = self.model_list.currentText()
        self.model_ai_update(self.current_model)
        QtWidgets.QMessageBox.information(self, "Model Selected", f"Model selection saved successfully!")