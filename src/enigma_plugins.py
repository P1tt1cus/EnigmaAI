from binaryninja import BinaryView
from .enigma_ui import OllamaConnectionDialog


def set_server_information(bv: BinaryView):
    print("set server information")

    dialog = OllamaConnectionDialog("titties", 1234)
    if dialog._exec():
        print("coool")


def set_model_dialog(bv):
    """
    Display a dialog to set the model for the Ollama client.

    Args:
        bv (BinaryView): The current BinaryView instance.

    Returns:
        bool: True if the model was set successfully, False otherwise.
    """
    set_server_dialog(bv)
    model_dialog = OllamaModelDialog(client.get_model(), client.get_available_models())
    if model_dialog.exec_():
        model = model_dialog.model_combo.currentText()
        return True
    return False