from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from app.extensions import db, bcrypt
from app.models import User, Organization
from app.schemas.auth_schemas import SignupSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# --------------------
# Signup route
# --------------------

signup_schema = SignupSchema()

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

# --------------------
# Login route
# --------------------

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

# --------------------
# Protected route executed before any command within the program, like jobs, candidates etc, are executed.
# --------------------

from app.services.auth_service import login_required

@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify(g.current_user.to_dict()), 200

# --------------------
# Logout route
# --------------------

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session_id = request.cookies.get("session_id")
    Session.query.filter_by(id=session_id).delete()
    db.session.commit()

    response = jsonify({"message": "Logged out successfully."})
    response.delete_cookie("session_id")
    return response, 200

# --------------------
# ForgotPassword or ResetPassword route
# --------------------

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from app.models import PasswordResetToken
from app.schemas.auth_schemas import ForgotPasswordSchema, ResetPasswordSchema

forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()

RESET_TOKEN_TTL_MINUTES = 20

def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        data = forgot_password_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()

    generic_response = {"message": "If an account with that email exists, a reset link has been generated."}

    if not user:
        return jsonify(generic_response), 200

    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
    )
    db.session.add(reset_token)
    db.session.commit()

    print(f"[DEV] password reset token for {user.email}: {raw_token}")
    generic_response["dev_reset_token"] = raw_token
    return jsonify(generic_response), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    try:
        data = reset_password_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    token_hash = _hash_token(data["token"])
    reset_token = PasswordResetToken.query.filter_by(token_hash=token_hash).first()

    if not reset_token or not reset_token.is_valid():
        return jsonify({"errors": {"_general": ["This reset link is invalid or has expired."]}}), 400

    user =User.query.get(reset_token.user_id)
    user.password_hash = bcrypt.generate_password_hash(data["new_password"]).decode("utf-8")

    reset_token.used_at = datetime.now(timezone.utc)

    Session.query.filter_by(user_id=user.id).delete()
    db.session.commit()

    return jsonify({"message": "Password reset successful. Please log in with your new password."}), 200