from flask import Flask, render_template, request, jsonify
from datetime import datetime

import sqlite3

LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

app = Flask(__name__)

conn = sqlite3.connect('./lib/databasewp3.db')

@app.route("/")
def qr():
    return render_template('check_in.html', greeting=get_greeting())

# makes greeting based on current time
def get_greeting():
    now = datetime.now()
    if now.hour < 12:
        return 'Goedemorgen'
    elif now.hour < 18:
        return 'Goedemiddag'
    else:
        return 'Goedenavond'


@app.route("/overzicht_docent")
def overzicht_docent():
    return render_template("overzicht_docent.html")


@app.route("/close_checkin", methods=['POST'])
def close_checkin():
    return render_template('check_in.html', message="De check-in is gesloten")

@app.route('/plan_bijeenkomst', methods=['GET', 'POST'])
def plan_bijeenkomst():
    if request.method == 'POST':
        meetingid = request.form['meetingid']
        name = request.form['name']
        datemeeting = request.form['datemeeting']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        # classid = request.form['classid']

        conn.execute("INSERT INTO meeting (meetingid, start_time, end_time, name, datemeeting) VALUES (?, ?, ?, ?, ?)",
                     (meetingid, start_time, end_time, name, datemeeting))
        conn.commit()

        return 'bijeenkomst aangemaakt'
    else:
        return render_template("bijeenkomst_plannen.html")

if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)