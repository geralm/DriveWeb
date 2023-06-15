
import iExecute
import os
from Files.FileManager import FileManager

class CreateFile(iExecute):
    def __init__(self):
        pass

    #crea el archivo
    def crear_archivo(nombre_archivo, contenido):
        nombre_completo = nombre_archivo + ".txt"
        try:
            with open(nombre_completo, "w") as archivo:
                archivo.write(contenido)
            ruta_absoluta = os.path.abspath(nombre_completo)
            return ruta_absoluta
        except Exception as e:
            return 0
        

    def execute(self, comands:list, *args)->dict:
        """
        Create a file with the name and content passed in the comands list.
        """
        name = comands[0]
        content = comands[1]

        ruta = self.crear_archivo(name,content)
        print(ruta)

        if (ruta != 0):
            fileBD = FileManager()
            fileBD.createFile(self, ruta)
        else:
            print("Error\n")
    
        return None
    


