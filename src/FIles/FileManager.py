import json 
import os
from datetime import datetime
class FileManager():
    
    def __init__(self) -> None:
        self.BD_PATH = 'src/Files/bd.json'
        self.DEFAULTS_DIRECTORIES:tuple = ("personal", "drive", "root")

    def getFileProperties(self, path: str) -> dict:
        file: dict = {}  # Crear un diccionario vacío para almacenar las propiedades del archivo
        if os.path.exists(path):  # Comprobar si la ruta de archivo existe
            # Rellenar el diccionario con las propiedades del archivo
            file = {
                "name": os.path.basename(path),  # Nombre del archivo
                "extension": os.path.splitext(path)[1],  # Extensión del archivo
                "absolutePath": path,  # Ruta absoluta del archivo
                "creationDate": datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d %H:%M:%S"),  # Fecha de creación del archivo
                "lastModification": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S"),  # Última fecha de modificación del archivo
                "size": os.path.getsize(path)  # Tamaño del archivo en bytes
            }
        else:
            # Si la ruta de archivo no existe, establecer un diccionario con un mensaje de error
            file = {"error": "File not found"}
        return file  # Devolver el diccionario con las propiedades del archivo

    def createUser(self, username: str, cantBytes: int) -> dict:
        try:
            with open(self.BD_PATH, 'r') as file:
                data = json.load(file)
                user_exists = any(user['username'] == username for user in data['users'])
                if user_exists:
                    return {"error": "Username already exists"}
                else:
                    data['users'].append({
                        "username": username,
                        "root": self.createDirectory("root"),
                        "sizeDrive": cantBytes
                    })
                    data['users'][-1]["root"]["directories"].append( self.createDirectory("personal"))
                    data['users'][-1]["root"]["directories"].append( self.createDirectory("drive"))
            
            with open(self.BD_PATH, 'w') as file:
                json.dump(data, file, indent=4)
            return {"status": "User created"}
        except IOError:
            return {"error": "User not created due to file IO error"}
        except json.JSONDecodeError:
            return {"error": "User not created due to JSON decoding error"}
    def getUser(self, username: str) -> dict:
        try:
            with open(self.BD_PATH, 'r') as file:  # Abrir el archivo JSON en modo de lectura
                data = json.load(file)  # Cargar los datos del archivo JSON
                user_exists = any(user['username'] == username for user in data['users'])  # Verificar si existe un usuario con el nombre de usuario especificado
                if user_exists:
                    # Si el usuario existe, devolver el primer usuario coincidente en la lista de usuarios
                    return next(user for user in data['users'] if user['username'] == username)
                else:
                    return {"error": "User not found"}  # Si el usuario no se encuentra, devolver un diccionario con un mensaje de error
        except IOError:
            return {"error": "User not found due to file IO error"}  # Manejar el error si ocurre un problema de E/S al abrir el archivo
        except json.JSONDecodeError:
            return {"error": "User not found due to JSON decoding error"}  # Manejar el error si ocurre un problema al decodificar el archivo JSON

    def __updateUser(self, userData: dict):
        try:
            with open(self.BD_PATH, 'r') as file:  # Abrir el archivo JSON en modo de lectura
                data = json.load(file)  # Cargar los datos del archivo JSON
                user_exists = any(user['username'] == userData['username'] for user in data['users'])  # Verificar si el usuario existe en la lista de usuarios
                if user_exists:
                    # Eliminar el usuario existente de la lista y agregar el usuario actualizado
                    data['users'] = [user for user in data['users'] if user['username'] != userData['username']]
                    data['users'].append(userData)
                    with open(self.BD_PATH, 'w') as file:  # Abrir el archivo JSON en modo de escritura
                        json.dump(data, file, indent=4)  # Sobrescribir el archivo JSON con los datos actualizados
                    return {"status": "User updated successfully"}  # Devolver un diccionario con un mensaje de éxito
                else:
                    return {"error": "User not found"}  # Si el usuario no se encuentra, devolver un diccionario con un mensaje de error
        except IOError:
            return {"error": "User not found due to file IO error"}  # Manejar el error si ocurre un problema de E/S al abrir o escribir en el archivo
        except json.JSONDecodeError:
            return {"error": "User not found due to JSON decoding error"}  # Manejar el error si ocurre un problema al decodificar el archivo JSON
    
    def addFile(self, userData: dict, fileData: dict, path: str) -> dict:
        dest: dict = self.__searchDirectory(userData, path)
        if dest.get("error"):
            return dest
        dest["files"].append(fileData)
        self.__updateUser(userData)
        return {"status": "File added successfully"}
    def addDirectory(self, userData: dict, directoryData: dict, path: str) -> dict:
        dest: dict = self.__searchDirectory(userData, path)
        if dest.get("error"):
            return dest
        dest["directories"].append(directoryData)
        self.__updateUser(userData)
        return {"status": "Directory added successfully"}
    def deleteFile(self, userData: dict, path: str) -> dict:
        path = tuple(path.split("/"))
        dest: dict = userData["root"]
        for directory in path[:-1]:
            directory_found:bool = False
            for item in dest["directories"]:
                if item.get("name") == directory:
                    dest = item
                    directory_found = True
                    break
            if not directory_found:
                return {"error": "Directory not found"}
        for file in dest["files"]:
            if file.get("name") == path[-1]:
                dest["files"].remove(file)
                self.__updateUser(userData)
                return {"status": "File deleted successfully"}
        return {"error": "File not found"}
    def deleteDirectory(self, userData: dict, path: str) -> dict:
        path = tuple(path.split("/"))
        dest: dict = userData["root"]
        if self.isDefaultDirectory(path[-1]):
            return {"error": "Default directory cannot be deleted"}
        for directory in path[:-1]:
            directory_found:bool = False
            for item in dest["directories"]:
                if item.get("name") == directory:
                    dest = item
                    directory_found = True
                    break
            if not directory_found:
                return {"error": "Directory not found"}
        for directory in dest["directories"]:
            if directory.get("name") == path[-1]:
                dest["directories"].remove(directory)
                self.__updateUser(userData)
                return {"status": "Directory deleted successfully"}
        return {"error": "Directory not found"}
    def __searchDirectory(self, userData: dict, directoryPath: str):
        path = tuple(directoryPath.split("/"))
        dest: dict = userData["root"]
        for directory in path:
            directory_found:bool = False
        
            for item in dest["directories"]:
                if item.get("name") == directory:
                    dest = item
                    directory_found = True
                    break
            if not directory_found:
                return {"error": "Directory not found"}
        return dest
    def searchFile(self, userData: dict, path: str) -> dict:
        fileName = path.split("/")[-1]
        directoryPath = "/".join(path.split("/")[:-1])
        dest: dict = self.__searchDirectory(userData, directoryPath)
        if dest.get("error"):
            return dest
        for file in dest["files"]:
            if file.get("name") == fileName:
                return file
        return {"error": "File not found"}
    def createDirectory(self, name:str)->dict:
        return  {
                    "name": name,
                    "directories": [],
                    "files": []
                }
    def createFile2(self, absolutePath:str)->dict:
        name: str = absolutePath.split("\\")[-1]
        return {
            "name": name,
            "absolutePath": absolutePath,
        }
    
    def generarId(self) -> int:
        with open(self.BD_PATH, 'r') as file:
            json_content = json.load(file)
            json_content["id_counter"] += 1

        with open(self.BD_PATH, 'w') as file:
            json.dump(json_content, file)

        return json_content["id_counter"]
    
    def calcularTamanoEnBytes(self, string:str)->int:
        bytes_string = string.encode()
        tamano_en_bytes = len(bytes_string)
        return tamano_en_bytes

    def createFile(self, name:str, content:str)->dict:
        id = self.generarId()
        return {
            "id": id,
            "name": name+".txt",
            "content": content,
            "size": self.calcularTamanoEnBytes(content),
            "compartido": False
        }
    

    def isDefaultDirectory(self, name:str)->bool:
        return name in self.DEFAULTS_DIRECTORIES
