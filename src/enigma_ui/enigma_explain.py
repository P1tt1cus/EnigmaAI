from PySide6 import QtCore, QtWidgets, QtGui
from .enigma_workers import OllamaWorker
import markdown  

class EnigmaExplainTab(QtWidgets.QWidget):

    def __init__(self, parent, bin_api):
        """
        Initialize the EnigmaExplainTab.
        """
        super().__init__()
        self.bin_api = bin_api
        self.parent = parent

        # Define these so that callbacks can use them without errors.
        self.session_log = []

        # Configure Markdown with fenced_code extension
        self.md = markdown.Markdown(extensions=['fenced_code'])

        # Create UI elements
        self.text_box = QtWidgets.QTextBrowser()
        self.text_box.setReadOnly(True)
        self.text_box.setOpenLinks(False)
        self.text_box.anchorClicked.connect(self.onAnchorClicked)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text_box)
        layout.addLayout(self._create_explain_buttons_layout())

        self.setLayout(layout)  # Set the layout on the widget

        self.message_data = ""

        # Connect the signal from EnigmaOllamaClient to the slot
        #self.parent._ai_client.response_received.connect(self.update_text_box) # REMOVE THIS LINE

    def _create_explain_buttons_layout(self) -> QtWidgets.QHBoxLayout:
        """
        Creates the layout with buttons for explanation functionalities.

        Returns:
            QHBoxLayout: Layout containing buttons for explanation actions.
        """
        layout = QtWidgets.QHBoxLayout()

        explain_il_bt = QtWidgets.QPushButton("Explain Function")
        explain_line_bt = QtWidgets.QPushButton("Explain Line")
        clear_text_bt = QtWidgets.QPushButton("Clear")

        # Connect signals to slot methods.
        connected = explain_il_bt.clicked.connect(self.onExplainFunctionClicked)
        if not connected:
            print("Failed to connect explain_il_bt to onExplainFunctionClicked")

        connected = explain_line_bt.clicked.connect(self.onExplainLineClicked)
        if not connected:
            print("Failed to connect explain_line_bt to onExplainLineClicked")

        connected = clear_text_bt.clicked.connect(self.onClearTextClicked)
        if not connected:
            print("Failed to connect clear_text_bt to onClearTextClicked")

        layout.addWidget(explain_il_bt)
        layout.addWidget(explain_line_bt)
        layout.addWidget(clear_text_bt)

        # Store button references
        self.explain_il_bt = explain_il_bt
        self.explain_line_bt = explain_line_bt
        self.clear_text_bt = clear_text_bt

        return layout

    def onExplainFunctionClicked(self) -> None:
        """
        Called when the 'Explain Function' button is clicked.
        """

        # Always clear the text box before adding new text
        self.text_box.clear()
        self.thread = QtCore.QThread()
        self.worker = OllamaWorker(self.parent._ai_client, self.bin_api.get_function_il())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_c)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_text_box)
        self.worker.finished.connect(self.render_html)
        self.thread.start()

    def onExplainLineClicked(self) -> None:
        """
        Called when the 'Explain Line' button is clicked.
        """
        print("Explain Line button clicked!")
        line_text = self.bin_api.get_line_text()
        html = markdown.markdown(str(line_text))  # Convert to HTML
        self.text_box.setHtml(html)  # Set HTML to QTextBrowser

    def onClearTextClicked(self) -> None:
        """
        Clears all text boxes when the 'Clear' button is clicked.
        """
        print("Clear button clicked!")
        self.session_log.clear()
        self.text_box.clear()

    def onAnchorClicked(self, url: QtCore.QUrl) -> None:
        """
        Opens the clicked URL in the default browser.

        Args:
            url (QUrl): The URL that was clicked.
        """
        print(f"Anchor clicked: {url.toString()}")
        QtGui.QDesktopServices.openUrl(url)
    
    def render_html(self):
        """
        Render the HTML to the text box.
        """
        html = self.md.convert(self.message_data)
        self.text_box.clear()
        self.text_box.setHtml(html)


    @QtCore.Slot(str)
    def update_text_box(self, message):
        """
        Update the text box with the new message.
        """
        # html = self.md.convert(message)
        self.message_data += message
        self.text_box.clear()
        self.text_box.append(self.message_data)

