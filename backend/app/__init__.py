# backend/app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, migrate, cors

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        from app import models
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    return app