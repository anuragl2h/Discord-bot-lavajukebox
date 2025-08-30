import os
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"

# Allow cross-origin requests (important for frontend JS)
socketio = SocketIO(app, cors_allowed_origins="*")

# Track connected users
connected_users = set()

@app.route("/")
def index():
    return render_template("index.html")

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
    emit("message", f"{username}: {msg}", broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)