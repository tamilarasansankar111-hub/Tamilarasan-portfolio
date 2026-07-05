# Tamilarasan S — Portfolio (Flask + Supabase)

A production-structured personal portfolio site with a secure admin
dashboard for managing every piece of content — profile photo, resume,
hero/about text, skills, projects (with images/screenshots),
certifications, contact info and social links — without touching code.

This is a restructure of the previously-built static site into a real
Flask + Supabase application, keeping all existing content, sections,
styling and animations, and fixing the duplication/scattered-files
issues of the earlier prototypes.

## Architecture

```
Portfolio/
├── app.py                # Flask application factory + error handlers
├── config.py              # Env-based configuration (dev/prod)
├── requirements.txt
├── .env.example
│
├── routes/
│   ├── auth.py             # Login / logout (Supabase Auth + session)
│   ├── portfolio.py        # Public pages — all read from Supabase
│   └── admin.py             # Protected dashboard + JSON CRUD/upload APIs
│
├── database/
│   ├── supabase.py          # Supabase client wrapper (service-role, server-side only)
│   └── schema.sql            # Full table schema, seed data, RLS policies
│
├── templates/
│   ├── base.html              # Shared head/nav/footer
│   ├── index.html              # All public sections (home/about/skills/...)
│   ├── admin.html               # Tabbed admin dashboard
│   ├── login.html               # Admin login page
│   └── 404.html                  # 404 / 500 error page
│
├── static/
│   ├── css/style.css              # All existing styling (unchanged)
│   ├── js/main.js                  # Public-facing behavior (theme, nav, animations)
│   ├── js/admin.js                  # Admin dashboard CRUD calls
│   ├── images/{profile,certificates,projects}/  # default seed assets
│   ├── resume/                        # default seed resume
│   └── uploads/                        # (unused placeholder; real uploads go to Supabase Storage)
│
└── utils/
    ├── decorators.py    # login_required / api_login_required
    └── uploads.py         # Supabase Storage upload helpers
```

### Why one `index.html` but still separate pages?

Every section (`/`, `/about`, `/skills`, `/education`, `/projects`,
`/certifications`, `/contact`) is a **real, separate Flask route** — no
scroll-jumping, real page loads, real URLs. They all render the same
`index.html` template with a `page` variable controlling which section
shows, which keeps the template count minimal (as requested) while still
giving you genuinely separate pages.

### Security model

- The Flask backend talks to Supabase using the **service role key**
  (`SUPABASE_SERVICE_KEY`), which is never sent to the browser. All
  reads/writes happen server-side.
- Admin login is verified against **Supabase Auth**
  (`auth.sign_in_with_password`), so your real password lives in
  Supabase, not in this code. A signed Flask session cookie is what
  gates access to `/admin/*` afterward.
- Row Level Security policies in `schema.sql` allow public read access
  to content tables and block public writes — defense-in-depth in case
  the anon key is ever used directly.

## Setup

### 1. Supabase project
1. Create a free project at [supabase.com](https://supabase.com).
2. **SQL Editor** → paste and run `database/schema.sql`.
3. **Storage** → create four **public** buckets: `profile-photos`,
   `resumes`, `project-images`, `certificate-images`.
4. **Authentication → Users → Add user** → create your admin login
   (e.g. `tamilarasansankar111@gmail.com` / your chosen password).
5. **Project Settings → API** → copy the **Project URL**, **anon public
   key**, and **service_role key**.

### 2. Local environment
```bash
cp .env.example .env
# then edit .env and fill in SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY
```

### 3. Install & run
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000`. Log in at `http://localhost:5000/login`.

### 4. Deploy
Any host that runs Flask works (Render, Railway, Fly.io, a VPS, etc.).
For production:
```bash
gunicorn "app:create_app()"
```
Set the same environment variables from `.env` in your host's config,
and set `FLASK_ENV=production`.

## What's editable from the admin dashboard

- Profile photo, resume (PDF)
- Hero title / role / tagline, About summary, Career objective
- Contact email / phone / location
- Social links (add / delete)
- Skills — technical (with category + proficiency %) and soft (badge), add / delete
- Projects — title, tag, description, GitHub/demo links, main image, multiple screenshots, add / delete
- Certifications — title, description, icon, image, add / delete

Education is stored in the `education` table (seeded from the resume)
but isn't exposed in the admin UI yet, since it wasn't part of the
original request — ask if you'd like that added too.
