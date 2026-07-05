-- ============================================================
-- Tamilarasan S — Portfolio Database Schema (Supabase / Postgres)
-- Run once in Supabase: SQL Editor > New query > paste > Run
--
-- Design note: the Flask backend talks to Supabase using the
-- SERVICE ROLE key (server-side only, never exposed to the browser),
-- which bypasses Row Level Security entirely. The RLS policies below
-- exist as defense-in-depth in case the anon/public key is ever used
-- directly (e.g. future client-side reads) — they allow public read
-- access and block public writes.
-- ============================================================

-- 1. Profile (singleton row: photo, resume, hero + about content)
create table if not exists profile (
  id int primary key default 1,
  photo_url text,
  resume_url text,
  hero_title text default 'Tamilarasan S',
  hero_role text default 'IT Student | Full Stack & AI-Driven Web Developer',
  hero_tagline text default 'Building things with Python, HTML, CSS & curiosity',
  about_summary text default 'Motivated Information Technology student with skills in Python, HTML, CSS, MySQL, and UI/UX design. Passionate about full stack and AI-driven web development with experience in responsive web applications and problem-solving projects.',
  career_objective text default 'To grow as a full stack and AI-driven web developer, applying my skills in Python, web technologies and UI/UX design to build responsive, user-focused applications while continuously learning modern tools and best practices.',
  updated_at timestamptz default now(),
  constraint single_row check (id = 1)
);
insert into profile (id) values (1) on conflict (id) do nothing;

-- 2. Skills (technical = progress bar, soft = badge)
create table if not exists skills (
  id uuid primary key default gen_random_uuid(),
  type text not null check (type in ('technical','soft')),
  category text,            -- e.g. "Languages" (technical only)
  name text not null,
  level int,                 -- 0-100 (technical only)
  icon text,                  -- font-awesome class (soft only)
  sort_order int default 0,
  created_at timestamptz default now()
);

insert into skills (type, category, name, level, sort_order) values
  ('technical', 'Languages', 'Python', 88, 1),
  ('technical', 'Languages', 'C', 72, 2),
  ('technical', 'Web Technologies', 'HTML & CSS', 85, 3),
  ('technical', 'Web Technologies', 'JavaScript', 70, 4),
  ('technical', 'Data & Design', 'Power BI', 65, 5),
  ('technical', 'Data & Design', 'UI / UX Design', 78, 6)
on conflict do nothing;

insert into skills (type, name, icon, sort_order) values
  ('soft', 'Problem Solving', 'fa-solid fa-puzzle-piece', 1),
  ('soft', 'Team Collaboration', 'fa-solid fa-people-group', 2),
  ('soft', 'Leadership', 'fa-solid fa-flag', 3)
on conflict do nothing;

-- 3. Education (kept static/read-only in the UI, but stored so it isn't hardcoded)
create table if not exists education (
  id uuid primary key default gen_random_uuid(),
  degree text not null,
  institution text not null,
  year_label text,           -- e.g. "Pursuing · 2027" or "2023"
  score_label text,           -- e.g. "CGPA 7.45" or "Percentage 65%"
  sort_order int default 0,
  created_at timestamptz default now()
);
insert into education (degree, institution, year_label, score_label, sort_order) values
  ('Bachelor of Technology (Information Technology)', 'Muthayammal Engineering College', 'Pursuing · 2027', 'CGPA 7.45', 1),
  ('Higher Secondary Certificate (HSC)', 'Sree Gokulam Matric Hr Sec School', '2023', 'Percentage 65%', 2)
on conflict do nothing;

-- 4. Projects
create table if not exists projects (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  tag text default 'Project',
  description text not null,
  github_link text,
  demo_link text,
  image_url text,             -- main project thumbnail
  screenshots jsonb default '[]'::jsonb,  -- array of screenshot URLs
  sort_order int default 0,
  created_at timestamptz default now()
);

insert into projects (title, tag, description, sort_order) values
  ('Public Service Complaint Management System', 'Web Development Project',
   'A web-based system designed to help citizens raise, track and manage public service complaints in a structured, organized way.', 1),
  ('Smart Presentation Generator', 'Hackathon Project',
   'A hackathon project focused on automatically generating presentations, built to solve a real problem under time constraints as part of a team.', 2)
on conflict do nothing;

-- 5. Certifications
create table if not exists certifications (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  icon text default 'fa-solid fa-certificate',
  image_url text,             -- optional uploaded certificate image/PDF
  sort_order int default 0,
  created_at timestamptz default now()
);

insert into certifications (title, description, icon, sort_order) values
  ('Internship', 'Accent Techno Soft — ServiceNow University Virtual Internship', 'fa-solid fa-briefcase', 1),
  ('Industrial Visit', 'Kites Soft Pvt. Ltd.', 'fa-solid fa-industry', 2),
  ('NPTEL Certification', 'Edge Computing', 'fa-solid fa-certificate', 3)
on conflict do nothing;

-- 6. Contact info (singleton row)
create table if not exists contact_info (
  id int primary key default 1,
  email text default 'tamilarasansankar111@gmail.com',
  phone text default '+91 93612 40214',
  location text default 'Namakkal, India',
  updated_at timestamptz default now(),
  constraint single_row_contact check (id = 1)
);
insert into contact_info (id) values (1) on conflict (id) do nothing;

-- 7. Social links
create table if not exists social_links (
  id uuid primary key default gen_random_uuid(),
  platform text not null,     -- e.g. "LinkedIn", "GitHub"
  url text not null,
  icon text not null,          -- font-awesome class
  sort_order int default 0,
  created_at timestamptz default now()
);
insert into social_links (platform, url, icon, sort_order) values
  ('LinkedIn', 'https://linkedin.com/in/tamilarasan-sankar-8455343a5', 'fa-brands fa-linkedin-in', 1),
  ('GitHub', 'https://github.com/tamilarasansankar111-hub', 'fa-brands fa-github', 2)
on conflict do nothing;

-- 8. Admin/session audit (optional but useful — logs each admin login)
create table if not exists admin_logins (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  logged_in_at timestamptz default now(),
  ip_address text
);

-- ============================================================
-- Row Level Security — public read, no public writes.
-- The Flask backend uses the service_role key, which bypasses RLS,
-- for every write (and can be used for reads too).
-- ============================================================
alter table profile enable row level security;
alter table skills enable row level security;
alter table education enable row level security;
alter table projects enable row level security;
alter table certifications enable row level security;
alter table contact_info enable row level security;
alter table social_links enable row level security;
alter table admin_logins enable row level security;

create policy "Public read profile" on profile for select using (true);
create policy "Public read skills" on skills for select using (true);
create policy "Public read education" on education for select using (true);
create policy "Public read projects" on projects for select using (true);
create policy "Public read certifications" on certifications for select using (true);
create policy "Public read contact_info" on contact_info for select using (true);
create policy "Public read social_links" on social_links for select using (true);
-- admin_logins intentionally has no public read/write policy: only the
-- service_role key (used server-side) can access it.

-- ============================================================
-- Storage buckets — create these in Supabase Dashboard > Storage:
--   1. "profile-photos"   (Public bucket: ON)
--   2. "resumes"          (Public bucket: ON)
--   3. "project-images"   (Public bucket: ON)
--   4. "certificate-images" (Public bucket: ON)
-- ============================================================
