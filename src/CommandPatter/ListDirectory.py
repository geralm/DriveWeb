import iExecute
from Files.FileManager import FileManager
class ListDirectory(iExecute):
    def __init__(self, BD:FileManager):
        self.BD = BD
    def execute(self, comands:list, *args)->dict:
        """
        List the contents of the current directory.
        """
        
        return None