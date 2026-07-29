from functools import wraps
from datetime import datetime, timezone
from flask import request, jsonify, g
from app.models import Session, User

def get_current_user():  # Looks at the request's cookie, returns the logged-in User. or None
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None

    session = Session.query.get(session_id)
    if not session or not session.is_valid():
        return None

    return User.query.get(session.user_id)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"errors": {"_general": ["Authentication required."]}}), 401

        g.current_user = user  # stashes the user data somewhere the route functions can access without needing to recheck the cookie continuously.
        return f(*args, **kwargs)

    return decorated_function