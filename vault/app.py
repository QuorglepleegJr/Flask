from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

from sqlite3 import connect, OperationalError

from sys import exit

app = Flask(__name__)
app.config['SECRET_KEY'] = '19dnoasb3a'

ACCESS_CODE = "Pink"

class UserDB():
    
    '''
    Static class storing records of users.
    Shouldn't be instatiated (won't throw an error, but does nothing).
    The admin username cannot be deleted, although it contains no extra permissions,
        it acts as a proof-of-concept.
    '''

    __connection = None
    __cursor = None

    def initialise():

        # Connect to the DB

        UserDB.__connection = connect("vault/users.db", check_same_thread=False)

        UserDB.__cursor = UserDB.__connection.cursor()

        # Create the user table if it doesn't already exist

        UserDB.__cursor.execute('''
            SELECT count(name) FROM sqlite_master WHERE type='table' AND name='users';
            ''')
        
        if UserDB.__cursor.fetchone()[0] != 1:

            UserDB.__cursor.execute('''
                CREATE TABLE users(
                USERNAME TEXT PRIMARY KEY NOT NULL,
                REALNAME TEXT NOT NULL,
                PASSWORD TEXT NOT NULL,
                ADMIN BOOLEAN
                );
                ''')
        
        # Create the admin entry if it doesn't already exist

        UserDB.__cursor.execute('''
            SELECT count(username) FROM users WHERE username='admin';
            ''')
        
        if UserDB.__cursor.fetchone()[0] != 1:

            UserDB.__cursor.execute('''
                INSERT INTO users VALUES
                    ('admin', 'Administrator', 'pass', 1);
                ''')
        
        UserDB.__connection.commit()
    
    def close():

        UserDB.__connection.commit()
        UserDB.__connection.close()

    def exists(username):

        try:

            UserDB.__cursor.execute('''
                SELECT count(username) FROM users WHERE username=?;
                ''', (username,))
            
            return UserDB.__cursor.fetchone()[0] == 1
        
        except OperationalError as op_e:

            print(f"Caution: Operational Error found when checking if entry {username} exists")
            print("DETAILS:", op_e)
    
    def is_admin(username):

        if UserDB.exists(username):

            try:

                UserDB.__cursor.execute('''
                    SELECT admin FROM users WHERE username=?;
                    ''', (username,))
                
                return UserDB.__cursor.fetchone()[0] == 1
            
            except OperationalError as op_e:

                print(f"Caution: Operational Error found when checking if entry {username} is an administrator")
                print("DETAILS:", op_e)
        
        return None

    def get_password(username):

        if UserDB.exists(username):

            try:

                UserDB.__cursor.execute('''
                    SELECT password FROM users WHERE username=?;
                    ''', (username,))
                
                return UserDB.__cursor.fetchone()[0]
            
            except OperationalError as op_e:

                print(f"Caution: Operational Error found when checking if entry {username} exists")
                print("DETAILS:", op_e)
        
        return None

    def get_realname(username):

        if UserDB.exists(username):

            try:

                UserDB.__cursor.execute('''
                    SELECT realname FROM users WHERE username=?;
                    ''', (username,))
                
                return UserDB.__cursor.fetchone()[0]
            
            except OperationalError as op_e:

                print(f"Caution: Operational Error found when checking if entry {username} exists")
                print("DETAILS:", op_e)
    
        return None

    def get_all_records():

        try:

            UserDB.__cursor.execute('''
                SELECT * FROM users;
                ''')

            return UserDB.__cursor.fetchall()
    
        except OperationalError as op_e:

            print(f"Caution: Operational Error found when retreiving all records")
            print("DETAILS:", op_e)

    def promote(username):

        try:

            UserDB.__cursor.execute('''
                UPDATE users SET admin=1 WHERE username=?;
                ''', (username,))
        
        except OperationalError as op_e:

            print(f"Caution: Operational Error found when promoting entry {username} to admin")
            print("DETAILS:", op_e)
    
    def demote(username):

        try:

            UserDB.__cursor.execute('''
                UPDATE users SET admin=0 WHERE username=?;
                ''', (username,))
        
        except OperationalError as op_e:

            print(f"Caution: Operational Error found when demoting entry {username} from admin")
            print("DETAILS:", op_e)

    def add(realname, username, password):

        try:

            UserDB.__cursor.execute('''
                INSERT INTO users VALUES
                    (?, ?, ?, False);
                ''', (username, realname, password,))
            
            UserDB.__connection.commit()
        
        except OperationalError as op_e:

            print(f"Caution: Operational Error found when adding entry {username} to database")
            print("DETAILS:", op_e)

    def remove(username):

        if UserDB.exists(username):

            try:
                
                UserDB.__cursor.execute('''
                    DELETE FROM users WHERE username=?;
                    ''', (username,))
                
                UserDB.__connection.commit()
            
            except OperationalError as op_e:

                print(f"Caution: Operational Error found when removing entry {username} from database")
                print("DETAILS:", op_e)

