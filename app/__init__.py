from flask import Flask

from config import Config
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User, DailyLog, Prediction, Insight
    from app.routes import auth_bp, main_bp, logs_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(logs_bp)

    return app