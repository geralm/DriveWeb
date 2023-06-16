from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash
from src.Files.FileManager import FileManager
from urllib.parse import unquote
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
    usuario = request.form ['usuario']
    jsonResultado = request.form['jsonResultado']
    jsonResultado = eval(jsonResultado)
    stringDirectorio = request.form['stringDirectorio']
    nombreDirectorio = request.form['directorio']
    listaDirectorio = stringDirectorio.split('/')
    listaTentativa = listaDirectorio.copy()
    listaTentativa.append(nombreDirectorio)
    if listaTentativa[0] == '':
        listaTentativa.pop(0)
    directorioActual = jsonResultado["root"]
    for carpeta in listaTentativa:
        for index, directory in enumerate(directorioActual['directories']):
            if directory['name'] == carpeta:   
                directorioActual = directorioActual['directories'][index]
                break
        else:
            arbol = generar_arbol(directorioActual)
            return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Nombre de carpeta inválido", infoArchivo = "", usuario = nombreUsuario   )
    stringDirectorio = "/".join(listaTentativa)
    arbol = generar_arbol(directorioActual)
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
    directorioActual = jsonResultado["root"]
    for carpeta in listaTentativa:
        for index, directory in enumerate(directorioActual['directories']):
            if directory['name'] == carpeta:   
                directorioActual = directorioActual['directories'][index]
                break
        else:
            arbol = generar_arbol(directorioActual)
            return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Nombre de carpeta inválido", usuario = nombreUsuario, infoArchivo = ""    )
    stringDirectorio = "/".join(listaTentativa)
    arbol = generar_arbol(directorioActual)
    return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = ""    )
    


@views.route("/verArchivo", methods = ['POST'])
def verArchivo():
    nombreUsuario = request.form ['usuario']
    arbol = request.form ['arbol']
    nombreArchivo = request.form['archivo']
    stringDirectorio = request.form['stringDirectorio']
    jsonResultado = request.form['jsonResultado']
    bd: FileManager = FileManager()
    resultado = bd.searchFile(nombreUsuario, stringDirectorio, nombreArchivo) 
    if "error" in resultado:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado,stringDirectorio = stringDirectorio, error = "Archivo no encontrado", usuario = nombreUsuario, infoArchivo = ""   )
    else:
        return render_template('drive.html', drive = arbol, jsonResultado = jsonResultado, stringDirectorio = stringDirectorio, usuario = nombreUsuario, infoArchivo = resultado["info"]  )


def generar_arbol(json, nivel=0):
    arbol = ''
    for directorio in json['directories']:
        arbol += '     ' * nivel + '├── ' + directorio['name'] + '/\n'
        arbol += generar_arbol(directorio, nivel + 1)
    for archivo in json['files']:
        arbol += '     ' * nivel + '├── ' + archivo['name'] + '\n'
    return arbol