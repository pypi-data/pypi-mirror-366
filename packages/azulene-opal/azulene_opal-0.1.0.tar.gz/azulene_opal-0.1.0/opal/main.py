# # Typer CLI entrypoint

import typer
from opal import auth, jobs

app = typer.Typer(help="</> Opal CLI - Submit and manage Azulene Opal jobs via a command line interface")

# Register auth commands
app.command("signup")(auth.signup)
app.command("login")(auth.login)
app.command("logout")(auth.logout)
app.command("whoami")(auth.whoami)

# Create sub-app for jobs
jobs_app = typer.Typer(help="Job commands (submit, cancel, get, etc.)")
jobs_app.command("submit", help="Submit a new job to the backend")(jobs.submit)
jobs_app.command("cancel", help="Cancel a running job by job ID")(jobs.cancel)
jobs_app.command("get", help="Get detailed information about a specific job by ID")(jobs.get)
jobs_app.command("list-all", help="List all submitted jobs for the current user")(jobs.list_all)
jobs_app.command("poll", help="Poll a job by ID until it completes or fails")(jobs.poll)
jobs_app.command("health", help="Check the health/status of the backend job system")(jobs.check_health)
jobs_app.command("get-job-types", help="Get the list of available job types")(jobs.get_job_types)
jobs_app.command("get-job-types2", help="Get the list of available job types")(jobs.get_job_types2)

# Mount it under `opal jobs ...`
app.add_typer(jobs_app, name="jobs")

def main():
    app()

if __name__ == "__main__":
    main()