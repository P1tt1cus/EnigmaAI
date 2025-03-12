from PySide6 import QtCore, QtWidgets, QtGui
from .enigma_workers import OllamaWorker
import markdown

class EnigmaChatSidebar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        self.setObjectName("EnigmaChatSidebar")
        
        self.example_fn = QtWidgets.QPushButton("Explain function", self)
        self.rename_vr = QtWidgets.QPushButton("Rename variables", self)
        self.rename_fn = QtWidgets.QPushButton("Rename function", self)

        self.example_fn.clicked.connect(parent.explain_function)
        self.rename_fn.clicked.connect(parent.rename_function)

        layout.addWidget(self.example_fn)
        layout.addWidget(self.rename_vr)
        layout.addWidget(self.rename_fn)
        layout.addStretch()

class EnigmaChatTab(QtWidgets.QWidget):
    def __init__(self, parent, bin_api):
        super().__init__()
        self.bin_api = bin_api
        self.parent = parent
        self._ai_client = parent._ai_client

        # For renaming function
        self._tmp_new_fn_name = ""
        self._tmp_old_fn_name = ""

        # Initialize Markdown with an extension for fenced code blocks.
        self.md = markdown.Markdown(extensions=['fenced_code', 'codehilite', 'tables'])

        # Chat history: list of (author, message) tuples.
        self.chat_history = []
        
        # Buffer to hold the current streaming AI response.
        self.current_stream = ""
 
        # Connect the Explain function button to the parent's explain_function.
        self._ollama_message_connected = False
        self._fn_name_connected = False
       
        # Flag to indicate streaming is in progress.
        self.is_streaming = False

        # UI elements for the chat area.
        self.chat_box = QtWidgets.QTextBrowser()
        self.chat_box.setReadOnly(True)
        self.chat_box.setOpenLinks(False)
        self.chat_box.anchorClicked.connect(self.on_anchor_clicked)
        self.chat_box.document().setDefaultStyleSheet(self.get_style_sheet())

        self.input_box = QtWidgets.QLineEdit()
        self.send_button = QtWidgets.QPushButton("Send")
        self.clear_button = QtWidgets.QPushButton("Clear Chat")

        # Chat layout (chat_box + input area).
        chat_layout = QtWidgets.QVBoxLayout()
        chat_layout.addWidget(self.chat_box)
        input_layout = QtWidgets.QHBoxLayout()
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)
        chat_layout.addLayout(input_layout)

        # Main layout contains only the chat area so its width is not affected by the sidebar.
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(chat_layout)
        self.setLayout(main_layout)

        # Create the sidebar as a floating widget.
        self.sidebar = EnigmaChatSidebar(self)
        # By default, the sidebar is hidden.
        self.sidebar_visible = False
        self.sidebar.setVisible(False)

        # Create a toggle button for the sidebar (it will float over the top right).

        self.sidebar_toggle = QtWidgets.QToolButton(self)
        self.sidebar_toggle.setFixedSize(30, 30)
        self.sidebar_toggle.setText("»")
        self.sidebar_toggle.clicked.connect(self.toggle_sidebar)

        # Connections.
        self.send_button.clicked.connect(self.on_send_clicked)
        self.clear_button.clicked.connect(self.clear_chat)
        self.input_box.returnPressed.connect(self.on_send_clicked)

        # Render initial chat (if any).
        self.render_html()

    def resizeEvent(self, event):
        """
        Position the toggle button and the sidebar.
        The toggle button is repositioned based on sidebar visibility.
        """
        super().resizeEvent(event)
        margin = 10
        toggle_width = self.sidebar_toggle.width()
        if self.sidebar_visible:
            x = self.width() - self.sidebar.width() - toggle_width - margin
        else:
            x = self.width() - toggle_width - margin
        self.sidebar_toggle.move(x, margin)
        if self.sidebar_visible:
            self.sidebar.setGeometry(self.width() - self.sidebar.width(), 0,
                                      self.sidebar.width(), self.height())
        else:
            self.sidebar.setGeometry(self.width(), 0, self.sidebar.width(), self.height())
        self.sidebar_toggle.raise_()

    def toggle_sidebar(self):
        """
        Toggles the visibility of the sidebar and updates the toggle button icon.
        """
        self.sidebar_visible = not self.sidebar_visible
        self.sidebar.setVisible(self.sidebar_visible)
        if self.sidebar_visible:
            self.sidebar_toggle.setText("«")
        else:
            self.sidebar_toggle.setText("»")
        self.resizeEvent(None)

    def _send_message(self, message, run_method_name: str):
        """
        Common method to append message, start worker thread, and update UI.
        The run_method_name argument should be the name of the worker method
        to call (e.g. 'run' or 'run_c').
        """
        if not message.strip():
            return

        self.append_message("You", message)
        self._ai_client.set_function_il(self.bin_api.get_function_il())
        self.input_box.clear()

        self.is_streaming = True
        self.current_stream = ""
        self.chat_history.append(("EnigmaAI", ""))
        self.render_html()

        # Create a new thread and worker for the long-running task. 
        self.thread = QtCore.QThread()
        self.worker = OllamaWorker(self._ai_client, message=message)
        self.worker.moveToThread(self.thread)
        
        # Get the worker method to call.

        # Depending on the run_method_name, we will call the appropriate method.
        # This is a simple way to avoid code duplication.
        run_method = getattr(self.worker, run_method_name)
        self.thread.started.connect(run_method)

        # Connect signals for cleanup        

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Depending on the run_method_name, we will connect the appropriate signals.
        if run_method_name in ["run", "run_c"]:
            self._ai_client.response_received.connect(self.append_ollama_message, QtCore.Qt.UniqueConnection)
            self._ollama_message_connected = True
            self.worker.finished.connect(self.finish_response)

        elif run_method_name == "run_rename_fn":
            self._ai_client.response_received.connect(self.append_fn_name, QtCore.Qt.UniqueConnection)
            self._fn_name_connected = True
            self.worker.finished.connect(self.final_rename)

        self.thread.start()

    def on_send_clicked(self):
        """
        Called when the Send button is clicked.
        """
        message = self.input_box.text()
        self._send_message(message, "run")

    def explain_function(self):
        """
        Called to explain a function; behaves like on_send_clicked
        but uses the worker's run_c method.
        """

        # In this example, we use the same input box text.
        # You could alternatively pre-populate the message from another source.
        self._send_message("Running explain function.", "run_c")

    def rename_function(self):
        """
        Use the Binary Ninja API to rename a function based on
        EnigmaAI's suggestion.
        """
        
        # Store the old function name for later. 
        # This techincally is going to cause a bug, but it's a good example for now.
        self._tmp_old_fn_name = self.bin_api.get_function_name()

        # Set the tmp name to empty.
        self._tmp_new_fn_name = ""

        # Run the rename function.
        self._send_message("Running rename function.", "run_rename_fn")

    def final_rename(self):
        """
        Final function rename call.
        """
        if self._tmp_new_fn_name:
            self.bin_api.rename_function(self._tmp_old_fn_name, self._tmp_new_fn_name)
            
            # Add confirmation message to chat window
            confirmation = f"Function renamed successfully:\n- Old name: `{self._tmp_old_fn_name}`\n- New name: `{self._tmp_new_fn_name}`"
            self.append_message("EnigmaAI", confirmation)
        else:
            # Handle case where no name was generated
            self.append_message("EnigmaAI", "Error: Failed to generate a new function name.")
        
        self.disconnect_signals()
        self.render_html()

    @QtCore.Slot(str)
    def append_fn_name(self, message):
        """
        Store's the returned function name from the AI.
        """
        self._tmp_new_fn_name += message

    def append_message(self, author, message):
        """
        Appends a message to the chat history and refreshes the display.
        """
        self.chat_history.append((author, message))
        self.render_html()

    @QtCore.Slot(str)
    def append_ollama_message(self, message):
        """
        Called when a new chunk arrives from the AI.
        Updates the streaming buffer and refreshes the display.
        """
        self.current_stream += message
        self.chat_history[-1] = ("EnigmaAI", self.current_stream)
        self.render_html()

    def finish_response(self):
        """
        Ends streaming and renders the final Markdown-processed response.
        """
        self.is_streaming = False
        final_text = self.md.convert(self.current_stream)
        self.chat_history[-1] = ("EnigmaAI", final_text)
        self.render_html()
        self.disconnect_signals()
        
    def disconnect_signals(self):
        """
        Disconnects all signals from the AI client.
        """
        if self._ollama_message_connected:
            try:
                self._ai_client.response_received.disconnect(self.append_ollama_message)
                self._ollama_message_connected = False
            except (TypeError, RuntimeError):
                # Slot was not connected or object already deleted
                self._ollama_message_connected = False
        
        if self._fn_name_connected:
            try:
                self._ai_client.response_received.disconnect(self.append_fn_name)
                self._fn_name_connected = False
            except (TypeError, RuntimeError):
                # Slot was not connected or object already deleted
                self._fn_name_connected = False

    def render_html(self):
        """
        Renders the chat history to the chat box.
        """
        html_parts = []

        for author, message in self.chat_history:
            if author == "Context":
                html_parts.append(f"<div class='context'>{self.md.convert(message)}</div>")
            elif author == "You":
                html_parts.append(f"<div class='user-message'><strong>{author}:</strong> {message}</div>")
            elif author == "EnigmaAI":
                if self.is_streaming and message == self.current_stream:
                    html_parts.append(f"<div class='ai-message streaming'><strong>{author}:</strong> {message}</div>")
                else:
                    html_parts.append(f"<div class='ai-message'><strong>{author}:</strong> {message}</div>")
            else:
                html_parts.append(f"<div><strong>{author}:</strong> {message}</div>")

        final_html = self.get_style_sheet() + "".join(html_parts)
        self.chat_box.setHtml(final_html)
        self.scroll_to_bottom()
        
    def get_style_sheet(self):
        """
        Returns CSS styling for chat messages.
        """
        return """
            <style>
                body { font-family: Arial, sans-serif; }
                .context { margin-bottom: 15px; }
                .user-message { margin-bottom: 15px; }
                .ai-message { margin-bottom: 15px; }
                /* Code block styling */
                pre, code {
                    background-color: #333333;
                    color: #00FF00;
                    font-family: Consolas, monospace;
                    padding: 10px;
                    border-radius: 4px;
                    overflow-x: auto;
                }
            </style>
        """

    def scroll_to_bottom(self):
        """
        Scrolls the chat box to the bottom.
        """
        scrollbar = self.chat_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_anchor_clicked(self, url: QtCore.QUrl):
        """
        Opens a clicked URL in the default browser.
        """
        print(f"Anchor clicked: {url.toString()}")
        QtGui.QDesktopServices.openUrl(url)

    def clear_chat(self):
        """
        Clears the chat history and resets the UI.
        """
        self.chat_history.clear()
        self.current_stream = ""
        if hasattr(self._ai_client, "clear_context"):
            self._ai_client.clear_context()

        # Refresh the chat box.
        self.render_html()