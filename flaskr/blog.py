from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required  #Importerer dekoratøren for innloggingssjekk
from flaskr.db import get_db  #Importerer funksjonen for å hente databaseforbindelsen

#Oppretter en ny Blueprint for bloggfunksjonaliteten
bp = Blueprint("blog", __name__)

#Rute for å vise alle blogginnlegg(/)
@bp.route("/")
def index():
    db = get_db()
    #Henter alle blogginnlegg fra databasen, sortert etter opprettelsesdato. Som betyr nyest først
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    #Generer html innhold basert på 'blog/index.html' og sender med blogginnleggene
    return render_template('blog/index.html', posts=posts)
    
#Rute for å opprette nye blogginnlegg(create)
@bp.route('/create', methods=('GET', 'POST'))
@login_required  #Krever at brukeren er logget inn
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        #Sjekker om tittelen er oppgitt
        if not title:
            error = 'Title is required.'

        #Viser feilmelding hvis valideringen feiler, ellers lagrer innlegget
        if error is not None:
            flash(error)
        else:
            db = get_db()
            #Legger inn et nytt blogginnlegg i databasen
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            #Sender brukeren tilbake til hovedsiden etter lagring
            return redirect(url_for('blog.index'))

    #Generer html innhold basert på 'blog/create.html' for å opprette nytt innlegg.
    return render_template('blog/create.html')

#Hjelpefunksjon som skal finne en spesefikk bloginnlegg etter id
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    #Sjekker om innlegget eksisterer og om brukeren har rettigheter
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

#Rute for å oppdatere et eksisterende blogginnlegg(update)
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required 
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        #Oppdaterer innlegget hvis det ikke er noen feil
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            #Omdirigerer til hovedsiden etter oppdatering
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

#Rute for å slette et blogginnlegg(delete)
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required 
def delete(id):
    get_post(id)  #Henter blogginlegget for å sjekke rettigheter
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()

    return redirect(url_for('blog.index'))
