from ollama import chat, Client
from ollama import ChatResponse
from enum import Enum
from collections import deque
from .enigma_prompts import EnigmaPrompts
import json
import os
from PySide6 import QtCore

class MType(Enum):
    SYSTEM = 1
    SYSTEM_PSEUDO = 2
    SYSTEM_RENAME_FN = 3

class EnigmaOllamaClient(QtCore.QObject):  # Inherit from QObject

    response_received = QtCore.Signal(str)  # Define a signal

    def __init__(self, host: str = None, port: int = None, model: str = None):
        super().__init__()  # Call QObject's constructor
        self.ollama_model = model
        self.client: Client = None
        self.host = host
        self.port = port
        self.system_messages_general = EnigmaPrompts.general
        self.system_messages_pseudo_c = EnigmaPrompts.pseudo_c
        self.conversation_history = deque(maxlen=20)

        # Current function IL
        self.function_il = {
            "role": "system",
            "content": None
        }

        print("Creating Ollama client")

        # Cache directory for config
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # Load the cached model and set it       
        self._load_model_config()

        # Load the configuration
        # This will create a client with the cached config
        self._load_client_config()
        
        # Create the client is host and port is set
        # Only should be set if the config was saved in the UI, which will overwrite the cache
        if host and port:
            self.host = host
            self.port = port
            self.create_client()

        if model:
            self.ollama_model = model
            self.cache_data()
 
    def create_client(self):
        """ Create the Ollama client. """
        
        # Create the client 
        self.client = Client(host=f"{self.host}:{self.port}")
        self.cache_data()

    def get_models(self):
        """
        Return a list of available models.

        Returns:
            list: A list of available models or none if no client is created.        
        """
        if self.client is not None:
            print("Getting models")
            return self.client.list()
        return None

    def cache_data(self):
        """
        Cache the model and client data.
        """
        if self.ollama_model:
            with open(os.path.join(self.cache_dir, 'model.json'), 'w') as f:
                json.dump({'model': self.ollama_model}, f)

        if self.client:
            with open(os.path.join(self.cache_dir, 'server.json'), 'w') as f:
                json.dump({'host': self.host, 'port': self.port}, f)

    def set_model(self, model: str):
        self.ollama_model = model
        self.cache_data()

    def chat_psuedo_c(self):
        """
        Send a message to the Ollama model and prepended system messages
        and save context.
        """
        self.chat(type=MType.SYSTEM_PSEUDO)
    
    def chat_rename_function(self):
        """
        Send a message to the Ollama model and prepended system messages
        and save context.
        """
        self.chat(type=MType.SYSTEM_RENAME_FN)

    def chat(self, message: str = None, type: MType = MType.SYSTEM):
        """
        Send a message to the Ollama model and prepended system messages
        and save context.
        """

        # Check if the model and client are set
        if not self.ollama_model or not self.client:
            return None
        
        # Prepare message queue based on mtype
        messages = self.prepare_message_queue(type)

        # Only save system message context
        if type == MType.SYSTEM:
            
            # Save the conversation context
            new_message = self.save_conversation('user', message)
            
            # Prepare the new message
            messages.append(new_message)

        # Get the response back from the client
        ai_response = ""
        for part in self.client.chat(model=self.ollama_model, messages=messages, stream=True):
            ai_response += part.message.content
            self.response_received.emit(part.message.content)
    
        # Save the context of the response if message type is system
        if type == MType.SYSTEM:
            self.save_conversation("assistant", ai_response)
    
    def prepare_message_queue(self, type: MType) -> list:
        """ Prepare initial message queue to provide to the model """
        
        # Create a fresh message queue for prepending system
        # messages to conversation history.
        messages = []

        if type == MType.SYSTEM:
       
            # Add the system messages first.
            messages.extend([{'role': 'system', 'content': msg} for msg in self.system_messages_general])
            
            # Append the conversation history - only for system messages
            messages.extend(self.conversation_history)
       
        elif type == MType.SYSTEM_PSEUDO:

            # Add the system pseudo-c messages 
            messages.extend([{'role': 'system', 'content': msg} for msg in self.system_messages_pseudo_c])
        
        elif type == MType.SYSTEM_RENAME_FN:

            # Add the system rename function messages
            messages.extend([{'role': 'system', 'content': msg} for msg in EnigmaPrompts.rename_fn])

        # Enigma AI should always have context of the current function IL
        # Atleast for now.
        messages.append(self.function_il)

        return messages
    
    def set_function_il(self, function_il: str):
        """ 
        Set the current function IL.
        """
        self.function_il['content'] = function_il
    
    def add_sys_msg(self, chat_message: str):
        """ 
        Save a system message that will persistently be re-used generally.
        """
        message = {
            'role' : 'system',
            'content' : chat_message
        }
        self.system_messages_general.append(message)
 
    def add_c_sys_msg(self, chat_message: str):
        """ 
        Save a system message that will persistently be re-used for psuedo-c 
        calls.
        """
        message = {
            'role' : 'system',
            'content' : chat_message
        }
        self.system_messages_pseudo_c.append(message)

    def save_conversation(self, role: str, message: str) -> dict:
        """ 
        Save conversation context for a period of time.
        """
        message = {
            'role': role,
            'content': message,
        }
        self.conversation_history.append(message)

        return message
    
    def _load_client_config(self):
        """ 
        Load the configuration from a file.
        """
        client_config_path = os.path.join(self.cache_dir, 'server.json')
        print(client_config_path)
        if os.path.exists(os.path.join(self.cache_dir, 'server.json')):
            print("Loading client config")
            with open(os.path.join(self.cache_dir, 'server.json'), 'r') as f:
                config = json.load(f)
                self.host = config['host']
                self.port = config['port']
                self.create_client()
                return True
        print("No client config found")
        return False

    def _load_model_config(self):
        """ 
        Load the model configuration from a file.
        """
        if os.path.exists(os.path.join(self.cache_dir, 'model.json')):
            print("Loading model config")
            with open(os.path.join(self.cache_dir, 'model.json'), 'r') as f:
                config = json.load(f)
                self.ollama_model = config['model']
                return True
        return False
    
    def clear_context(self):
        """ 
        Clear the conversation history.
        """
        self.conversation_history.clear()

    def client_exists(self):
        """ 
        Check if the client exists.
        """
        return self.client is not None