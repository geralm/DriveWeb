import json 
import os
from datetime import datetime

"""
    {
    "users": [
        {
        "username": "username",
        "root": {
            "personal": {
            "directories": [],
            "files": [
                {
                "name": "file1",
                "absolutePath": "C:/Users/username/personal/file1.txt",
                }
            ]
            },
            "drive": {}
        }
        }
    ]
    }
    
"""
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

    def createUser(self, username: str) -> dict:
        try:
            with open(self.BD_PATH, 'r') as file:
                data = json.load(file)
                user_exists = any(user['username'] == username for user in data['users'])
                if user_exists:
                    return {"error": "Username already exists"}
                else:
                    data['users'].append({
                        "username": username,
                        "root": self.createDirectory("root")
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
    def createFile(self, name:str, absolutePath:str)->dict:
        return {
            "name": name,
            "absolutePath": absolutePath,
        }
    def isDefaultDirectory(self, name:str)->bool:
        return name in self.DEFAULTS_DIRECTORIES
# bd = BD()
bd: FileManager = FileManager()
#print(bd.createUser("test2"))
# print(bd.getUser("test"))
# print(bd.addFile(bd.getUser("test"), bd.createFile("Filetest", r"c:\Users\Esteb\Documents\ProyectoDriveTest"), "personal"))
# print(bd.getUser("test"))
# print(bd.deleteFile(bd.getUser("test"), "personal/Filetest"))
# print(bd.getUser("test"))
# print(bd.deleteFile(bd.getUser("test"), "test"))
# print(bd.getUser("test"))
# print(bd.addDirectory(bd.getUser("test"), bd.createDirectory("test1"), "personal"))
# print(bd.addDirectory(bd.getUser("test"), bd.createDirectory("test2"), "personal/test1"))
# print(bd.addDirectory(bd.getUser("test"), bd.createDirectory("test3"), "personal/test1/test2")) # Error
# print(bd.addFile(bd.getUser("test"), bd.createFile("Filetest.txt", r"c:\Users\Esteb\Documents\ProyectoDriveTest"), "personal/test1/test2"))
# File: dict = bd.searchFile(bd.getUser("test"), "personal/test1/test2/Filetest.txt")
# print(bd.getFileProperties(File["absolutePath"]))
# print(bd.deleteFile(bd.getUser("test"), "personal/test1/test2/Filetest.txt"))


    
