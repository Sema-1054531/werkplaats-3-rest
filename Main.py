
from flask import Flask, render_template, request, redirect, session, json, jsonify
import sqlite3

app = Flask(__name__)


# Verbinding maken met de database
conn = sqlite3.connect('databasewp3.db')
c = conn.cursor()



# Stel de route in voor het renderen van het sjabloon
@app.route('/')
def index():
    return render_template('studentenoverzicht.html')


# Stel de route in voor het toevoegen van een student
@app.route('/add_student', methods=['POST'])
def add_student():
    studentmail = request.form['studentmail']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    conn = sqlite3.connect('databasewp3.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (studentmail, firstname, lastname) VALUES (?, ?, ?)",
              (studentmail, firstname, lastname))
    conn.commit()
    conn.close()
    return jsonify({'success': True})



@app.route('/get_students', methods=['GET'])
def get_students():
    conn = sqlite3.connect('databasewp3.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return jsonify(students)





# Route voor inlogpagina
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['studentmail']
        wachtwoord = request.form['password']

        # Controleren of de ingevoerde e-mail en wachtwoord bestaan in de database
        c.execute("SELECT * FROM students WHERE studentmail = ? AND password = ?", (email, wachtwoord))
        student = c.fetchone()

        if student is not None:
            session['email'] = email
            return redirect('/dashboard')
        else:
            error = "Ongeldige inloggegevens. Probeer het opnieuw."
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


# Route voor dashboardpagina
@app.route('/dashboard')
def dashboard():
    # Controleren of de gebruiker is ingelogd
    if 'email' in session:
        email = session['email']
        return render_template('dashboardleeraar.html', email=email)
    else:
        return redirect('/')

@app.route('/rooster')
def show_rooster():
    return render_template('rooster.html')

@app.route('/roosteroverzicht')
def show_roosteroverzicht():
    return render_template('roosteroverzicht.html')

@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.form.to_dict()
    with open('static/rooster.json', 'w') as f:
        json.dump(data, f)
    return 'Data succesvol opgeslagen in rooster.json'


if __name__ == '__main__':
    app.run(debug=True)

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
conn = sqlite3.connect('databasewp3.db')


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

@app.route("/aanmelden" , methods=['GET', 'POST'])
def check_in_student():
    db = get_db()

    if request.method == 'POST':
        studentid = request.form['studentid']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        progress = request.form['progress']
        checkin_date = request.form['checkin_date']
        checkin_time = request.form['checkin_time']

        #validate the input
        if not studentid:
            return 'Er ging iets mis met het ophalen van je studentnummer'
        if not firstname:
            return 'Vul eerst je naam in'
        if not lastname:
            return 'Vul eerst je achternaam in'
        if not progress:
            return 'Vergeet niet aan te geven hoe je er voor staat'
        if not checkin_date:
            return 'Er ging iets mis met het ophalen van de datum van vandaag'
        if not checkin_time:
            return 'Er ging iets mis met het ophalen van de tijd'

        db.execute("INSERT INTO checkin (studentid, firstname, lastname, progress, checkin_date, checkin_time) VALUES (?, ?, ?, ?, ?, ?)",
                   (studentid, firstname, lastname, progress, checkin_date, checkin_time))
        db.commit()

        return "Je bent ingescheckt voor vandaag!"
    meeting = db.execute('SELECT * FROM meeting').fetchall()
    return render_template("check-in-form-student.html", meeting=meeting)

@app.route('/plan_bijeenkomst', methods=['GET', 'POST'])
def plan_bijeenkomst():
    db = get_db()

    if request.method == 'POST':
        title = request.form['title']
        datemeeting = request.form['datemeeting']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        classids = request.form.getlist('class[]')

        # if 'class' in request.form:
        #     classid = request.form['class']
        # else:
        #     classid = None
        if 'subject' in request.form:
            subjectid = request.form['subject']
        else:
            subjectid = None

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
        if not classids:
            return 'Selecteer welke klassen je verwacht'
        if not subjectid:
            return 'Selecteer voor welke les je deze bijeenkomst maakt'

        cursor = db.cursor()
        cursor.execute("INSERT INTO meeting (title, datemeeting, start_time, end_time, subjectid) VALUES (?, ?, ?, ?, ?)",
                   (title, datemeeting.strftime('%Y-%m-%d'), start_time, end_time, subjectid))
        meetingid = cursor.lastrowid

        for classid in classids:
            cursor.execute("INSERT INTO meeting_classes (meetingid, classid) VALUES (?, ?)", (meetingid, classid))

        db.commit()

        return 'bijeenkomst aangemaakt'
    classes = db.execute('SELECT * from class ORDER BY classname').fetchall()
    subjects = db.execute('SELECT * from subject').fetchall()
    return render_template("bijeenkomst_plannen.html", classes=classes, subjects=subjects)


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)

