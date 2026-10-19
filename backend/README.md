Flask + SQLite API

Run it

pip install -r backend/requirements.txt
python backend/app.py

The Tests
python -m pytest backend


## Database

It's in schema.sql

- **users:** `id`, `username` (unique, case-insensitive), `email`, `password`, `role` (`member` by default, or `admin`), `created_at`
- **notes:** `id`, `owner_id`, `title`, `content` (HTML), `is_public`, `created_at`, `updated_at`

## API

All requests and responses are JSON. Errors look like `{"error": "message"}`.

| Method | URL | Body | Who | Result |
|---|---|---|---|---|
| POST | `/api/signup` | `{username, email, password}` | anyone | `201` user, `400` bad input, `409` username taken |
| POST | `/api/login` | `{username, password, remember}` | anyone | `200` user + session cookie, `401` wrong login |
| POST | `/api/logout` | none | anyone | `200` |
| GET | `/api/me` | none | logged in | `200` current user, `401` if not logged in |
| GET | `/api/notes` | none | logged in | `200` list of your notes |
| POST | `/api/notes` | `{title, content}` | logged in | `201` new note |
| GET | `/api/notes/<id>` | none | owner, or anyone if public | `200` note, `403`, `404` |
| PUT | `/api/notes/<id>` | any of `{title, content, is_public}` | owner | `200` updated note, `403` |
| DELETE | `/api/notes/<id>` | none | owner | `200`, `403` |
| GET | `/api/admin/users` | none | admin | `200` list of users, `403` |

username required, password at least 6 characters

changing from localStorage to the database, something like this:

const response = await fetch("/api/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password })
});
const data = await response.json();
if (!response.ok) {
    showMessage(data.error, "white");
}




All acount are admin need to do run this

sqlite3 backend/notesy.db "UPDATE users SET role = 'admin' WHERE username = 'betty';"


