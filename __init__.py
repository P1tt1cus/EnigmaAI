from binaryninjaui import Sidebar

from .src.enigma_sidebar import EnigmaAIWidgetType

enigma_ai_widget = EnigmaAIWidgetType()
Sidebar.addSidebarWidgetType(enigma_ai_widget)

