from flask import Flask, redirect, url_for, request
app = Flask(__name__)

from math import sqrt, ceil

def is_prime(n):

    try:

        if int(n) < 2: return False

        for i in range(2, ceil(sqrt(int(n)))):

            if n%i == 0: return False
        
        return True

    except ValueError:

        return False

@app.route('/')
def home():
    return '''
    <p>Password protected content. Provide a request with suitable arguments.<p>
    '''

@app.route('/password/hint')
def hint():
    return '''
    <h1>What is the average air speed of an unladen swallow?</h1>
    '''

@app.route('/password')
def password_check():

    try:

        attempt = request.args["pass"]

        if attempt == "African or European?":

            return redirect(url_for('successful', redirect="Bridge"))

        else:

            return '''
            <h1>Wrong. Off the bridge with you.</h1>
            '''
    
    except KeyError:

        return '''
        <h1>At least try with the password.</h1>
        '''

@app.route('/content')
def successful():

    try:

        redirect_from = request.args["redirect"]

        if redirect_from == "Bridge":

            return '''
            <p>Well of course I don't know that. You may cross.<p>
            '''

        if redirect_from == "Prime":

            return '''
            <p>That is indeed prime.<p>
            '''
        
    except KeyError:

        pass

    return '''
    <h1>Cheaters never prosper.</h1>
    '''

@app.route('/prime')
def prime_input():

    try:

        value = request.args["n"]

        if is_prime(value):

            return redirect(url_for('successful', redirect = "Prime"))
        
        return '''
        <h1>That isn't prime.</h1>
        '''
    
    except KeyError:

        return '''
        <p>There's supposed to be a number in n here.<p>
        '''