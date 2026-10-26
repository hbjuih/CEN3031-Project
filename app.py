import os
import sqlite3
from datetime import timedelta
from functools import wraps

from flask import Flask, abort, g, jsonify, redirect, request, send_from_directory, session, render_template

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "backend")
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BACKEND_DIR, "notesy.db")
FRONTEND_FOLDERS = {"sign_up", "log_in", "home", "images"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)  # "Remember Me"


# database

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Makes tables if they don't exist yet."""
    db = sqlite3.connect(DATABASE)
    try:
        with open(os.path.join(BACKEND_DIR, "schema.sql")) as f:
            db.executescript(f.read())
        db.commit()
    finally:
        db.close()

def user_to_dict(row):
    return {"id": row["id"], "username": row["username"], "email": row["email"],
            "role": row["role"], "created_at": row["created_at"]}


def note_to_dict(row):
    return {"id": row["id"], "owner_id": row["owner_id"], "title": row["title"],
            "content": row["content"], "is_public": bool(row["is_public"]),
            "created_at": row["created_at"], "updated_at": row["updated_at"]}


# helpers

def error(message, status):
    return jsonify({"error": message}), status


def current_user():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return error("You need to log in first.", 401)
        g.user = user
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if g.user["role"] != "admin":
            return error("Admins only.", 403)
        return view(*args, **kwargs)
    return wrapper


def get_note_or_404(note_id):
    note = get_db().execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if note is None:
        abort(404)
    return note


def can_view(user, note):
    return note["is_public"] or (user is not None and note["owner_id"] == user["id"])


def can_edit(user, note):
    return user is not None and note["owner_id"] == user["id"]


# auth

@app.post("/api/signup")
def signup():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username:
        return error("Please enter a username.", 400)
    if not email:
        return error("Please enter an email.", 400)
    if len(password) < 6:
        return error("Password must be at least 6 characters long.", 400)

    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error("That username is already taken; please try again.", 409)

    user = db.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(user_to_dict(user)), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user is None or user["password"] != password:
        return error("Username or password is incorrect.", 401)

    session.clear()
    session["user_id"] = user["id"]
    session.permanent = bool(data.get("remember"))
    return jsonify(user_to_dict(user))


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})


@app.get("/api/me")
@login_required
def me():
    return jsonify(user_to_dict(g.user))


# notes

@app.get("/api/notes")
@login_required
def list_notes():
    rows = get_db().execute(
        "SELECT * FROM notes WHERE owner_id = ? ORDER BY updated_at DESC", (g.user["id"],)
    ).fetchall()
    return jsonify([note_to_dict(r) for r in rows])


@app.post("/api/notes")
@login_required
def create_note():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return error("A note needs a title.", 400)

    db = get_db()
    cur = db.execute(
        "INSERT INTO notes (owner_id, title, content) VALUES (?, ?, ?)",
        (g.user["id"], title, data.get("content") or ""),
    )
    db.commit()
    return jsonify(note_to_dict(get_note_or_404(cur.lastrowid))), 201


@app.get("/api/notes/<int:note_id>")
def get_note(note_id):
    note = get_note_or_404(note_id)
    if not can_view(current_user(), note):
        return error("You don't have access to this note.", 403)
    return jsonify(note_to_dict(note))


@app.put("/api/notes/<int:note_id>")
@login_required
def update_note(note_id):
    note = get_note_or_404(note_id)
    if not can_edit(g.user, note):
        return error("Only the owner can edit this note.", 403)

    data = request.get_json(silent=True) or {}
    title = (data.get("title", note["title"]) or "").strip()
    if not title:
        return error("A note needs a title.", 400)
    content = data.get("content", note["content"])
    is_public = int(bool(data.get("is_public", note["is_public"])))

    db = get_db()
    db.execute(
        "UPDATE notes SET title = ?, content = ?, is_public = ?, updated_at = CURRENT_TIMESTAMP "
        "WHERE id = ?",
        (title, content, is_public, note_id),
    )
    db.commit()
    return jsonify(note_to_dict(get_note_or_404(note_id)))


@app.delete("/api/notes/<int:note_id>")
@login_required
def delete_note(note_id):
    note = get_note_or_404(note_id)
    if not can_edit(g.user, note):
        return error("Only the owner can delete this note.", 403)

    db = get_db()
    db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    return jsonify({"message": "Note deleted."})


# admin

@app.get("/api/admin/users")
@admin_required
def admin_list_users():
    rows = get_db().execute("SELECT * FROM users ORDER BY id").fetchall()
    return jsonify([user_to_dict(r) for r in rows])


# frontend

@app.get("/<folder>/<path:filename>")
def frontend(folder, filename):
    # Only the frontend folders are served, never backend/ (keeps notesy.db private).
    if folder not in FRONTEND_FOLDERS:
        abort(404)
    return send_from_directory(os.path.join(PROJECT_DIR, folder), filename)


@app.errorhandler(404)
def not_found(_error):
    if request.path.startswith("/api/"):
        return error("Not found.", 404)
    return "Page not found", 404

@app.route('/')
def home():
    return render_template('landing-page.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/plans')
def plans():
    return render_template('plans.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/home')
# @login_required Uncomment Once Finished
def home_page():
    #user = g.user
    #db = get_db()
    #recent_notes = db.execute("SELECT * FROM notes WHERE owner_id = ? ORDER BY updated_at DESC LIMIT 3", (user["id"],)).fetchall()
    return render_template('home.html')
    #return render_template('home.html', recent_notes=recent_notes, current_user=user) Delete Above and Uncomment This

@app.route("/search")
@login_required
def search():
    q = request.args.get("query", "").strip()

    notes, notebooks, tags = [], [], []
    # Finish This.

    return render_template("search,html")

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/tags')
def tags_page():
    return render_template("tags.html")

@app.route('/shared')
def shared():
    return render_template("shared.html")

@app.route('/notes')
def notes_page():
    return render_template("notes.html")

@app.route('/notebooks')
def notebooks_page():
    return render_template("notebooks.html")

@app.route('/account')
def account_page():
    return render_template("account.html")

@app.route('/account-edit')
def account_edit_page():
    return render_template("account-edit.html")

init_db()

if __name__ == "__main__":
    app.run(debug=True)
