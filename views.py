from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from src.Files.FileManager import FileManager
from urllib.parse import unquote
import html
import ast, json

views = Blueprint(__name__,"views")

@views.route("/")
def home():
    return render_template('index.html')

@views.route("/getRegistro", methods=['GET'])
def getRegistro():
    return render_template('registrar.html')

@views.route("/crearCuenta", methods = ['POST'])
def crearCuenta():
    nombreUsuario = request.form['username']
    tamanioDrive = request.form['tamanio']
    bd: FileManager = FileManager()
    resultado = bd.createUser(nombreUsuario,tamanioDrive)
    if "error" in resultado:
        errorRegistro = "No se pudo crear la cuenta. Por favor, revise las credenciales"
    else:
        errorRegistro = "Se creó la cuenta exitosamente"
    return render_template('index.html', error = errorRegistro )

@views.route("/iniciarSesion", methods = ['POST'])
def iniciarSesion():
    nombreUsuario = request.form['username']
    bd: FileManager = FileManager()
    resultado = bd.getUser(username=nombreUsuario)
    if "error" in resultado:
        errorInicioSesion = "Error al iniciar sesión. Por favor, revise las credenciales"
        return render_template('index.html', error = errorInicioSesion)
    else:
        errorInicioSesion = "Se ingresó exitosamente"
        arbol = generar_arbol(resultado['root'])
        return render_template('drive.html', drive = arbol, jsonResultado = resultado, usuario = nombreUsuario )
    
@views.route("/entrarDirectorio", methods = ['POST'])
def entrarDirectorio():
    nombreUsuario = request.form ['usuario']
    jsonResultado = request.form['jsonResultado']
    jsonResultado = eval(jsonResultado)
    stringDirectorio = request.form['stringDirectorio']
    nombreDirectorio = request.form['directorio']
    listaDirectorio = stringDirectorio.split('/')
    listaTentativa = listaDirectorio.copy()
    listaTentativa.append(nombreDirectorio)
    if listaTentativa[0] == '':
        listaTentativa.pop(0)
    resultado = obtenerJsonRelativo(listaTentativa,nombreUsuario)
    arbol = resultado[1]
    if not resultado[0]:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Nombre de carpeta inválido", infoArchivo = "", usuario = nombreUsuario   )
    stringDirectorio = "/".join(listaTentativa)
    return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, infoArchivo = "", usuario = nombreUsuario   )

@views.route("/salirDirectorio", methods = ['POST'])
def salirDirectorio():
    nombreUsuario = request.form ['usuario']
    jsonResultado = request.form['jsonResultado']
    jsonResultado = eval(jsonResultado)
    stringDirectorio = request.form['stringDirectorio']
    listaDirectorio = stringDirectorio.split('/')
    listaTentativa = listaDirectorio.copy()
    if listaTentativa[0] == '':
        listaTentativa.pop(0)
    if len(listaTentativa) > 0:
        listaTentativa.pop(-1)
    resultado = obtenerJsonRelativo(listaTentativa,nombreUsuario)
    arbol = resultado[1]
    if not resultado[0]:
            return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Nombre de carpeta inválido", usuario = nombreUsuario, infoArchivo = ""    )
    stringDirectorio = "/".join(listaTentativa)
    return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = ""    )
    


@views.route("/verArchivo", methods = ['POST', 'GET'])
def verArchivo():
    nombreUsuario = request.form ['usuario']
    arbol = request.form ['arbol']
    nombreArchivo = request.form['archivo']
    stringDirectorio = request.form['stringDirectorio']
    jsonResultado = request.form['jsonResultado']
    bd: FileManager = FileManager()
    resultado = bd.searchFile(nombreUsuario, stringDirectorio, nombreArchivo) 
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Archivo no encontrado", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = resultado["info"]  )

@views.route("/crearArchivo", methods = ['POST'])
def crearArchivo():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']

    nombreArchivo = request.form['nombreArchivoCreacion']
    contenido = request.form['contenidoArchivoCreacion']
    extension = request.form['extensionArchivoCreacion']
    
    bd: FileManager = FileManager()
    resultado = bd.addFile(bd.getUser(nombreUsuario), bd.createFile(nombreArchivo,contenido,extension), stringDirectorio)
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Error al crear Archivo: nombre repetido", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Archivo creado con exito" )

@views.route("/crearDirectorio", methods = ['POST'])
def crearDirectorio():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']

    nombreDirectorio = request.form['nombreDirectorioCreacion']
    
    bd: FileManager = FileManager()
    resultado = bd.addDirectory(bd.getUser(nombreUsuario), bd.createDirectory(nombreDirectorio), stringDirectorio)
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Error al crear Directorio: nombre repetido", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Directorio creado con exito" )
    

#en proceso
@views.route("/compartirArchivo", methods = ['POST'])
def compartiArchivo():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]

    usuarioDestino = request.form['nombreUsuarioCompartir']
    archivoACompartir = request.form['nombreArchivoCompartir']

    bd: FileManager = FileManager()
    resultado = bd.compartirFile(nombreUsuario, stringDirectorio, archivoACompartir, usuarioDestino)
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = resultado["error"], usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Compartido con exito" )
    
@views.route("/compartirDirectorio", methods = ['POST'])
def compartirDirectorio():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]

    archivoACompartir = request.form['nombreDirectorioCompartir']
    usuarioDestino = request.form['nombreUsuarioCompartir']

    bd: FileManager = FileManager()
    resultado = bd.compartirDirectorio(nombreUsuario, stringDirectorio, archivoACompartir, usuarioDestino)
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = resultado["error"], usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Compartido con exito" )
   
