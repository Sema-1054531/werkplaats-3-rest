from flask import Flask, render_template, request, jsonify, g, redirect, session, json
from datetime import datetime, timedelta

from flask_restful import Resource, Api, reqparse, fields, marshal_with

import sqlite3
import os

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'lib/databasewp3.db')
app.secret_key = os.urandom(24)
api = Api(app)

# Sessie timeout configuratie
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=604800)

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

    if 'studentmail' in session:
        return redirect('/roosteroverzicht_student')

    if request.method == 'POST':
        studentmail = request.form['studentmail']
        cursor = db.cursor()
        # Controleren of de ingevoerde e-mail en wachtwoord bestaan in de database
        cursor.execute("SELECT studentid, classid, firstname, lastname, studentmail FROM students WHERE studentmail = ?", (studentmail,))
        student = cursor.fetchone()

        if student is not None:
            studentid = student[0]
            classid = student[1]
            firstname = student[2]
            lastname = student[3]
            studentmail = student[4]

            session['studentid'] = studentid
            session['classid'] = classid
            session['firstname'] = firstname
            session['lastname'] = lastname
            session['studentmail'] = studentmail

            return redirect('/roosteroverzicht_student')
        else:
            error = "Ongeldige inloggegevens. Probeer het opnieuw."
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/login/docent', methods=['GET', 'POST'])
def login_teachers():
    db = get_db()

    if request.method == 'POST':
        teacherid = request.form['teacherid']
        cursor = db.cursor()
        # Controleren of de ingevoerde e-mail en wachtwoord bestaan in de database
        cursor.execute("SELECT teacherid FROM teacher WHERE teacherid = ?", (teacherid,))
        teacher = cursor.fetchone()

        if teacher is not None:
            session['teacherid'] = teacherid
            return redirect('/overzicht_docent')
        else:
            error = "Ongeldige inloggegevens. Probeer het opnieuw."
            return render_template('login.html', error=error)
    else:
        return render_template('login_docent.html')

@app.route('/loguit')
def logout():
    session.pop('studentmail', None)
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

class LessonsResource(Resource):
    def get(self):
        # Check if user is a student or a teacher
        if 'studentmail' in session:
            # If user is a student, get the classid from session
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            classid = session['classid']

            # Query to get meeting from students own class
            cursor.execute("SELECT * FROM meeting "
                           "INNER JOIN meeting_classes mc ON meeting.meetingid = mc.meetingid "
                           "WHERE mc.classid = ?", (classid,))
            result = cursor.fetchall()

            # Formatting meeting data
            lessons = []
            for row in result:
                lesson = {
                    'id': row[0],
                    'title': row[1],
                    'datemeeting': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'teacherid': row[5],
                    'subjectid': row[6]
                }

                # Query to get the name of teacher
                cursor.execute("SELECT firstname, lastname FROM teacher WHERE teacherid = ?", (row[5],))
                teacher = cursor.fetchone()

                # Add name of teacher to lesobject
                if teacher is not None:
                    lesson['teachername'] = teacher[0] + ' ' + teacher[1]
                else:
                    lesson['teachername'] = 'Onbekend'

                # Query to get name of subject
                cursor.execute("SELECT subjectname FROM subject WHERE subjectid = ?", (row[6],))
                subject = cursor.fetchone()

                # Add name of subject to lesobject
                if subject is not None:
                    lesson['subjectname'] = subject[0]
                else:
                    lesson['subjectname'] = 'Onbekend'

                lessons.append(lesson)

        elif 'teacherid' in session:
            # If user is a teacher, get the teacherid from session
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.cursor()
            teacherid = session['teacherid']
            cursor.execute("SELECT * FROM meeting "
                           "WHERE teacherid = ?", (teacherid,))
            result = cursor.fetchall()

            # Formatting meeting data
            lessons = []
            for row in result:
                lesson = {
                    'id': row[0],
                    'title': row[1],
                    'datemeeting': row[2],
                    'start_time': row[3],
                    'end_time': row[4],
                    'teacherid': row[5],
                    'subjectid': row[6]
                }

                # Query to get the name of teacher
                cursor.execute("SELECT firstname, lastname FROM teacher WHERE teacherid = ?", (row[5],))
                teacher = cursor.fetchone()

                # Add name of teacher to lesobject
                if teacher is not None:
                    lesson['teachername'] = teacher[0] + ' ' + teacher[1]
                else:
                    lesson['teachername'] = 'Onbekend'

                # Query to get name of subject
                cursor.execute("SELECT subjectname FROM subject WHERE subjectid = ?", (row[6],))
                subject = cursor.fetchone()

                # Add name of subject to lesobject
                if subject is not None:
                    lesson['subjectname'] = subject[0]
                else:
                    lesson['subjectname'] = 'Onbekend'

                lessons.append(lesson)

        else:
            # If user is not logged in or is not a student or teacher, return an error
            return jsonify({'error': 'Unauthorized access'}), 401

        # close connection with database
        cursor.close()
        conn.close()

        return jsonify({'lessons': lessons})

