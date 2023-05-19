from flask import Flask, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


app = Flask(__name__)
app.config['SECRET_KEY'] = '19dnoasb3a'

ACCESS_CODE = "Pink"

class User():

    __users = {}

    def exists(username):

        return User.__users.get(username, None) is not None

    def get_password(username):

        desired = User.__users.get(username, None)

        if desired is not None:

            return desired.__password
    
        return None

    def __init__(self, realname, username, password):

        self.__realname = realname
        self.__username = username
        self.__password = password

        User.__users[username] = self
    
    

class LoginForm(FlaskForm):

    username = StringField("Username")
    password = StringField("Password")
    submit = SubmitField("Login")

class RegisterForm(LoginForm):

    realname = StringField("Real Name")
    confirm_pass = StringField("Re-enter Password")
    code = StringField("Access Code")
    submit = SubmitField("Register")

@app.route('/', methods=['GET', 'POST'])
def welcome():

    # Unimplemented

    return ''''''

@app.route('/register', methods=['GET', 'POST'])
def register():

    register_form = RegisterForm()

    if register_form.is_submitted():

        access_code = register_form.code.data

        if access_code != ACCESS_CODE:

            return render_template("register.html", form=register_form, error="Access code incorrect.")

        username = register_form.username.data

        if User.exists(username):

            return render_template("register.html", form=register_form, error="Username already exists.")
        
        password = register_form.password.data
        confirm_pass = register_form.confirm_pass.data

        if password != confirm_pass:

            return render_template("register.html", form=register_form, error="Passwords do not match.")
        
        realname = register_form.realname.data

        User(realname, username, password)

        session["username"] = username

        return redirect(url_for("welcome"))

    else:

        return render_template("register.html", form=register_form, error="")

@app.route('/login', methods=['GET','POST'])
def login():

    login_form = LoginForm()

    if login_form.is_submitted():

        username = login_form.username.data
        
        if not User.exists(username):

            return render_template("login.html", form=login_form, error="User does not exist.")
        
        password = login_form.password.data

        if password != User.get_password(username):

            return render_template("login.html", form=login_form, error="Incorrect password.")

        session["username"] = username

        return redirect(url_for("welcome"))

    else:

        return render_template("login.html", form=login_form, error="")

User("The Administrator", "admin", "monkeyintospace")