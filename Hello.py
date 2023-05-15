from flask import Flask, redirect, url_for, request
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Home Page</h1>
    <p>Welcome to the home page!<p>
    '''

@app.route('/secret')
def secret():
    return '''
    <h1>GO AWAY</h1>
    <p>You're not meant to be here.<p>
    <h2>LEAVE</h2>
    '''

@app.route('/<path>')
def reject(path):
    return f'''
    <h1>ERROR 404</h1>
    <p>Page "/{path}" not found.<p>
    '''

@app.route('/admin')
def greet_admin():
    return '''
    <h1>Greetings.</h1>
    '''

@app.route('/user/<name>')
def greet_other(name):
    if name == 'benjamin':
        return redirect(url_for('greet_admin'))
    else:
        return redirect(url_for('reject', path = name))

@app.route('/details')
def details():
    print("Hearers:", request.headers)
    print("Args:", request.args)
    return '''
    <h1>Your details have been passed to the console.</h1>
    '''