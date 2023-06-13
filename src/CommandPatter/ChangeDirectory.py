
import iExecute
from Files.FileManager import FileManager
class ChangeDirectory(iExecute):
    def __init__(self, BD:FileManager):
        self.BD = BD
    def execute(self, comands:list, **kargs)->dict:
        """
        Change the current directory to the directory passed in the comands list.
        """
        return None
    