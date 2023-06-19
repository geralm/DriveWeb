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
        
        nombre = fileData["name"]
        for file in dest["files"]:
            if file["name"] == nombre:
                return {"error": "Ya existe el nombre del archivo"}
            
        dest["files"].append(fileData)
        self.__updateUser(userData)
        return {"status": "File added successfully"}
    
    
    
    def addDirectory(self, userData: dict, directoryData: dict, path: str) -> dict:
        dest: dict = self.__searchDirectory(userData, path)
        if dest.get("error"):
            return dest
        
        nombre = directoryData["name"]
        for directory in dest["directories"]:
            if directory["name"] == nombre:
                return {"error": "Ya existe el nombre del directorio"}
            
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
    def searchFile(self, username: str, path: str, name: str) -> dict:
        listaDirectorio = path.split('/')
        lista_directorios = listaDirectorio.copy()

        # Cargar el JSON en un diccionario
        with open(self.BD_PATH) as file:
            data = json.load(file)

        # Buscar el usuario por el nombre de usuario
        usuarios = data["users"]
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["username"] == username:
                usuario_encontrado = usuario
                break

        if usuario_encontrado is None:
            return {"error": "Usuario no encontrado"}
        
        # Buscar los directorios en la estructura del usuario
        directorios = usuario_encontrado["root"]["directories"]
        for nombre_directorio in lista_directorios:
            directorio_encontrado = None
            for directorio in directorios:
                if directorio["name"] == nombre_directorio:
                    directorio_encontrado = directorio
                    directorios = directorio["directories"]
                    files = directorio["files"]
                    break

            if directorio_encontrado is None:
                return {"error": "Directorio no encontrado "+nombre_directorio}
            
        # Buscar el archivo en el último directorio
        archivos = files
        archivo_encontrado = None
        for archivo in archivos:
            if archivo["name"] == name:
                archivo_encontrado = archivo
                break

        if archivo_encontrado is None:
            return {"error": "Archivo no encontrado"}

        informacion = f"Información del archivo:\n"
        informacion += f"Nombre: {archivo_encontrado['name']}\n"
        informacion += f"Extension: txt\n"
        informacion += f"Tamaño: {archivo_encontrado['size']}\n"
        informacion += f"Fecha Creacion: {archivo_encontrado['fechaCreacion']}\n"
        informacion += f"Fecha Modificacion: {archivo_encontrado['fechaModificacion']}\n"
        informacion += f"Compartido: {archivo_encontrado['compartido']}\n\n"

        informacion += f"Contenido: {archivo_encontrado['content']}\n"
        
        
        return {"info": informacion}
    
    
    def createDirectory(self, name:str)->dict:
        return  {
                    "name": name,
                    "directories": [],
                    "files": []
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

    def createFile(self, name:str, content:str, extension: str)->dict:
        id = self.generarId()
        fecha_actual = datetime.now()
        fecha_hora_str = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
        return {
            "id": id,
            "name": name+"."+extension,
            "content": content,
            "size": self.calcularTamanoEnBytes(content),
            "fechaCreacion": fecha_hora_str,
            "fechaModificacion": fecha_hora_str,
            "compartido": False
        }
    
    def shareFile(selfe, filename: str, username: str, path: str)->dict:
        #obtener archivo
        #cambiar compartido a True
        #copiar Archivo en el drive del usuario
        #1- exisite el usuario?
        #2- no esta el archivo repetido?
        print ("en proceso")

    def modificarFile(self, username: str, path: str, name: str, newContent: str) -> dict:
        listaDirectorio = path.split('/')
        lista_directorios = listaDirectorio.copy()

        # Cargar el JSON en un diccionario
        with open(self.BD_PATH) as file:
            data = json.load(file)

        # Buscar el usuario por el nombre de usuario
        usuarios = data["users"]
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["username"] == username:
                usuario_encontrado = usuario
                break

        if usuario_encontrado is None:
            return {"error": "Usuario no encontrado"}
        
        # Buscar los directorios en la estructura del usuario
        directorios = usuario_encontrado["root"]["directories"]
        for nombre_directorio in lista_directorios:
            directorio_encontrado = None
            for directorio in directorios:
                if directorio["name"] == nombre_directorio:
                    directorio_encontrado = directorio
                    directorios = directorio["directories"]
                    files = directorio["files"]
                    break

            if directorio_encontrado is None:
                return {"error": "Directorio no encontrado "+nombre_directorio}
            
        # Buscar el archivo en el último directorio
        archivos = files
        archivo_encontrado = None
        for archivo in archivos:
            if archivo["name"] == name:
                archivo_encontrado = archivo
                break

        if archivo_encontrado is None:
            return {"error": "Archivo no encontrado"}

        fecha_actual = datetime.now()
        fecha_hora_str = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")

        archivo["content"] = newContent
        archivo["size"] = self.calcularTamanoEnBytes(newContent) 
        archivo["fechaModificacion"] = fecha_hora_str
        
        with open(self.BD_PATH, 'w') as file:
            json.dump(data, file, indent=4)

        return {"info": "Modificado con exito"}

    def deleteDirectorio(self, userData: dict, path: str) -> dict:
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
            
        for file in dest["directories"]:
            if file.get("name") == path[-1]:
                dest["directories"].remove(file)
                self.__updateUser(userData)
                return {"status": "File deleted successfully"}
        return {"error": "File not found"}
    
    def compartirFile(self, username: str, path: str, name: str, userDestino: str) -> dict:
        listaDirectorio = path.split('/')
        lista_directorios = listaDirectorio.copy()

        # Cargar el JSON en un diccionario
        with open(self.BD_PATH) as file:
            data = json.load(file)

        # Buscar el usuario por el nombre de usuario
        usuarios = data["users"]
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["username"] == username:
                usuario_encontrado = usuario
                break

        if usuario_encontrado is None:
            return {"error": "Usuario no encontrado"}
        
        # Buscar los directorios en la estructura del usuario
        directorios = usuario_encontrado["root"]["directories"]
        for nombre_directorio in lista_directorios:
            directorio_encontrado = None
            for directorio in directorios:
                if directorio["name"] == nombre_directorio:
                    directorio_encontrado = directorio
                    directorios = directorio["directories"]
                    files = directorio["files"]
                    break

            if directorio_encontrado is None:
                return {"error": "Directorio no encontrado "+nombre_directorio}
            
        # Buscar el archivo en el último directorio
        archivos = files
        archivo_encontrado = None
        for archivo in archivos:
            if archivo["name"] == name:
                archivo_encontrado = archivo
                break

        if archivo_encontrado is None:
            return {"error": "Archivo no encontrado"}


        archivo["compartido"] = True
        
        with open(self.BD_PATH, 'w') as file:
            json.dump(data, file, indent=4)

        #buscar en usuario Destino
        usuarios = data["users"]
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["username"] == userDestino:
                usuario_encontrado = usuario
                break

        if usuario_encontrado is None:
            return {"error": "Usuario Destino invalido"}
        
        result = bd.addFile(bd.getUser(userDestino), archivo, "drive")
        if "error" in result:
            archivo["compartido"] = False
            with open(self.BD_PATH, 'w') as file:
                json.dump(data, file, indent=4)
            return {"error": "error"}
        return {"info": "Compartido con exito"}
    
    def compartirDirectorio (self, username: str, path: str, name: str, userDestino: str) -> dict:
        listaDirectorio = path.split('/')
        lista_directorios = listaDirectorio.copy()

        # Cargar el JSON en un diccionario
        with open(self.BD_PATH) as file:
            data = json.load(file)

        # Buscar el usuario por el nombre de usuario
        usuarios = data["users"]
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["username"] == username:
                usuario_encontrado = usuario
                break

        if usuario_encontrado is None:
            return {"error": "Usuario no encontrado"}
        
        # Buscar los directorios en la estructura del usuario
        directorios = usuario_encontrado["root"]["directories"]
        for nombre_directorio in lista_directorios:
            directorio_encontrado = None
            for directorio in directorios:
                if directorio["name"] == nombre_directorio:
                    directorio_encontrado = directorio
                    directorios = directorio["directories"]
                   
                    break

            if directorio_encontrado is None:
                return {"error": "Directorio no encontrado "+nombre_directorio}
            
        # Buscar el archivo en el último directorio
        print(directorios)
        archivos = directorios
        archivo_encontrado = None
        for archivo in archivos:
            print (archivo["name"]+" "+name)
            if archivo["name"] == name:
                archivo_encontrado = archivo
                break

        if archivo_encontrado is None:
            return {"error": "Directorio no encontrado"}

        
        with open(self.BD_PATH, 'w') as file:
            json.dump(data, file, indent=4)

        #buscar en usuario Destino
        usuarios = data["users"]
        usuario_encontrado = None
        for usuario in usuarios:
            if usuario["username"] == userDestino:
                usuario_encontrado = usuario
                break

        if usuario_encontrado is None:
            return {"error": "Usuario Destino invalido"}
        
        result = bd.addDirectory(bd.getUser(userDestino), archivo, "drive")

        if "error" in result:
            archivo["compartido"] = False
            with open(self.BD_PATH, 'w') as file:
                json.dump(data, file, indent=4)
            return {"error": result["error"]}
        return {"info": "Compartido con exito"}
    
    def isDefaultDirectory(self, name:str)->bool:
        return name in self.DEFAULTS_DIRECTORIES
    def cargarArchivo(self, realpath, username, virtualPath, ):
        print(self.__getFileInfo(realpath))

        return {"inf"}
    def __getFileInfo(self, realpath) -> dict:
        if os.path.isfile(realpath):
            fileContent:str  = ""
            with open(realpath, 'r') as file:
                fileContent = file.read()
            fileInfo:dict = self.getFileProperties(realpath)
            fileInfo["content"] = fileContent
            return fileInfo
        else:
            return {"error": "El archivo no existe"}


# bd = BD()
bd: FileManager = FileManager()
bd.cargarArchivo(r"c:\Users\Esteb\Documents\ProyectoDriveTest\test.txt", "test", "personal")
#print (bd.searchFile("Prueba", "personal/Anidado1","esoooo.txt"))
#print(bd.createUser("Prueba",100))
#print(bd.addFile(bd.getUser("Prueba"), bd.createFile("Filetest", "Hola, esto es una prueba"), "personal"))
#print(bd.getUser("Prueba"))
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


    
