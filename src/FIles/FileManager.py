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
                "extension": "txt",
                "absolutePath": "C:/Users/username/personal/file1.txt",
                "creationDate": "2020-10-10",
                "lastModification": "2020-10-10",
                "size": "10MB"
                }
            ]
            },
            "drive": {}
        }
        }
    ]
    }
"""
def getFileProperties(path:str)->dict:
    file:dict = {}
    if os.path.exists(path):
        file = {
            "name": os.path.basename(path),
            "extension": os.path.splitext(path)[1],
            "absolutePath": path,
            "creationDate": datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d %H:%M:%S"),
            "lastModification": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S"),
            "size": os.path.getsize(path)
        }
    else:
        file = {"error": "File not found"}
    return file
print(getFileProperties("C:\\Users\\Esteb\\Documents\\ProyectoDriveTest\\prueba1.txt"))


    
