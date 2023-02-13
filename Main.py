from flask import Flask, render_template
import datetime
# This demo glues a random database and the Flask framework. If the database file does not exist,
# a simple demo dataset will be created.
LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

app = Flask(__name__)

@app.route("/")
def checkin():
    time = datetime.datetime.now().time()
    if time >= datetime.time(6) and time < datetime.time(12):
        greeting = "Goedemorgen"
    elif time >= datetime.time(12) and time < datetime.time(18):
        greeting = "Goedemiddag"
    else:
        greeting = "Goedenavond"
    return render_template('check_in.html', greeting=greeting)


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)