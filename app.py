import os
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"

socketio = SocketIO(app, cors_allowed_origins="*")
connected_users = set()

# --- Connect to MySQL with SSL ---

def get_db_connection():
    """Establishes a secure connection to the MySQL database with SSL, using a single certificate for verification."""
    ssl_cert_path = os.environ.get("DB_SSL_CERT")

    if ssl_cert_path:
        # Use the single certificate path as the CA to verify the server
        ssl_args = {'ca': ssl_cert_path}
        print(f"Attempting SSL connection using certificate at {ssl_cert_path}")
        return pymysql.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASS", ""),
            database=os.environ.get("DB_NAME", "chatdb"),
            port=int(os.environ.get("DB_PORT", 3306)),
            autocommit=True,
            ssl=ssl_args
        )
    else:
        # Fallback to a non-SSL connection if no certificate path is provided
        print("No SSL certificate path provided. Connecting without SSL.")
        return pymysql.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASS", ""),
            database=os.environ.get("DB_NAME", "chatdb"),
            port=int(os.environ.get("DB_PORT", 3306)),
            autocommit=True
        )

def initialize_database():
    """Creates the messages table if it doesn't already exist."""
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                message TEXT
            )
        """)
        db.commit()
        print("Database and 'messages' table initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Call this function once at application startup
initialize_database()

# --- Flask routes and SocketIO handlers ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT username, message FROM messages ORDER BY id DESC LIMIT 50")
    rows = cursor.fetchall()
    return jsonify({"history": [f"{r[0]}: {r[1]}" for r in rows]})

@socketio.on("connect")
def handle_connect():
    username = session.get('username', 'Guest')
    if username not in connected_users:
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
    db = get_db_connection()
    cursor = db.cursor()
    username = session.get('username', 'Guest')
    print(f"{username}: {msg}")
    cursor.execute(
        "INSERT INTO messages (username, message) VALUES (%s, %s)",
        (username, msg)
    )
    db.commit()
    new_message_id = cursor.lastrowid
    emit("message", f"{username}: {msg}", broadcast=True)

@socketio.on("delete_message")
def handle_delete_message(message_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM messages WHERE id = %s", (message_id,))
    db.commit()
    emit("message_deleted", message_id, broadcast=True)

# Main application entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)