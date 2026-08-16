# backend/app/__init__.py
from flask import Flask
from config import Config
from app.extensions import db, migrate, cors, bcrypt, limiter, talisman

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        from app import models
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])
    bcrypt.init_app(app)
    limiter.init_app(app)
    talisman.init_app(
        app,
        force_https=False,  # will flip to True once deployed with a real HTTPS domain
        content_security_policy={
            "default-src": "'self'",
        },
        strict_transport_security=False,  # same — enable once on real HTTPS
    )

    from app.routes.health import health_bp
    app.register_blueprint(health_bp)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.jobs import jobs_bp
    app.register_blueprint(jobs_bp)

    from app.routes.candidates import candidates_bp
    app.register_blueprint(candidates_bp)

    from app.routes.applications import applications_bp
    app.register_blueprint(applications_bp)

    from app.routes.ai_analysis import ai_analysis_bp
    app.register_blueprint(ai_analysis_bp)

    from app.routes.job_distribution import distribution_bp
    app.register_blueprint(distribution_bp)

    return app