class LoginForm(FlaskForm):

    username = StringField("Username")
    password = StringField("Password")
    submit = SubmitField("Login")

class RegisterForm(LoginForm):

    realname = StringField("Real Name")
    confirm_pass = StringField("Re-enter Password")
    code = StringField("Access Code")
    submit = SubmitField("Register")

@app.route('/', methods=['GET','POST'])
def home():

    return redirect(url_for('content'))

@app.route('/content', methods=['GET', 'POST'])
def content():

    if 'username' in session:

        username = session['username']

        if UserDB.exists(username):

            return render_template("content.html", \
                user=UserDB.get_realname(username), admin=UserDB.is_admin(username))

    return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():

    register_form = RegisterForm()

    if register_form.is_submitted():

        access_code = register_form.code.data

        if access_code != ACCESS_CODE:

            return render_template("register.html", form=register_form, error="Access code incorrect.")

        username = register_form.username.data

        if UserDB.exists(username):

            return render_template("register.html", form=register_form, error="Username already exists.")
        
        password = register_form.password.data
        confirm_pass = register_form.confirm_pass.data

        if password != confirm_pass:

            return render_template("register.html", form=register_form, error="Passwords do not match.")
        
        realname = register_form.realname.data

        UserDB.add(realname, username, password)

        session['username'] = username

        return redirect(url_for("content"))

    else:

        return render_template("register.html", form=register_form, error="")

@app.route('/login', methods=['GET','POST'])
def login():

    login_form = LoginForm()

    if login_form.is_submitted():

        username = login_form.username.data
        
        if not UserDB.exists(username):

            return render_template("login.html", form=login_form, error="User does not exist.")
        
        password = login_form.password.data

        if password != UserDB.get_password(username):

            return render_template("login.html", form=login_form, error="Incorrect password.")

        session["username"] = username

        return redirect(url_for("content"))

    else:

        return render_template("login.html", form=login_form, error="")

@app.route('/admin', methods=['GET','POST'])
def admin():

    if 'username' in session:

        if UserDB.is_admin(session['username']):

            info = UserDB.get_all_records()

            return render_template("admin.html", users=info)
    
    return redirect(url_for("login"))

@app.route('/delete_user', methods=['GET','POST'])
def delete_user():

    if 'username' in session:

        if UserDB.is_admin(session['username']):

            if "user" in request.args:

                UserDB.remove(request.args['user'])
    
    return redirect(url_for("admin"))

@app.route('/promote', methods=['GET','POST'])
def promote():

    if 'username' in session:

        if UserDB.is_admin(session['username']):

            if "user" in request.args:

                UserDB.promote(request.args['user'])
    
    return redirect(url_for("admin"))

@app.route('/demote', methods=['GET','POST'])
def demote():

    if 'username' in session:

        if UserDB.is_admin(session['username']):

            if "user" in request.args:

                UserDB.demote(request.args['user'])
    
    return redirect(url_for("admin"))

@app.route('/logout', methods=['GET','POST'])
def logout():

    if 'username' in session:

        session.pop('username')

    return redirect(url_for("login")) 

@app.route('/delete', methods=['GET','POST'])
def delete():

    if 'username' in session:

        username = session.pop('username')

        UserDB.remove(username)

    return redirect(url_for("login"))

if __name__ == "__main__":

    UserDB.initialise()

    app.run(host="0.0.0.0", port=5000)

    UserDB.close()

