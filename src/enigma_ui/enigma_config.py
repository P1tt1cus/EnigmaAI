from PySide6 import QtWidgets, QtCore

class EnigmaConfigTab(QtWidgets.QWidget):
    
    def __init__(self, update_host_port: callable):
        """
        Initializes the EnigmaConfigTab for configuring the Ollama server URL and port.
        """
        super().__init__()
        self.update_host_port = update_host_port

        # Initialize UI elements
        self.url_label = QtWidgets.QLabel("Ollama Server URL:")
        self.url_input = QtWidgets.QLineEdit("http://localhost")  # Default URL

        self.port_label = QtWidgets.QLabel("Ollama Server Port:")
        self.port_input = QtWidgets.QLineEdit("11434")  # Default Port

        self.save_button = QtWidgets.QPushButton("Save Configuration")
        self.save_button.clicked.connect(self.onSaveConfigClicked)

        # Set up the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.save_button)

        self.url = None
        self.port = None

        self.setLayout(layout)

    @QtCore.Slot()
    def onSaveConfigClicked(self) -> None:
        """
        Handles the event when the 'Save Configuration' button is clicked.
        Saves the entered URL and port.
        """
        try:

            self.url = self.url_input.text()
            self.port = int(self.port_input.text())
            
            # Run the update_ai_client function to update the AI client with the new configuration
            self.update_host_port(self.url, self.port)

            QtWidgets.QMessageBox.information(self, "Configuration Saved", f"Ollama Server URL and Port saved successfully!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error saving configuration: {str(e)}")