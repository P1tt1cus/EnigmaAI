from binaryninja import *
from binaryninjaui import SidebarWidgetType, SidebarWidgetLocation, \
    SidebarContextSensitivity
from PySide6 import QtCore, QtGui
from .enigma_widgets import EnigmaAIWidgets

class EnigmaAIWidgetType(SidebarWidgetType):
    """
    A SidebarWidgetType for creating instances of EnigmaAIWidget and managing its properties.
    """

    def __init__(self) -> None:
        """
        Initializes the EnigmaAIWidgetType with an icon and sets up its basic properties.
        """
        icon = QtGui.QImage(56, 56, QtGui.QImage.Format_RGB32)
        icon.fill(0)
        p = QtGui.QPainter()
        p.begin(icon)
        p.setFont(QtGui.QFont("Open Sans", 36))
        p.setPen(QtGui.QColor(255, 255, 255, 255))
        p.drawText(QtCore.QRectF(0, 0, 56, 56), QtCore.Qt.AlignCenter, "AI")
        p.end()
        super().__init__(icon, "EnigmaAI")

    def createWidget(self, frame, data) -> EnigmaAIWidgets:
        """
        Factory method to create a new instance of EnigmaAIWidget.

        Parameters:
            frame (ViewFrame): The frame context for the widget.
            data: Additional data for the widget.

        Returns:
            EnigmaAIWidget: A new instance of EnigmaAIWidget.
        """
        enigma_ai_widget = EnigmaAIWidgets("EnigmaAI", frame, data)
        
        # Initialise the UI components
        enigma_ai_widget._init_ui()

        return enigma_ai_widget

    def defaultLocation(self) -> SidebarWidgetLocation:
        """
        Specifies the default location of the widget within the Binary Ninja UI.

        Returns:
            SidebarWidgetLocation: The default sidebar location.
        """
        return SidebarWidgetLocation.RightContent

    def contextSensitivity(self) -> SidebarContextSensitivity:
        """
        Defines the context sensitivity of the widget, indicating how it responds to context changes.

        Returns:
            SidebarContextSensitivity: The context sensitivity setting.
        """
        return SidebarContextSensitivity.SelfManagedSidebarContext