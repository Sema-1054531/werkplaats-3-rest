from flask import Flask, render_template, request, redirect, session, json
import sqlite3

app = Flask(__name__)


# Verbinding maken met de database
conn = sqlite3.connect('databasewp3.db')
c = conn.cursor()



# Route voor inlogpagina
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['studentmail']
        wachtwoord = request.form['wachtwoord']

        # Controleren of de ingevoerde e-mail en wachtwoord bestaan in de database
        c.execute("SELECT * FROM students WHERE studentmail = ? AND wachtwoord = ?", (email, wachtwoord))
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
@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.form.to_dict()
    with open('rooster.json', 'w') as f:
        json.dump(data, f)
    return 'Data succesvol opgeslagen in rooster.json'


if __name__ == '__main__':
    app.run(debug=True)
