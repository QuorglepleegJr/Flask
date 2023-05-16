from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

app = Flask(__name__)
app.config['SECRET_KEY'] = "asoia179fna8"

VALID_LOGINS = {
    ("benjamin","password"),
    ("admin","letmein"),
}

class LoginForm(FlaskForm):

    username = StringField("Username")
    password = StringField("Password")
    submit = SubmitField("Submit")

class DemoColourForm(FlaskForm):

    base = SelectField("Colour base", choices=[
        ("red", "Red"),
        ("pink", "Pink"),
        ("purple", "Purple"),
        ("deep-purple", "Deep Purple"),
        ("indigo", "Indigo"),
        ("blue", "Blue"),
        ("light-blue", "Light Blue"),
        ("cyan", "Cyan"),
        ("teal", "Teal"),
        ("green", "Green"),
        ("light-green", "Light Green"),
        ("lime", "Lime"),
        ("yellow", "Yellow"),
        ("amber", "Amber"),
        ("orange", "Orange"),
        ("deep-orange", "Deep Orange"),
        #("brown", "Brown"),
        #("grey", "Grey"),
        #("blue-grey", "Blue Grey"),
        #("black", "Black"),
        #("white", "White"),
        #("transparent", "Transparent"),
        ])

class FullColourForm(DemoColourForm):

    modify = SelectField("Modification", choices=[
        ("lighten", "Lighten"),
        ("darken", "Darken"),
        ("accent", "Accent"),
        ])
    
    strength = SelectField("Strength", choices=[
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
    ])

@app.route('/', methods=['GET','POST'])
def home():

    return render_template("home.html")

@app.route('/login', methods=['GET','POST'])
def login():

    login_form = LoginForm()

    if login_form.is_submitted():

        username = login_form.username.data
        password = login_form.password.data

        if (username, password) in VALID_LOGINS:

            return redirect(url_for("full_access"))

        return render_template("login.html", form=login_form, login_error="Invalid login.")

    return render_template("login.html", form=login_form, login_error="")

@app.route('/demo', methods=['GET','POST'])
def demo_access():

    demo_colour = DemoColourForm()

    return render_template("demo_colour.html", form = demo_colour)
