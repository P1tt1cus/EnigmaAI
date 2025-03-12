from .enigma_ollama import EnigmaOllamaClient

class OllamaConfig:
    def __init__(self):
        self.host = None
        self.port = None
        self.model = None
        self.client = self._create_client()

    def _create_client(self):
        return EnigmaOllamaClient(host=self.host, port=self.port, model=self.model)

    def update_host_port(self, host, port):
        self.host = host
        self.port = port
        self.client = self._create_client()

    def update_model(self, model):
        self.model = model
        self.client = self._create_client()