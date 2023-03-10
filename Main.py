from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)


# Verbinding maken met de database
conn = sqlite3.connect('databasewp3.db')
c = conn.cursor()

# Tabel voor studenten aanmaken als deze nog niet bestaat
c.execute('''CREATE TABLE IF NOT EXISTS studenten
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT NOT NULL,
              wachtwoord TEXT NOT NULL)''')
conn.commit()

# Voorbeeld studenten toevoegen
c.execute("INSERT INTO studenten (email, wachtwoord) VALUES (?, ?)", ('johndoe@student.com', 'wachtwoord123'))
c.execute("INSERT INTO studenten (email, wachtwoord) VALUES (?, ?)", ('janedoe@student.com', 'wachtwoord456'))
conn.commit()


# Route voor inlogpagina
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['studentmail']
        wachtwoord = request.form['wachtwoord']

        # Controleren of de ingevoerde e-mail bestaat in de database
        c.execute("SELECT * FROM studentmail WHERE studentmail = ?", (email,))
        student = c.fetchone()

        if student is not None and student[2] == wachtwoord:
            session['studentmail'] = emailgit
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
    if 'studentmail' in session:
        email = session['studentmail']
        return render_template('dashboard.html', email=email)
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
