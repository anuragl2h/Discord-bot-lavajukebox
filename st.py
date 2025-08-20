from flask import Flask, render_template
from flask_socketio import SocketIO, send
import os  # needed to get PORT from environment

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"  # needed for socketio
socketio = SocketIO(app, async_mode="eventlet")  # async_mode required for Vercel

@app.route("/")
def index():
    return render_template("index.html")  # our frontend

# Handle messages
@socketio.on("message")
def handle_message(msg):
    print(f"Message: {msg}")
    send(msg, broadcast=True)  # broadcast to everyone

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # get port from environment
    socketio.run(app, host="0.0.0.0", port=port)
