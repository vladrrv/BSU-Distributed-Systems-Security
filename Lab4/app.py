from flask import Flask, flash, redirect, render_template, request, session, abort
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html', wrong=session.get('wrong', False))
    else:
        return "Hello!"


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['wrong'] = False
        session['logged_in'] = True
    else:
        session['wrong'] = True
        flash('wrong password!')
    return home()


if __name__ == "__main__":
    app.run(debug=True)