@views.route("/modificarArchivo", methods = ['POST'])
def modificarArchivo():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]

    archivoMod = request.form['archivo']
    newContent = request.form['contenidoArchivoModificado']

    bd: FileManager = FileManager()
    resultado = bd.modificarFile(nombreUsuario, stringDirectorio, archivoMod, newContent)
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Error: no existe el archivo en el directorio actual", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Modificado con exito" )
    
@views.route("/eliminarArchivo", methods = ['POST'])
def eliminarArchivo():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']
    listaDirectorio = stringDirectorio.split('/')
    

    archivoMod = request.form['archivo']

    bd: FileManager = FileManager()
    resultado = bd.deleteFile(bd.getUser(nombreUsuario), stringDirectorio+"/"+archivoMod)

    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Error: no existe el archivo en el directorio actual", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Eliminado con exito" )
    

@views.route("/eliminarDirectorio", methods = ['POST'])
def eliminarDirectorio():
    nombreUsuario = request.form ['usuario']
    stringDirectorio = request.form['stringDirectorio']
    arbol = request.form ['arbol']
    jsonResultado = request.form['jsonResultado']
    listaDirectorio = stringDirectorio.split('/')
    

    directorio = request.form['directorio']

    bd: FileManager = FileManager()
    resultado = bd.deleteDirectorio(bd.getUser(nombreUsuario), stringDirectorio+"/"+directorio)

    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Error: no existe el archivo en el directorio actual", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error = "Eliminado con exito" )
"""
Funciones del copy
"""
@views.route("/download", methods = ['POST'])
def download():
    nombreUsuario = request.form ['usuario']
    arbol = request.form ['arbol']
    nombreArchivo = request.form['nombreArchivo']
    stringDirectorio = request.form['stringDirectorio']
    jsonResultado = request.form['jsonResultado']
    rutadestino: str = request.form['rutaDestino']
    bd: FileManager = FileManager()
    resultado = bd.downloadFile(nombreUsuario, stringDirectorio, nombreArchivo, rutadestino)
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = resultado["error"], usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "", error="Descarga existosa" )
@views.route("/copiarArchivo", methods = ['POST'])
def copiar():
    nombreUsuario = request.form ['usuario']
    arbol = request.form ['arbol']
    nombreArchivo = request.form['nombreArchivo']
    rutadestino: str = request.form['ruta']
    stringDirectorio = request.form['stringDirectorio']
    jsonResultado = request.form['jsonResultado']
    bd: FileManager = FileManager()
    resultado: dict = bd.copyVV(nombreUsuario, stringDirectorio+"/"+nombreArchivo, rutadestino)
    listaDirectorio = stringDirectorio.split('/')
    arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = resultado["error"], usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "" )
@views.route("/moverArchivo", methods = ['POST'])
def mover():
    nombreUsuario = request.form ['usuario']
    arbol = request.form ['arbol']
    nombreArchivo = request.form['nombreArchivo']
    rutadestino: str = request.form['ruta']
    stringDirectorio = request.form['stringDirectorio']
    jsonResultado = request.form['jsonResultado']
    bd: FileManager = FileManager()
    resultado: dict = bd.moverVV(nombreUsuario, stringDirectorio+"/"+nombreArchivo, rutadestino)
    if "error" not in resultado:
        if bd.isFile(nombreArchivo):
            resultado: dict = bd.deleteFile(bd.getUser(nombreUsuario), stringDirectorio+"/"+nombreArchivo)
        else:
            resultado: dict = bd.deleteDirectory(bd.getUser(nombreUsuario), stringDirectorio+"/"+nombreArchivo)
        listaDirectorio = stringDirectorio.split('/')
        arbol = obtenerJsonRelativo(listaDirectorio,nombreUsuario)[1]
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = resultado["error"], usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = "" , error= "Movido con exito")
@views.route("/load", methods=['POST'])
def load():
    usuario = request.form['usuario']
    jsonResultado = request.form['jsonResultado']
    stringDirectorio = request.form['stringDirectorio']
    rutaArchivo = request.form.get('rutaArchivo')
    
    # Realizar acciones con los datos aquí
    # Por ejemplo, guardar la ruta del archivo en el servidor
    print("Ruta del archivo:", rutaArchivo)
    
    return "load"

def generar_arbol(json, nivel=0):
    arbol = ''
    for directorio in json['directories']:
        arbol += '     ' * nivel + '├── ' + directorio['name'] + '/\n'
        arbol += generar_arbol(directorio, nivel + 1)
    for archivo in json['files']:
        arbol += '     ' * nivel + '├── ' + archivo['name'] + '\n'
    return arbol

def obtenerJsonRelativo(listaDirectorios,nombreUsuario):
    bd: FileManager = FileManager()
    resultado = bd.getUser(username=nombreUsuario)
    directorioActual = resultado["root"]
    for carpeta in listaDirectorios:
        for index, directory in enumerate(directorioActual['directories']):
            if directory['name'] == carpeta:   
                directorioActual = directorioActual['directories'][index]
                break
        else:
            arbol = generar_arbol(directorioActual)
            return (False,arbol)
    arbol = generar_arbol(directorioActual)
    return (True,arbol)