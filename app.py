
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "studyplannersecret"

def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        is_admin BOOLEAN DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        deadline TEXT,
        completed BOOLEAN DEFAULT 0,
        subject_id INTEGER,
        FOREIGN KEY(subject_id) REFERENCES subjects(id)
    )
    """)

    conn.commit()
    conn.close()

create_tables()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            return "Username already exists!"

        conn.close()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT tasks.id, tasks.title, tasks.deadline,
    tasks.completed, subjects.subject_name
    FROM tasks
    JOIN subjects
    ON tasks.subject_id = subjects.id
    """)

    tasks = cur.fetchall()
    conn.close()

    return render_template('dashboard.html', tasks=tasks)

@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        subject_name = request.form['subject_name']

        cur.execute(
            "INSERT INTO subjects(subject_name) VALUES (?)",
            (subject_name,)
        )

        conn.commit()

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()

    conn.close()

    return render_template('subjects.html', subjects=subjects)

@app.route('/delete_subject/<int:id>')
def delete_subject(id):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM subjects WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/subjects')

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()

    if request.method == 'POST':
        title = request.form['title']
        deadline = request.form['deadline']
        subject_id = request.form['subject_id']

        cur.execute("""
        INSERT INTO tasks(title, deadline, subject_id)
        VALUES (?, ?, ?)
        """, (title, deadline, subject_id))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('add_task.html', subjects=subjects)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        deadline = request.form['deadline']

        cur.execute("""
        UPDATE tasks
        SET title=?, deadline=?
        WHERE id=?
        """, (title, deadline, id))

        conn.commit()

        return redirect('/dashboard')

    cur.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()

    conn.close()

    return render_template('edit_task.html', task=task)

@app.route('/delete/<int:id>')
def delete_task(id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
