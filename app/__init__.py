from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.defects import defects_bp
    from app.routes.dashboard import dash_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(defects_bp)
    app.register_blueprint(dash_bp)

    with app.app_context():
        db.create_all()

    return app