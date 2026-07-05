"""
Authentication blueprint.

Login verifies credentials against Supabase Auth (auth.sign_in_with_password),
so the real password lives in Supabase — not in this codebase. On success we
store a simple server-side session flag; we do not need to keep Supabase's
access token since all privileged data access happens server-side with the
service role key anyway.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.supabase import get_supabase_auth_client, get_supabase

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")

        try:
            auth_client = get_supabase_auth_client()
            result = auth_client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if result and result.user:
                session.permanent = True
                session["admin_logged_in"] = True
                session["admin_email"] = email

                # Optional audit log — best-effort, ignore failures
                try:
                    supabase = get_supabase()
                    supabase.table("admin_logins").insert({
                        "email": email,
                        "ip_address": request.remote_addr,
                    }).execute()
                except Exception:
                    pass

                next_url = request.args.get("next") or url_for("admin.dashboard")
                return redirect(next_url)
            else:
                flash("Incorrect email or password.", "error")
        except Exception as e:
          print("SUPABASE LOGIN ERROR:", repr(e))
          flash(str(e), "error")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("portfolio.home"))
