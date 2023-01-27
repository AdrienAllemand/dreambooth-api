import functools
import os
from flask import (
    Blueprint, current_app, render_template, g
)
from flaskr.auth import login_required
from flaskr.db import get_db

from werkzeug.utils import secure_filename

bp = Blueprint('home', __name__, url_prefix='/home')

# This handles the registration
@bp.route('/')
@login_required
def home():
    db = get_db()
    trainingSessions = db.execute(
        'SELECT id, author_id, created, is_resolved'
        ' FROM training WHERE author_id = ?'
        ' ORDER BY created DESC',
        (g.user['id'],)
    ).fetchall()

    try:
        images = os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(str(g.user['id']))))
    except FileNotFoundError:
        images = []

    return render_template('user/home.html',trainingSessions=trainingSessions, images=images)


