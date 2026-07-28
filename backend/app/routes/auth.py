from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db, bcrypt
from app.models import User, Organization
from app.schemas.auth_schemas import SignupSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
signup_schema = SignupSchema()

# Signup route

@auth_bp.route("/signup", methods=["POST"])
def signup():
    # validate the incoming data
    try:
        data = signup_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # Check the email isn't already taken
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"errors": {"email": ["An account with this email already exists."]}}), 409

    # create the organization
    organization = Organization(name=data["organization_name"])
    db.session.add(organization)
    db.session.flush() # gives 'organization.id' a real value before we use it

    # hash the password
    password_hash = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    # create the user
    user = User(
        organization_id=organization.id,
        email=data["email"],
        password_hash=password_hash,
        first_name=data["first_name"],
        last_name=data["last_name"],
        role="admin"
    )
    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201

# Login route

from datetime import datetime, timedelta, timezone
from app.models import Session
from app.schemas.auth_schemas import LoginSchema

login_schema = LoginSchema()
SESSION_LIFETIME_DAYS = 7

@auth_bp.route("/login", methods=["POST"])
def login():
    # validate input shape
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    # find the user by email
    user = User.query.filter_by(email=data["email"]).first()

    # check password
    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"errors": {"_general": ["Invalid email or password."]}}), 401

    # create a new session row
    session = Session(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_LIFETIME_DAYS),
    )
    db.session.add(session)
    db.session.commit()

    # send the session id back as a cookie
    response = jsonify(user.to_dict())
    response.set_cookie(
        "session_id",
        session.id,
        httponly=True,
        secure=False, # will become true once on https in production
        samesite="Lax",
        max_age=SESSION_LIFETIME_DAYS * 24 * 60 * 60,
    )
    return response, 200