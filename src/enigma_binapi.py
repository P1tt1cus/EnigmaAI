from binaryninja import BinaryView


class EnigmaBinAPI:

    def __init__(self, parent: BinaryView) -> None:
        """
        This class holds for methods fpr the Binary Ninja API for the Enigma plugin.
        """
        self.parent = parent

    def rename_function(self, old_name: str, new_name: str) -> bool:
        """
        Rename a function in the Binary Ninja database.
        return: 
            bool: True if the function was renamed successfully, False otherwise.
        """
        functions = self.parent.bv.get_functions_containing(self.parent.offset_addr)
        for function in functions:
            if function.name == old_name:
                print("renamed function")
                function.name = new_name
                return True
        return False
    
    def get_function_name(self) -> str:
        """
        Get the name of the current function.
        return: 
            str: The name of the function.
        """
        if not self.parent.offset_addr:
            return "None"
        func = self.parent.bv.get_functions_containing(self.parent.offset_addr)
        if func:
            self.func_name = func[0].name
            return func[0].name
        return "None"
    
    def get_function_il(self) -> str:
        """
        Get the IL of the current function.
        return: 
            str: The IL of the function.
        """
        if not self.parent.offset_addr:
            return "None"
        func = self.parent.bv.get_functions_containing(self.parent.offset_addr)
        if func:
            return str(func[0].high_level_il)
        return "None"
    
    def update_offset(self, offset: int) -> None:
        """
        Update the offset address.
        """
        self.parent.offset_addr = offset