from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from emblnk.config import Config
from flask_migrate import Migrate
from flask_apscheduler import APScheduler

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()
scheduler = APScheduler()
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)

    app.config['SERVER_NAME'] = '127.0.0.1:5000'
    app.config['APPLICATION_ROOT'] = ''
    app.config['PREFERRED_URL_SCHEME'] = 'http'

    @app.context_processor
    def inject_vars():
        error = False
        if 'error' in session:
            error = session['error']
        return {'error': error, }
    
    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db, render_as_batch=True)
        scheduler.init_app(app)
        scheduler.start()
        bcrypt.init_app(app)
    
    login_manager.init_app(app)
    from emblnk.users.routes import users
    from emblnk.main.routes import main
    from emblnk.errors.handlers import errors
    from emblnk.campaigns.routes import campaign
    from emblnk.campaigns.tracking import tracking

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(campaign)
    app.register_blueprint(tracking)

    return app