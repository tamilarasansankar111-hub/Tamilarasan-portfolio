"""
Admin blueprint.

- GET  /admin                 -> dashboard page (protected)
- Profile / hero / about:     PUT  /admin/api/profile
- Photo upload:                POST /admin/api/profile/photo
- Resume upload:                POST /admin/api/profile/resume
- Contact info:                 PUT  /admin/api/contact
- Social links:                  POST/PUT/DELETE /admin/api/social-links[/<id>]
- Skills:                         POST/PUT/DELETE /admin/api/skills[/<id>]
- Projects (+ images):            POST/PUT/DELETE /admin/api/projects[/<id>]
                                    POST /admin/api/projects/<id>/image
                                    POST /admin/api/projects/<id>/screenshots
- Certifications (+ image):       POST/PUT/DELETE /admin/api/certifications[/<id>]
                                    POST /admin/api/certifications/<id>/image

All CRUD endpoints return JSON and are protected by api_login_required,
so the browser session cookie (not a Supabase key) is what gates access.
"""
from flask import Blueprint, render_template, request, jsonify
from database.supabase import get_supabase
from utils.decorators import login_required, api_login_required
from utils.uploads import upload_image, upload_document, UploadError

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------- dashboard
@admin_bp.route("/")
@login_required
def dashboard():
    supabase = get_supabase()
    profile = supabase.table("profile").select("*").eq("id", 1).single().execute().data or {}
    contact_info = supabase.table("contact_info").select("*").eq("id", 1).single().execute().data or {}
    skills = supabase.table("skills").select("*").order("sort_order").execute().data or []
    projects = supabase.table("projects").select("*").order("sort_order").execute().data or []
    certifications = supabase.table("certifications").select("*").order("sort_order").execute().data or []
    social_links = supabase.table("social_links").select("*").order("sort_order").execute().data or []
    return render_template(
        "admin.html",
        profile=profile,
        contact_info=contact_info,
        skills=skills,
        projects=projects,
        certifications=certifications,
        social_links=social_links,
    )


def _err(message, code=400):
    return jsonify({"error": message}), code


# ---------------------------------------------------------------- profile / hero / about
@admin_bp.route("/api/profile", methods=["PUT"])
@api_login_required
def update_profile():
    data = request.get_json(silent=True) or {}
    fields = {}
    for key in ("hero_title", "hero_role", "hero_tagline", "about_summary", "career_objective"):
        if key in data:
            fields[key] = data[key]
    if not fields:
        return _err("No valid fields provided.")
    supabase = get_supabase()
    supabase.table("profile").update(fields).eq("id", 1).execute()
    return jsonify({"success": True, "updated": fields})


@admin_bp.route("/api/profile/photo", methods=["POST"])
@api_login_required
def update_profile_photo():
    file = request.files.get("photo")
    try:
        url = upload_image(file, "profile-photos")
    except UploadError as e:
        return _err(str(e))
    supabase = get_supabase()
    supabase.table("profile").update({"photo_url": url}).eq("id", 1).execute()
    return jsonify({"success": True, "photo_url": url})


@admin_bp.route("/api/profile/resume", methods=["POST"])
@api_login_required
def update_profile_resume():
    file = request.files.get("resume")
    try:
        url = upload_document(file, "resumes")
    except UploadError as e:
        return _err(str(e))
    supabase = get_supabase()
    supabase.table("profile").update({"resume_url": url}).eq("id", 1).execute()
    return jsonify({"success": True, "resume_url": url})


# ---------------------------------------------------------------- contact info
@admin_bp.route("/api/contact", methods=["PUT"])
@api_login_required
def update_contact():
    data = request.get_json(silent=True) or {}
    fields = {k: data[k] for k in ("email", "phone", "location") if k in data}
    if not fields:
        return _err("No valid fields provided.")
    supabase = get_supabase()
    supabase.table("contact_info").update(fields).eq("id", 1).execute()
    return jsonify({"success": True, "updated": fields})


# ---------------------------------------------------------------- social links
@admin_bp.route("/api/social-links", methods=["POST"])
@api_login_required
def add_social_link():
    data = request.get_json(silent=True) or {}
    platform, url, icon = data.get("platform"), data.get("url"), data.get("icon")
    if not platform or not url or not icon:
        return _err("platform, url and icon are required.")
    supabase = get_supabase()
    res = supabase.table("social_links").insert({"platform": platform, "url": url, "icon": icon}).execute()
    return jsonify({"success": True, "item": res.data[0] if res.data else None})


@admin_bp.route("/api/social-links/<link_id>", methods=["PUT"])
@api_login_required
def edit_social_link(link_id):
    data = request.get_json(silent=True) or {}
    fields = {k: data[k] for k in ("platform", "url", "icon") if k in data}
    if not fields:
        return _err("No valid fields provided.")
    supabase = get_supabase()
    supabase.table("social_links").update(fields).eq("id", link_id).execute()
    return jsonify({"success": True})


@admin_bp.route("/api/social-links/<link_id>", methods=["DELETE"])
@api_login_required
def delete_social_link(link_id):
    supabase = get_supabase()
    supabase.table("social_links").delete().eq("id", link_id).execute()
    return jsonify({"success": True})


