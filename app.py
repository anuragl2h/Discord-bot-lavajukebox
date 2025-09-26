import os
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"

socketio = SocketIO(app, cors_allowed_origins="*")
connected_users = set()

# --- Setup SQLAlchemy engine with pooling ---
ca_cert_path = "/etc/secrets/ca.pem"
DATABASE_URL = (
    f"mysql+pymysql://{os.environ.get('DB_USER', 'root')}:"
    f"{os.environ.get('DB_PASS', '')}@"
    f"{os.environ.get('DB_HOST', 'localhost')}:"
    f"{os.environ.get('DB_PORT', '3306')}/"
    f"{os.environ.get('DB_NAME', 'chatdb')}"
    f"?ssl_ca={ca_cert_path}"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # number of connections to keep open
    max_overflow=20,       # extra connections beyond pool_size
    pool_timeout=30,       # wait time (seconds) before giving up
    pool_recycle=1800,     # recycle connections (seconds)
    echo=False             # set True for SQL logs
)

SessionLocal = sessionmaker(bind=engine)

# --- Ensure messages table exists ---
with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            message TEXT
        )
    """))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatai")
def main():
  return render_template("Main.html")
# --- Return last 50 messages for history ---
@app.route("/history")
def history():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT username, message FROM messages ORDER BY id DESC LIMIT 50"))
        rows = result.fetchall()
    return jsonify({"history": [f"{r[0]}: {r[1]}" for r in rows]})
@app.route("/submit", methods=["POST"])
def submit():
    ai_response = "❌ Something went wrong"  # Default fallback
    
    try:
        data = request.get_json()
        user_input = data.get("user_text")

        # --- Check empty input ---
        if not user_input:
            return jsonify({"ai_response": "⚠️ No input provided"}), 400

        # --- Send request to OpenRouter API ---
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                # Use env variable instead of hardcoding the key
                "Authorization": f"Bearer {os.environ.get("API")}",
                "Content-Type": "application/json",
            },
            json={   # you can use `json=` instead of `data=json.dumps(...)`
                "model": "google/gemma-3n-e2b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": user_input + " (please give fast and short answer in beautiful markdown)"
                    }
                ]
            },
            timeout=15  # prevent hanging forever
        )

        result = response.json()

        # --- Extract AI response safely ---
        if "choices" in result and len(result["choices"]) > 0:
            ai_response = result["choices"][0]["message"]["content"]
        else:
            ai_response = f"⚠️ Error from API: {result}"

    except Exception as e:
        ai_response = f"❌ Request failed: {str(e)}"

    return jsonify({"ai_response": ai_response})
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
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO messages (username, message) VALUES (:username, :msg)"),
            {"username": username, "msg": msg}
        )
    emit("message", f"{username}: {msg}", broadcast=True)

# Add a new event handler for "delete_message"
@socketio.on("delete_message")
def handle_delete_message(message_id):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM messages WHERE id = :id"), {"id": message_id})
    emit("message_deleted", message_id, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
