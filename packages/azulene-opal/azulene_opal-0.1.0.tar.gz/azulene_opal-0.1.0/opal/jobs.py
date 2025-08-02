# Submit, cancel, get, poll
import json
import httpx
import typer
from rich import print
from opal import config, auth

SUPABASE_URL = "https://vdkapdqniiehaweyhhbl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZka2FwZHFuaWllaGF3ZXloaGJsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE1NzE0MzcsImV4cCI6MjA2NzE0NzQzN30.uKXmjlR4TYQt7jSjzSD2fpgR7a3CW7RcBjYBGhTnAKs"  # Replace or load from env


# ---------------------
# Internal
# ---------------------

def _auth_headers():
    try:
        token = config.get_access_token()
    except config.TokenExpiredException:
        # Token expired: try to refresh
        token = auth.refresh_session()
    except config.NotLoggedInException:
        # Not logged in: handle as you wish
        raise Exception("You are not logged in. Please run `opal login`.")

    return {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }

# ---------------------
# CLI commands
# ---------------------

def check_health():
    url = f"{SUPABASE_URL}/functions/v1/check-health"
    r = httpx.get(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[green]✅ Health check passed[/green]")
        print(r.json())
    else:
        print("[red]❌ Health check failed:[/red]", r.text)

def submit(
    job_type: str = typer.Option(..., "--job-type", help="e.g., generate_conformers"),
    input_data: str = typer.Option(..., "--input-data", help='JSON string like \'{"smiles": "CCO"}\'')
):
    """Submit a job of a given type."""
    url = f"{SUPABASE_URL}/functions/v1/submit-job"

    # Handle both str and dict inputs
    if isinstance(input_data, str):
        parsed_input = json.loads(input_data)
    else:
        parsed_input = input_data  

    payload = {
        "job_type": job_type,
        "input_data": parsed_input
    }
    
    r = httpx.post(url, headers=_auth_headers(), json=payload)
    if r.status_code == 200:
        print("[green]✅ Job submitted successfully[/green]")
        print(r.json())
    else:
        print("[red]❌ Job submission failed:[/red]", r.text)

def list_all():
    url = f"{SUPABASE_URL}/functions/v1/get-jobs"
    r = httpx.get(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[blue]📋 Jobs:[/blue]")
        print(r.json())
    else:
        print("[red]❌ Failed to fetch jobs:[/red]", r.text)

def get(job_id: str = typer.Option(..., "--job-id", help="Job ID to fetch")):
    url = f"{SUPABASE_URL}/functions/v1/get-job/{job_id}"
    r = httpx.get(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[blue]📄 Job Info:[/blue]")
        print(r.json())
    else:
        print("[red]❌ Failed to fetch job:[/red]", r.text)

def cancel(job_id: str = typer.Option(..., "--job-id", help="Job ID to cancel")):
    url = f"{SUPABASE_URL}/functions/v1/cancel-job/{job_id}"
    r = httpx.delete(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[yellow]⚠️ Job cancelled[/yellow]")
        print(r.json())
    else:
        print("[red]❌ Failed to cancel job:[/red]", r.text)

def poll():
    url = f"{SUPABASE_URL}/functions/v1/poll-modal-results"
    r = httpx.post(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[green]🔁 Polling complete[/green]")
        print(r.json())
    else:
        print("[red]❌ Polling failed:[/red]", r.text)

def get_job_types():
    url = f"{SUPABASE_URL}/functions/v1/get-job-types"
    r = httpx.get(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[cyan]📦 Available job types (from Supabase Storage):[/cyan]")
        print(r.json())
    else:
        print("[red]❌ Failed to get job types:[/red]", r.text)

def get_job_types2():
    url = f"{SUPABASE_URL}/functions/v1/get-job-types2"
    r = httpx.get(url, headers=_auth_headers())
    if r.status_code == 200:
        print("[cyan]📦 Available job types (from function constant):[/cyan]")
        print(r.json())
    else:
        print("[red]❌ Failed to get job types:[/red]", r.text)
