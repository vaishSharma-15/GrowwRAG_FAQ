import os
import subprocess
import sys

# Read .env
env_vars = os.environ.copy()
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()

print("Starting Uvicorn API Server...")
# Start process in background
subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"],
    env=env_vars,
    stdout=open('logs/phase4/api_server.log', 'w'),
    stderr=subprocess.STDOUT
)
print("API server started in background.")
