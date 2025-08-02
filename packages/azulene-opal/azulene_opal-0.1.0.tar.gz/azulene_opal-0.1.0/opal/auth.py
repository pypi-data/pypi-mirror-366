# Signup, signin, refresh, logout, user info

import httpx
import typer
import time
from rich import print
from opal import config

SUPABASE_URL = "https://vdkapdqniiehaweyhhbl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZka2FwZHFuaWllaGF3ZXloaGJsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NzE0MzcsImV4cCI6MjA2NzE0NzQzN30.uKXmjlR4TYQt7jSjzSD2fpgR7a3CW7RcBjYBGhTnAKs"

# ---- CLI Functions ----

# -----------------------------------------
# Sign up
# -----------------------------------------
def signup(email: str = typer.Option(...), password: str = typer.Option(...)):
    """Sign up for a new account (email + password)."""
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    payload = {"email": email, "password": password}

    r = httpx.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        print("[green]✅ Sign-up successful. Please check your email to confirm your account.[/green]")
    else:
        print(f"[red]❌ Sign-up failed: {r.json().get('msg', r.text)}[/red]")

# -----------------------------------------
# Login
# -----------------------------------------
def login(email: str = typer.Option(...), password: str = typer.Option(...)):
    """Log in with email + password and save tokens locally."""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    payload = {"email": email, "password": password}

    r = httpx.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        session = r.json()
        config.save_tokens(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            expires_in=session["expires_in"]
        )
        print("[green]✅ Logged in successfully![/green]")
    else:
        print(f"[red]❌ Login failed: {r.json().get('msg', r.text)}[/red]")

# -----------------------------------------
# Logout
# -----------------------------------------
def logout():
    """Log out by clearing local tokens."""
    config.clear_tokens()
    print("[green]👋 Logged out successfully.[/green]")

# -----------------------------------------
# Who Am I
# -----------------------------------------
def whoami():
    """Fetch user info from Azulene Opal using the stored access token."""
    try:
        token = config.get_access_token()
    except config.TokenExpiredException:
        # Token expired: try to refresh
        token = refresh_session()
    except config.NotLoggedInException:
        # Not logged in: 
        print(f"[red]❌ You are not logged in! Please run `opal login`.[/red]")
        return

    url = f"{SUPABASE_URL}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }

    r = httpx.get(url, headers=headers)
    if r.status_code == 200:
        user = r.json()
        print("[blue]📄 Logged in as:[/blue]")
        print(user)
    else:
        print(f"[red]❌ Failed to fetch user info: {r.json().get('msg', r.text)}[/red]")

# -----------------------------------------
# Refresh Session
# -----------------------------------------
def refresh_session() -> str:
    """
    Refresh the access token using the refresh token.

    Returns:
        New access token as string

    Raises:
        Exception if refresh fails
    """
    try:
        refresh_token = config.get_refresh_token()
    except Exception as e:
        raise Exception("You are not logged in. Please run `opal login`.") from e

    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    payload = {"refresh_token": refresh_token}

    r = httpx.post(url, headers=headers, json=payload)
    if r.status_code == 200:
        session = r.json()
        config.save_tokens(
            access_token=session["access_token"],
            refresh_token=session["refresh_token"],
            expires_in=session["expires_in"]
        )
        print("[green]🔁 Access token refreshed successfully.[/green]")
        return session["access_token"]
    else:
        raise Exception(f"❌ Failed to refresh token: {r.json().get('msg', r.text)}")
    