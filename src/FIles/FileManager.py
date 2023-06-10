import json 
import os
from datetime import datetime
BD_PATH = 'src/Files/bd.json'
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
def createUser(username: str) -> dict:
    try:
        with open(BD_PATH, 'r') as file:
            data = json.load(file)
            user_exists = any(user['username'] == username for user in data['users'])
            if user_exists:
                return {"error": "Username already exists"}
            else:
                data['users'].append({
                    "username": username,
                    "root": {
                        "personal": {
                            "directories": [],
                            "files": []
                        },
                        "drive": {}
                    }
                })
        
        with open(BD_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        return {"status": "User created"}
    except IOError:
        return {"error": "User not created due to file IO error"}
    except json.JSONDecodeError:
        return {"error": "User not created due to JSON decoding error"}
def getUser(username: str) -> dict:
    try:
        with open(BD_PATH, 'r') as file:
            data = json.load(file)
            user_exists = any(user['username'] == username for user in data['users'])
            if user_exists:
                return next(user for user in data['users'] if user['username'] == username)
            else:
                return {"error": "User not found"}
    except IOError:
        return {"error": "User not found due to file IO error"}
    except json.JSONDecodeError:
        return {"error": "User not found due to JSON decoding error"}
print(getUser('Esteban'))


    
