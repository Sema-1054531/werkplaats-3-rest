
from flask import Flask, render_template, request, redirect, session, json, jsonify
import sqlite3

app = Flask(__name__)


# Verbinding maken met de database
conn = sqlite3.connect('databasewp3.db')
c = conn.cursor()





from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Stel de route in voor het renderen van het sjabloon
@app.route('/studentenoverzicht')
def studentenoverzicht():
    return render_template('studentenoverzicht.html')

@app.route('/studentprogress')
def studentprogress():
    return render_template('studentprogress.html')


# Stel de route in voor het toevoegen van een student
@app.route('/add_student', methods=['POST'])
def add_student():
    studentmail = request.form['studentmail']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    classid = request.form['classid']
    conn = sqlite3.connect('databasewp3.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (studentmail, firstname, lastname, classid) VALUES (?, ?, ?, ?)",
              (studentmail, firstname, lastname, classid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    title = "Check in"
    if request.method == 'POST':
        # Verwerk het formulier hier
        meetingid = request.form['meetingid']
        studentid = request.form['studentid']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        progress = request.form['progress']
        checkin_date = request.form['checkin_date']
        checkin_time = request.form['checkin_time']
        checkinid = request.form['checkinid']
        subjectid = request.form['subjectid']

        # Maak verbinding met de database en voer de gegevens in
        conn = sqlite3.connect('databasewp3.db')
        c = conn.cursor()
        c.execute("INSERT INTO checkin VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (meetingid, studentid, firstname, lastname, progress, checkin_date, checkin_time, checkinid, subjectid))
        conn.commit()
        conn.close()

    return render_template('check-in-form-student.html', title=title)



@app.route('/get_students', methods=['GET'])
def get_students():
    conn = sqlite3.connect('databasewp3.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()
    return jsonify(students)

@app.route('/get_student', methods=['GET'])
def get_student():
    conn = sqlite3.connect('databasewp3.db')
    c = conn.cursor()
    c.execute("SELECT * FROM checkin")
    checkin = c.fetchall()
    conn.close()
    return jsonify(checkin)

@app.route('/delete_student/<int:studentid>', methods=['DELETE'])
def delete_student(studentid):
    conn = sqlite3.connect('databasewp3.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM students WHERE studentid = ?', (studentid,))
    conn.commit()
    return jsonify({'result': True})



# Route voor inlogpagina
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
     studentmail = request.form['studentmail']

    # connect to the database
     conn = sqlite3.connect('databasewp3.db')
     c = conn.cursor()

    # check if the student email exists in the database
     c.execute("SELECT * FROM students WHERE studentmail=?", (studentmail,))
     result = c.fetchone()
     if result is None:
         return render_template('login.html', error='Invalid student email')
     else:
         # do something with the student data, such as checking the password
         # and redirecting to a new page if the login is successful
         return render_template('dashboardstudent.html')

         # close the database connection
     conn.close()
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

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)




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