api.add_resource(LessonsResource, '/api/lessons')


@app.route("/overzicht_docent")
def overzicht_docent():
    if 'teacherid' in session:
        teacherid = session['teacherid']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT firstname, lastname FROM teacher WHERE teacherid = ?", (teacherid,))
        teacher = cursor.fetchone()
        if teacher is not None:
            firstname, lastname = teacher
            name = f"{firstname} {lastname}"
            return render_template('overzicht_docent.html', name=name)
    return redirect('/login/docent')


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


@app.route("/check-in" , methods=['GET', 'POST'])
def check_in_student():
    db = get_db()

    if request.method == 'POST':
        studentid = request.form['studentid']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        progress = request.form['progress']
        checkin_date = request.form['checkin_date']
        checkin_time = request.form['checkin_time']
        meetingid = request.form['meetingid']

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

        db.execute("INSERT INTO checkin (studentid, firstname, lastname, progress, checkin_date, checkin_time, meetingid) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (studentid, firstname, lastname, progress, checkin_date, checkin_time, meetingid))
        db.commit()

        return "Je bent ingescheckt voor vandaag!"
    meetingid = request.args.get('meetingid') or request.form.get('meetingid')
    meeting = db.execute('SELECT * FROM meeting').fetchall()
    return render_template("check-in-form-student.html", meeting=meeting, meetingid=meetingid)


# API endpoint to get meetings
# class LessonsResource(Resource):
#     def get(self):
#         # connecting with database and getting classid from current student
#         conn = sqlite3.connect(app.config['DATABASE'])
#         cursor = conn.cursor()
#
#         classid = session['classid']
#
#         # Query to get meeting from students own class
#         cursor.execute("SELECT * FROM meeting "
#                        "INNER JOIN meeting_classes mc ON meeting.meetingid = mc.meetingid "
#                        "WHERE mc.classid = ?", (classid,))
#         result = cursor.fetchall()
#
#         # Formatting meeting data
#         lessons = []
#         for row in result:
#             lesson = {
#                 'id': row[0],
#                 'title': row[1],
#                 'datemeeting': row[2],
#                 'start_time': row[3],
#                 'end_time': row[4],
#                 'teacherid': row[5],
#                 'subjectid': row[6]
#             }
#
#             # Query to get the name of teacher
#             cursor.execute("SELECT firstname, lastname FROM teacher WHERE teacherid = ?", (row[5],))
#             teacher = cursor.fetchone()
#
#             # Add name of teacher to lesobject
#             if teacher is not None:
#                 lesson['teachername'] = teacher[0] + ' ' + teacher[1]
#             else:
#                 lesson['teachername'] = 'Onbekend'
#
#             # Query to get name of subject
#             cursor.execute("SELECT subjectname FROM subject WHERE subjectid = ?", (row[6],))
#             subject = cursor.fetchone()
#
#             # Add name of subject to lesobject
#             if subject is not None:
#                 lesson['subjectname'] = subject[0]
#             else:
#                 lesson['subjectname'] = 'Onbekend'
#
#             lessons.append(lesson)
#
#         # close connection with database
#         cursor.close()
#         conn.close()
#
#         return jsonify({'lessons': lessons})
#
# api.add_resource(LessonsResource, '/api/lessons')

@app.route('/roosteroverzicht_student')
def rooster_student():
    # check if student is logged in
    if 'studentmail' in session:
        studentmail = session['studentmail']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT firstname, lastname FROM students WHERE studentmail = ?", (studentmail,))
        student = cursor.fetchone()
        if student is not None:
            firstname, lastname = student
            name = f"{firstname} {lastname}"
            return render_template('roosteroverzicht_student.html', name=name)
    return redirect('/login')



if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)

