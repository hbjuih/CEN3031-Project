import sqlite3
from flask import Flask, flash, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user= get_db().execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return {'current_user': user}

@app.route('/')
def home():
    return render_template('landing-page.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/plans')
def plans():
    return render_template('plans.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        db.close()

        if user:
            session['user_id'] = user['id']
            return redirect('/')
        flash("Wrong email or password. Please try again.", "error")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('signup.html')

        db = get_db()
        existing_user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            flash("Email already registered.", "error")
            return render_template('signup.html')

        db.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        db.commit()
        db.close()

        flash("Account created successfully. Please log in.", "success")
        return redirect('/login')

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)