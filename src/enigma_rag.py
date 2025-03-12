import os

class RagDocs:

    def __init__(self):
        self.local_dir = os.path.dirname(os.path.abspath(__file__))
        self.local_cache_dir = os.path.join(self.local_dir, 'cache')
        if not os.path.exists(self.local_cache_dir):
            os.makedirs(self.local_cache_dir)

    def save_files(self, filepaths: list[str]):
        """ Save the contents of a file to the cache directory. """
        for filepath in filepaths:
            filename = os.path.basename(filepath)
            with open(filepath, 'r') as f:
                content = f.read()
            self._write_file(filename, content)
   
    def read_file(self, filename: str):
       """ Read the contents of a file in the cache directory. """
       with open(os.path.join(self.local_cache_dir, filename), 'r') as f:
            return f.read()
        
    def list_files(self):
        """ List all files in the cache directory. """
        return os.listdir(self.local_cache_dir)
    
    def _write_file(self, filename: str, content: str):
        """ Write the contents to a file in the cache directory. """
        with open(os.path.join(self.local_cache_dir, filename), 'w') as f:
            f.write(content)
        
    def delete_file(self, filename: str):
        """ Delete a file in the cache directory. """
        if os.path.exists(os.path.join(self.local_cache_dir, filename)):
            os.remove(os.path.join(self.local_cache_dir, filename))