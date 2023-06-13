from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, send


app = Flask(__name__)
app.config['SECRET_KEY']= 'secret'
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    isUserExist:bool = False
    if request.method == 'POST':
        username = request.form['username']
        #Buscar en el archivo de usuarios si existe
        
        if(isUserExist):
            return redirect(url_for('chat', username=username))
        else:
            return render_template('index.html', error='Unvalid user, plesase try again')
    return render_template('index.html')
if __name__ == '__main__':
    socketio.run(app, debug=True)