# ---------------------------------------------------------------- skills
@admin_bp.route("/api/skills", methods=["POST"])
@api_login_required
def add_skill():
    data = request.get_json(silent=True) or {}
    skill_type = data.get("type")
    name = data.get("name")
    if skill_type not in ("technical", "soft") or not name:
        return _err("type ('technical'/'soft') and name are required.")

    payload = {"type": skill_type, "name": name}
    if skill_type == "technical":
        payload["category"] = data.get("category") or "Other"
        payload["level"] = int(data.get("level", 50))
    else:
        payload["icon"] = data.get("icon") or "fa-solid fa-star"

    supabase = get_supabase()
    res = supabase.table("skills").insert(payload).execute()
    return jsonify({"success": True, "item": res.data[0] if res.data else None})


@admin_bp.route("/api/skills/<skill_id>", methods=["PUT"])
@api_login_required
def edit_skill(skill_id):
    data = request.get_json(silent=True) or {}
    fields = {k: data[k] for k in ("category", "name", "level", "icon", "sort_order") if k in data}
    if not fields:
        return _err("No valid fields provided.")
    supabase = get_supabase()
    supabase.table("skills").update(fields).eq("id", skill_id).execute()
    return jsonify({"success": True})


@admin_bp.route("/api/skills/<skill_id>", methods=["DELETE"])
@api_login_required
def delete_skill(skill_id):
    supabase = get_supabase()
    supabase.table("skills").delete().eq("id", skill_id).execute()
    return jsonify({"success": True})


# ---------------------------------------------------------------- projects
@admin_bp.route("/api/projects", methods=["POST"])
@api_login_required
def add_project():
    data = request.get_json(silent=True) or {}
    title, description = data.get("title"), data.get("description")
    if not title or not description:
        return _err("title and description are required.")
    payload = {
        "title": title,
        "description": description,
        "tag": data.get("tag") or "Project",
        "github_link": data.get("github_link") or None,
        "demo_link": data.get("demo_link") or None,
    }
    supabase = get_supabase()
    res = supabase.table("projects").insert(payload).execute()
    return jsonify({"success": True, "item": res.data[0] if res.data else None})


@admin_bp.route("/api/projects/<project_id>", methods=["PUT"])
@api_login_required
def edit_project(project_id):
    data = request.get_json(silent=True) or {}
    fields = {k: data[k] for k in ("title", "description", "tag", "github_link", "demo_link", "sort_order") if k in data}
    if not fields:
        return _err("No valid fields provided.")
    supabase = get_supabase()
    supabase.table("projects").update(fields).eq("id", project_id).execute()
    return jsonify({"success": True})


@admin_bp.route("/api/projects/<project_id>", methods=["DELETE"])
@api_login_required
def delete_project(project_id):
    supabase = get_supabase()
    supabase.table("projects").delete().eq("id", project_id).execute()
    return jsonify({"success": True})


@admin_bp.route("/api/projects/<project_id>/image", methods=["POST"])
@api_login_required
def upload_project_image(project_id):
    file = request.files.get("image")
    try:
        url = upload_image(file, "project-images")
    except UploadError as e:
        return _err(str(e))
    supabase = get_supabase()
    supabase.table("projects").update({"image_url": url}).eq("id", project_id).execute()
    return jsonify({"success": True, "image_url": url})


@admin_bp.route("/api/projects/<project_id>/screenshots", methods=["POST"])
@api_login_required
def upload_project_screenshots(project_id):
    """Accepts one or more files under the 'screenshots' field and appends
    their URLs to the project's existing screenshots array."""
    files = request.files.getlist("screenshots")
    if not files:
        return _err("No screenshot files provided.")

    supabase = get_supabase()
    uploaded_urls = []
    for file in files:
        try:
            url = upload_image(file, "project-images")
            uploaded_urls.append(url)
        except UploadError as e:
            return _err(str(e))

    existing = supabase.table("projects").select("screenshots").eq("id", project_id).single().execute()
    current_screenshots = (existing.data or {}).get("screenshots") or []
    updated_screenshots = current_screenshots + uploaded_urls

    supabase.table("projects").update({"screenshots": updated_screenshots}).eq("id", project_id).execute()
    return jsonify({"success": True, "screenshots": updated_screenshots})


# ---------------------------------------------------------------- certifications
@admin_bp.route("/api/certifications", methods=["POST"])
@api_login_required
def add_certification():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return _err("title is required.")
    payload = {
        "title": title,
        "description": data.get("description") or "",
        "icon": data.get("icon") or "fa-solid fa-certificate",
    }
    supabase = get_supabase()
    res = supabase.table("certifications").insert(payload).execute()
    return jsonify({"success": True, "item": res.data[0] if res.data else None})


@admin_bp.route("/api/certifications/<cert_id>", methods=["PUT"])
@api_login_required
def edit_certification(cert_id):
    data = request.get_json(silent=True) or {}
    fields = {k: data[k] for k in ("title", "description", "icon", "sort_order") if k in data}
    if not fields:
        return _err("No valid fields provided.")
    supabase = get_supabase()
    supabase.table("certifications").update(fields).eq("id", cert_id).execute()
    return jsonify({"success": True})


@admin_bp.route("/api/certifications/<cert_id>", methods=["DELETE"])
@api_login_required
def delete_certification(cert_id):
    supabase = get_supabase()
    supabase.table("certifications").delete().eq("id", cert_id).execute()
    return jsonify({"success": True})


@admin_bp.route("/api/certifications/<cert_id>/image", methods=["POST"])
@api_login_required
def upload_certification_image(cert_id):
    file = request.files.get("image")
    try:
        url = upload_image(file, "certificate-images")
    except UploadError as e:
        return _err(str(e))
    supabase = get_supabase()
    supabase.table("certifications").update({"image_url": url}).eq("id", cert_id).execute()
    return jsonify({"success": True, "image_url": url})
