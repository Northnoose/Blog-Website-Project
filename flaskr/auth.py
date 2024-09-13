import functools
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

#Oppretter en ny Blueprint for autentisering (auth)
bp = Blueprint("auth", __name__, url_prefix = "/auth")

#Definerer en rute for registrering
@bp.route('/register', methods=('GET', 'POST'))
def register():
    #Behandler POST-forespørsel for brukerregistrering
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        #Sjekker om brukernavn og passord er oppgitt
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        #Legger til brukeren i databasen hvis det ikke er noe gærent
        if error is None:
            try:
                #Hasher passordet for en sikker lagring
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                #Sender deg til innloggingssiden etter vellykket registrering
                return redirect(url_for("auth.login"))

        #Viser en feilmelding på skjermen vist det oppstår en feil
        flash(error)

    #Viser registreringsskjemaet
    return render_template('auth/register.html')

#Definerer en rute for innlogging(login)
@bp.route('/login', methods=('GET', 'POST'))
def login():
    #Behandler POST-forespørsel for innlogging
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        #Sjekker brukernavn og passord
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            #Logger inn brukeren ved å lagre brukerens ID i sesjonen
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    #Viser innloggingskjemaet
    return render_template('auth/login.html')

#En funksjon som kjøres før hver forespørsel for å laste inn innloggede bruker
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
    else: 
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id, )
        ).fetchone()

#Definerer en rute for utlogging(logout)
@bp.route("/logout")
def logout():
    #Fjerner brukeren fra sesjonen for å logge ut
    session.clear()
    return redirect(url_for("index"))

#En dekoratør for å kreve innlogging for visse ruter
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
    
        return view(**kwargs)
    return wrapped_view
