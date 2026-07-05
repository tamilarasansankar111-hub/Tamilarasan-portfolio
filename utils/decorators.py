"""
Auth decorators for protecting admin routes with session-based login.
"""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify


def login_required(view_func):
    """Redirect to login page (HTML routes) if not authenticated."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("auth.login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


def api_login_required(view_func):
    """Return 401 JSON (instead of redirecting) if not authenticated — for API/CRUD endpoints."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "Unauthorized. Please log in as admin."}), 401
        return view_func(*args, **kwargs)
    return wrapped
