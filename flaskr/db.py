import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# specific database functions
def fetchUserById(user_id):
    get_db().execute(
        'SELECT * FROM user WHERE id = ?', (user_id,)
    ).fetchone()


def createTraining(user_id):
    db = get_db()
    
    numberOfTraining = db.execute(
        'SELECT * FROM training WHERE id = ? AND is_resolved = false', (user_id,)
    ).rowcount;
    if numberOfTraining > 0:
        return False
    else:
        db.execute(
            'INSERT INTO training (user_id) VALUES (?)', (user_id,)
        )
        db.commit()
        return True