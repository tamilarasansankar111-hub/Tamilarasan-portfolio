"""
Public-facing portfolio blueprint.
Every route fetches its content from Supabase (via the service-role
client) and renders it server-side — visitors never call Supabase
directly, so no database keys are ever exposed to the browser.
"""
from flask import Blueprint, render_template, redirect, session
from database.supabase import get_supabase

portfolio_bp = Blueprint("portfolio", __name__)


def _get_profile():
    supabase = get_supabase()
    res = supabase.table("profile").select("*").eq("id", 1).single().execute()
    return res.data or {}


def _get_contact():
    supabase = get_supabase()
    res = supabase.table("contact_info").select("*").eq("id", 1).single().execute()
    return res.data or {}


def _get_social_links():
    supabase = get_supabase()
    res = supabase.table("social_links").select("*").order("sort_order").execute()
    return res.data or []


def _base_context():
    """Shared context every template needs (profile photo/resume, social links, admin state)."""
    return {
        "profile": _get_profile(),
        "social_links": _get_social_links(),
        "is_admin": bool(session.get("admin_logged_in")),
    }


@portfolio_bp.route("/")
def home():
    ctx = _base_context()
    return render_template("index.html", page="home", **ctx)


@portfolio_bp.route("/about")
def about():
    ctx = _base_context()
    return render_template("index.html", page="about", **ctx)


@portfolio_bp.route("/skills")
def skills():
    supabase = get_supabase()
    res = supabase.table("skills").select("*").order("sort_order").order("created_at").execute()
    all_skills = res.data or []
    technical = [s for s in all_skills if s["type"] == "technical"]
    soft = [s for s in all_skills if s["type"] == "soft"]

    categories = {}
    for s in technical:
        categories.setdefault(s.get("category") or "Other", []).append(s)

    ctx = _base_context()
    return render_template("index.html", page="skills", technical_categories=categories, soft_skills=soft, **ctx)


@portfolio_bp.route("/education")
def education():
    supabase = get_supabase()
    res = supabase.table("education").select("*").order("sort_order").execute()
    ctx = _base_context()
    return render_template("index.html", page="education", education_items=res.data or [], **ctx)


@portfolio_bp.route("/projects")
def projects():
    supabase = get_supabase()
    res = supabase.table("projects").select("*").order("sort_order").order("created_at").execute()
    ctx = _base_context()
    return render_template("index.html", page="projects", projects=res.data or [], **ctx)


@portfolio_bp.route("/certifications")
def certifications():
    supabase = get_supabase()
    res = supabase.table("certifications").select("*").order("sort_order").order("created_at").execute()
    ctx = _base_context()
    return render_template("index.html", page="certifications", certifications=res.data or [], **ctx)


@portfolio_bp.route("/contact")
def contact():
    ctx = _base_context()
    ctx["contact_info"] = _get_contact()
    return render_template("index.html", page="contact", **ctx)


@portfolio_bp.route("/resume")
def download_resume():
    """Redirect to the current resume file stored in Supabase Storage."""
    profile = _get_profile()
    resume_url = profile.get("resume_url")
    if resume_url:
        return redirect(resume_url)
    return redirect("/static/resume/default_resume.pdf")
