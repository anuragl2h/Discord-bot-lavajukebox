from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret!"  # needed for socketio
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")  # our frontend

# Handle messages
@socketio.on("message")
def handle_message(msg):
    print(f"Message: {msg}")
    send(msg, broadcast=True)  # broadcast to everyone

if __name__ == "__main__":
    socketio.run(app, debug=True)