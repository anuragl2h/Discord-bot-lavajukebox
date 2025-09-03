import os
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"

socketio = SocketIO(app, cors_allowed_origins="*")
connected_users = set()

# --- Connect to MySQL ---
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASS", ""),
    database=os.environ.get("DB_NAME", "chatdb"),
    port=int(os.environ.get("DB_PORT", 3306))
)
cursor = db.cursor()

# Create messages table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    message TEXT
)
""")
db.commit()

@app.route("/")
def index():
    return render_template("index.html")

# --- Return last 50 messages for history ---
@app.route("/history")
def history():
    cursor.execute("SELECT username, message FROM messages ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    return jsonify({"history": [f"{r[0]}: {r[1]}" for r in rows]})

# --- Socket.IO events ---
@socketio.on("connect")
def handle_connect():
    username = request.args.get('username', 'Guest')
    session['username'] = username
    connected_users.add(username)
    emit("update_users", list(connected_users), broadcast=True)
    print(f"{username} connected")

@socketio.on("disconnect")
def handle_disconnect():
    username = session.get('username', 'Guest')
    connected_users.discard(username)
    emit("update_users", list(connected_users), broadcast=True)
    print(f"{username} disconnected")

@socketio.on("message")
def handle_message(msg):
    username = session.get('username', 'Guest')
    print(f"{username}: {msg}")

    # Save chat message in MySQL
    cursor.execute(
        "INSERT INTO messages (username, message) VALUES (%s, %s)",
        (username, msg)
    )
    db.commit()

    emit("message", f"{username}: {msg}", broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
