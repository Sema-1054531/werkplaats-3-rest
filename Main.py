from flask import Flask, render_template, request, jsonify, g
from datetime import datetime

import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'lib/databasewp3.db')

LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

def get_db():
    """Opens a new database connection if there is none  yet for the current application context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

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

@app.route("/aanmelden")
def check_in_student():
    return render_template("check-in-form-student.html")

@app.route('/plan_bijeenkomst', methods=['GET', 'POST'])
def plan_bijeenkomst():
    db = get_db()

    if request.method == 'POST':
        title = request.form['title']
        datemeeting = request.form['datemeeting']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        if 'class' in request.form:
            classid = request.form['class']
        else:
            classid = None

        # validate the input
        if not title:
            return 'Vul de omschrijving van de bijeenkomt in'
        if not datemeeting:
            return 'Vul een datum in'
        if not start_time:
            return 'Vul een start tijd in'
        if not end_time:
            return 'Vul een eind tijd in'
        if start_time >= end_time:
            return 'De start tijd moet voor de eind tijd liggen'
        datemeeting = datetime.strptime(request.form['datemeeting'], '%Y-%m-%d')
        if datemeeting.date() < datetime.now().date():
            return 'De datum ligt in het verleden!'

        db.execute("INSERT INTO meeting (title, datemeeting, start_time, end_time, classid) VALUES (?, ?, ?, ?, ?)",
                   (title, datemeeting.strftime('%Y-%m-%d'), start_time, end_time, classid))
        db.commit()

        return 'bijeenkomst aangemaakt'
    classes = db.execute('SELECT * from class').fetchall()
    return render_template("bijeenkomst_plannen.html", classes=classes)


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)