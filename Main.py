from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        studentmail = request.form['studentmail']
        password = request.form['password']
        # hier dient u uw validatie logica in te voegen en controleren of de gebruikersnaam en wachtwoord geldig zijn voor Hogeschool Rotterdam
    #if studentmail == 'studentmail' and password == 'geldig_wachtwoord':
#

    #return redirect(url_for('dashboard'))
     #else:
         #error = 'Ongeldige gebruikersnaam of wachtwoord. Probeer het opnieuw.'
    return render_template('Login.html')

#@app.route('/dashboard')
#def dashboard():
 #   return "Welkom bij het dashboard van Hogeschool Rotterdam!"


if __name__ == '__main__':
    app.run(debug=True)
