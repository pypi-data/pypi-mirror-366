# opal-cli

## Examples of CLI Usage

```shellscript
opal signup --email user@example.com --password secret123
opal login --email user@example.com --password secret123
opal whoami
opal logout

# Jobs
opal jobs submit --job-type xtb_calculation --input-data '{"numbers":[1,1], "positions":[[0,0,0],[0.74,0,0]]}'
opal jobs cancel --job-id abc123
opal jobs get --job-id abc123
opal jobs list-all
opal jobs poll
opal jobs get-job-types
opal jobs get-job-types2
opal jobs health
```

## Examples of Library Usage

```shellscript
from opal import auth, jobs

auth.login(email="test@example.com", password="password123")
jobs.submit_job("generate_conformers", {"smiles": "CCO", "num_conformers": 5})
```

## Install locally:

```shellscript
pip install -e .
where opal
pip show opal-cli
```

## Run locally:

```shellscript
python -m opal.main login --email zeed@azulenelabs.com --password password123
```

## CLI Examples

### **Help Commands**

```bash
python -m opal.main --help

python -m opal.main jobs --help

python -m opal.main signup --help

python -m opal.main jobs submit --help
```

### **Auth Commands**

```bash
# Sign up a new user
python -m opal.main signup --email your@email.com --password yourpassword

# Log in
python -m opal.main login --email your@email.com --password yourpassword

# Who am I (get current user info)
python -m opal.main whoami

# Log out
python -m opal.main logout
```

---

### **Job Commands**

```bash
# Submit a job (CMD)
python -m opal.main jobs submit --job-type generate_conformers --input-data "{\"smiles\": \"CCO\", \"num_conformers\": 5}"

# Submit a job (Git Bash / WSL / Linux / macOS)
python -m opal.main jobs submit --job-type generate_conformers --input-data '{"smiles": "CCO", "num_conformers": 5}'

# Submit a job (Powershell)
python -m opal.main jobs submit --job-type generate_conformers --input-data '{\"smiles\": \"CCO\", \"num_conformers\": 5}'

# List all jobs
python -m opal.main jobs list-all

# Get a specific job by ID
python -m opal.main jobs get --job-id YOUR_JOB_ID

# Cancel a job by ID
python -m opal.main jobs cancel --job-id YOUR_JOB_ID

# Poll modal for job status/results
python -m opal.main jobs poll

# Health check
python -m opal.main jobs health

# Get available job types (from Supabase Storage)
python -m opal.main jobs get-job-types

# Get available job types (from function variable)
python -m opal.main jobs get-job-types2
```

---

### Tips

* Wrap JSON input in single quotes (`'{"key": "value"}'`) and escape double quotes on Windows if needed.
* Replace `YOUR_JOB_ID` with actual returned IDs from `list-all` or `submit`.

---

## How to deploy to PyPI (TestPyPI)