from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"  # Create database
UPLOAD_FOLDER = path.join('staticFiles', 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '@Ya9cxjQKYr5Zs+iB'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # Database location
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)  # Initialize library

    from .views import view
    from .auth import auth
    from .admin import admin
    from .production import production

    app.register_blueprint(view, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(production, url_prefix='/production')

    from .models import User,\
        Note, \
        Vote,\
        AuditionConfig,\
        Candidate,\
        Round,\
        SFOAParticipant,\
        ProductionConfig,\
        Result

    # this imports object user and notes into the app

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
