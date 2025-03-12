from binaryninja import *
from binaryninja.settings import Settings
from binaryninjaui import SidebarWidget, UIActionHandler
from PySide6 import QtCore, QtWidgets

# Enigma Imports
from .enigma_ollama import EnigmaOllamaClient, MType
from .enigma_rag import RagDocs
from .enigma_binapi import EnigmaBinAPI
from .enigma_ui import EnigmaExplainTab, EnigmaConfigTab, EnigmaModelTab, EnigmaChatTab
from .enigma_settings import OllamaConfig  # Import OllamaConfig

class EnigmaAIWidgets(SidebarWidget):
    """
    A custom widget for Binary Ninja that provides functionalities for querying and displaying
    responses from a language model, along with code analysis tools.
    """

    def __init__(self, name, frame, data) -> None:
        """
        Initializes the EnigmaAIWidget with the required components and settings.

        Parameters:
            name (str): The name of the widget.
            frame (ViewFrame): The frame context in which the widget is used.
        """
        super().__init__(name)
        self.offset_addr = 0
        self.config = OllamaConfig()  # Create OllamaConfig instance
        self._ai_client = self.config.client  # Initialise the client - attempts to load cached config
        self.rag_docs = RagDocs()
        self.actionHandler = UIActionHandler()
        self.actionHandler.setupActionHandler(self)
        self.bv = None
        self.binapi = None
        self.session_log = []
        self._init_ui()

    @property
    def ai_client(self) -> EnigmaOllamaClient:
        return self._ai_client

    @ai_client.setter
    def ai_client(self, new_client: EnigmaOllamaClient) -> None:
        self._ai_client = new_client

    # Call back to update the AI client when the configuration is changed
    def update_host_port(self, host: str, port: int):
        self.config.update_host_port(host, port)
        self.ai_client = self.config.client

    def model_ai_update(self, model: str):
        self.config.update_model(model)
        self.ai_client = self.config.client

    def _init_ui(self) -> None:
        """
        Sets up the initial UI components and layouts for the widget.
        """
        
        # Initialise the Binary Ninja API class for retrieving information
        self.bin_api = EnigmaBinAPI(self)

        # Initialise the tabs for the widget
        # self.explain_tab = EnigmaExplainTab(self, self.bin_api)
        self.model_tab = EnigmaModelTab(self, self.model_ai_update)
        self.config_tab = EnigmaConfigTab(self.update_host_port)
        self.chat_tab = EnigmaChatTab(self, self.bin_api)

        # Add the tabs to the main tab widget
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self.chat_tab, "Chat")
        # self.tabs.addTab(self.explain_tab, "Explain")
        self.tabs.addTab(self.config_tab, "Config")
        self.tabs.addTab(self.model_tab, "Model")

        # Set the layout for the widget
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def notifyOffsetChanged(self, offset) -> None:
        """
        Updates the displayed offset when it is changed in the binary view.

        Parameters:
            offset (int): The new offset value.
        """
        self.offset_addr = offset
        self.bin_api.update_offset(offset)

    def notifyViewChanged(self, view_frame) -> None:
        """
        Updates the widget's context based on changes in the view frame.

        Parameters:
            view_frame (ViewFrame): The new view frame context.
        """
        if view_frame is None:
            self.il_type = None
            self.datatype = None
            self.bv = None
        else:
            self.il_type = view_frame.getCurrentViewInterface().getILViewType()
            self.datatype = view_frame.getCurrentView()
            self.bv = view_frame.getCurrentBinaryView()

    def contextMenuEvent(self, event) -> None:
        self.m_contextMenuManager.show(self.m_menu, self.actionHandler)