"""
Supabase client wrapper.

We use the SERVICE ROLE key here because this module is only ever
imported and used server-side (inside Flask routes). The service role
key bypasses Row Level Security, which is what lets the admin panel
read/write freely while the schema.sql policies still protect the data
if it were ever queried with the public anon key from a browser.

Never send SUPABASE_SERVICE_KEY to the browser/templates/JS.
"""
from supabase import create_client, Client
from flask import current_app


_client: Client | None = None


def get_supabase() -> Client:
    """Return a cached Supabase client configured with the service role key."""
    global _client
    if _client is None:
        url = current_app.config["SUPABASE_URL"]
        key = current_app.config["SUPABASE_SERVICE_KEY"]
        print("SUPABASE_URL =", url)
        print("KEY PREFIX =", key[:20] if key else "EMPTY")
        print("KEY LENGTH =", len(key) if key else 0)
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL / SUPABASE_SERVICE_KEY are not set. "
                "Copy .env.example to .env and fill in your Supabase project credentials."
            )
        _client = create_client(url, key)
    return _client


def get_supabase_auth_client() -> Client:
    """
    A separate client using the anon key, used ONLY for verifying admin
    login credentials via Supabase Auth (auth.sign_in_with_password).
    Using the anon key here is intentional and safe — Supabase Auth's
    sign-in endpoint is designed to be called with the public key.
    """
    url = current_app.config["SUPABASE_URL"]
    anon_key = current_app.config["SUPABASE_ANON_KEY"]
    if not url or not anon_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_ANON_KEY are not set.")
    return create_client(url, anon_key)