# bd = BD()
bd: FileManager = FileManager()
#print(bd.createUser("Prueba",100))
print(bd.addFile(bd.getUser("Prueba"), bd.createFile("Filetest", "Hola, esto es una prueba"), "personal"))
print(bd.getUser("Prueba"))
#print(bd.addFile(bd.getUser("Valeria"), bd.createFile("Filetest", r"c:\Users\Esteb\Documents\ProyectoDriveTest"), "personal/carpetaprueba"))

# print(bd.getUser("test"))
# print(bd.deleteFile(bd.getUser("test"), "personal/Filetest"))
# print(bd.getUser("test"))
# print(bd.deleteFile(bd.getUser("test"), "test"))
# print(bd.getUser("test"))
#print(bd.addDirectory(bd.getUser("test"), bd.createDirectory("test1"), "personal"))
# print(bd.addDirectory(bd.getUser("test"), bd.createDirectory("test2"), "personal/test1"))
# print(bd.addDirectory(bd.getUser("test"), bd.createDirectory("test3"), "personal/test1/test2")) # Error
# print(bd.addFile(bd.getUser("Valeria"), bd.createFile(r"c:\Users\Esteb\Documents\ProyectoDriveTest\prueba1.txt"), "drive"))
# File: dict = bd.searchFile(bd.getUser("Valeria"), "drive/prueba1.txt")
# print(bd.getFileProperties(File["absolutePath"]))
# print(bd.deleteFile(bd.getUser("test"), "personal/test1/test2/Filetest.txt"))


    
