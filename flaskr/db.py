import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

#Funksjon for å hente eller opprette en databaseforbindelse
def get_db():
    if 'db' not in g:
        #Oppretter en ny databaseforbindelse og lagrer den i g hvis den ikke allerede eksisterer
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],  
            detect_types=sqlite3.PARSE_DECLTYPES  
        )
        g.db.row_factory = sqlite3.Row  #Gjør det mye mere lesbar, siden man får kolonner man kan søke etter
    return g.db

#Funksjon for å lukke databaseforbindelsen
def close_db(e=None):
    db = g.pop('db', None)  #Fjerner og returnerer 'db' fra g hvis den eksisterer

    if db is not None:
        db.close()  #Lukker databaseforbindelsen som fortsatt er åpen

#Funksjon for å initialisere databasen ved å kjøre SQL-skript
def init_db():
    db = get_db()  #Henter databaseforbindelsen

    #Åpner og kjører SQL-skriptet definert i 'schema.sql' for å opprette tabeller
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

#Kommando for å initialisere databasen via Flask CLI
@click.command('init-db')
@with_appcontext  #Sikrer at komandoen kjøres med applikasjonskonteksten
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()  #Kaller funksjonen for å initialisere databasen
    click.echo('Initialized the database.')  #Skriver ut en bekreftelsesmelding til terminalen

#Funksjon for å registrere database-relaterte funksjoner og kommandoer med Flask-aplikasjonen
def init_app(app):
    app.teardown_appcontext(close_db)  
    app.cli.add_command(init_db_command)  


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
