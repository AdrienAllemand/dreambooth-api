import os

from flask import Flask, redirect, url_for


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # init the database
    from . import db
    db.init_app(app)

    # redirect to home
    @app.route('/')
    def goHome():
        return redirect(url_for('home.home'))
    
    # register the blueprints
    
    # register the auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    # register the image blueprint
    UPLOAD_FOLDER = os.path.join(app.instance_path,'uploads')
    try:
        print("Creating upload folder: " + UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER)
    except OSError:
        pass
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    from . import images
    app.register_blueprint(images.bp)

    # register the home blueprint
    from . import home
    app.register_blueprint(home.bp)

    return app
