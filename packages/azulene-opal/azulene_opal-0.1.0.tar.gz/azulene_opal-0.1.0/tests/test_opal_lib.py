from opal import auth, jobs

# 1. Sign up
# auth.signup(email="your@email.com", password="yourpassword")

# 2. Log in
auth.login(email="zeed@azulenelabs.com", password="password123")

# 3. Who am I
print(auth.whoami())

# 4. Submit a job
jobs.submit(job_type="generate_conformers",input_data={"smiles": "CCO", "num_conformers": 5}) # dict
# jobs.submit(job_type="generate_conformers",input_data='{"smiles": "CCO", "num_conformers": 5}') # str

# 5. List all jobs
print(jobs.list_all())

# 6. Get a specific job
print(jobs.get(job_id="YOUR_JOB_ID"))

# 7. Cancel a job
print(jobs.cancel(job_id="YOUR_JOB_ID"))

# 8. Poll job statuses
jobs.poll()

# 9. Health check
print(jobs.check_health())

# 10. Get job types
print(jobs.get_job_types())
print(jobs.get_job_types2())
