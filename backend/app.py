from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "blog.db"

# --- Database setup ---
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT (datetime('now', 'localtime'))
        );
        ''')
        conn.commit()
        conn.close()
        print("Database created.")


def get_db():
    return sqlite3.connect(DB_PATH)


# --- Routes ---

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    conn = get_db()
    try:
        conn.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
        conn.commit()
        return jsonify({'message': 'User registered successfully!'})
    except Exception:
        return jsonify({'error': 'Username already exists or invalid data'}), 400
    finally:
        conn.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT id FROM users WHERE username='{username}' AND password='{password}'")
    user = cur.fetchone()
    conn.close()

    if user:
        return jsonify({'message': 'Login successful', 'user_id': user[0]})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/blogs', methods=['POST'])
def create_blog():
    data = request.json
    user_id = data.get('user_id')
    title = data.get('title')
    content = data.get('content')

    if not user_id or not title or not content:
        return jsonify({'error': 'Missing fields'}), 400

    conn = get_db()
    conn.execute(
        f"INSERT INTO blogs (user_id, title, content) VALUES ({user_id}, '{title}', '{content}')"
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Blog created successfully!'})


@app.route('/blogs', methods=['GET'])
def get_blogs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT blogs.id, blogs.title, blogs.content, users.username, blogs.timestamp
        FROM blogs, users
        WHERE blogs.user_id = users.id
        ORDER BY blogs.id DESC
    ''')
    blogs = cur.fetchall()
    conn.close()

    blog_list = []
    for b in blogs:
        blog_list.append({
            'id': b[0],
            'title': b[1],
            'content': b[2],
            'username': b[3],
            'timestamp': b[4]
        })
    return jsonify(blog_list)


@app.route('/blogs/<int:blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM blogs WHERE id={blog_id} AND user_id={user_id}")
    conn.commit()
    deleted = cur.rowcount
    conn.close()

    if deleted:
        return jsonify({'message': 'Blog deleted successfully!'})
    else:
        return jsonify({'error': 'Blog not found or unauthorized'}), 404


if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
