from functools import wraps
from flask import session, request, redirect, url_for
from flask_login import current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login_usr', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.user_role == 'admin':
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function