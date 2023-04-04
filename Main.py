from flask import Flask, render_template, request, jsonify, g, redirect, session, json
from datetime import datetime

from database import get_db

import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'lib/databasewp3.db')
app.secret_key = os.urandom(24)

LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


conn = sqlite3.connect('lib/databasewp3.db')


@app.route("/")
def index():
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


# Route voor inlogpagina
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()

    if request.method == 'POST':
        studentid = request.form['studentid']
        cursor = db.cursor()
        # Controleren of de ingevoerde e-mail en wachtwoord bestaan in de database
        cursor.execute("SELECT studentid FROM students WHERE studentid = ?", (studentid,))
        student = cursor.fetchone()

        if student is not None:
            session['studentid'] = studentid
            return redirect('/roosteroverzicht_student')
        else:
            error = "Ongeldige inloggegevens. Probeer het opnieuw."
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/loguit')
def logout():
    session.pop('studentid', None)
    return redirect('/login')


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


@app.route("/overzicht_docent")
def overzicht_docent():
    return render_template("overzicht_docent.html")


@app.route("/close_checkin", methods=['POST'])
def close_checkin():
    return render_template('check_in.html', message="De check-in is gesloten")


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


@app.route('/api/roosteroverzicht_student/<int:studentid>')
def api_rooster_student(studentid):
    # check if student is logged in
    if 'studentid' in session and session['studentid'] == studentid:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT meeting.title, meeting.datemeeting, meeting.start_time, meeting.end_time, teacher.firstname, subject.subjectname
            FROM meeting
            JOIN meeting_classes ON meeting.meetingid = meeting_classes.meetingid
            JOIN students ON meeting_classes.classid = students.classid
            JOIN teacher ON meeting.teacherid = teacher.teacherid
            JOIN subject ON meeting.subjectid = subject.subjectid
            WHERE students.studentid = ?
            ORDER BY meeting.datemeeting, meeting.start_time
        """, (studentid,))
        rooster = cursor.fetchall()
        rooster_dict = []
        for row in rooster:
            rooster_dict.append({
                'title': row[0],
                'datemeeting': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'teacher': row[4],
                'subject': row[5]
            })
        return jsonify(rooster_dict)
    else:
        return jsonify({'message': 'Unauthorized access.'}), 401

@app.route('/roosteroverzicht_student')
def rooster_student():
    # check if student is logged in
    if 'studentid' in session:
        studentid = session['studentid']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT firstname, lastname FROM students WHERE studentid = ?", (studentid,))
        student = cursor.fetchone()
        if student is not None:
            firstname, lastname = student
            name = f"{firstname} {lastname}"
            return render_template('roosteroverzicht_student.html', name=name)
    return redirect('/login')


if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)

