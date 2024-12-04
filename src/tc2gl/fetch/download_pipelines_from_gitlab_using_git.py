import subprocess
import os

# Set your variables
TOKEN = os.environ.get('TOKEN', 'glpat-1N16MsjTcfPVZa5uZAdu')
TOKEN_NAME = os.environ.get('TOKEN_NAME', 'tc2gl-token')
BRANCH = os.environ.get('BRANCH', "master")
GIT_URL = os.environ.get('GIT_URL', "gitlab.com/test-digital/engineering/teamcitytogitlabconverter.git")

def download_pipelines_git():
    # Commands to initialize the repo and set it up
    commands = [
        ["git", "init"],  # Initialize an empty Git repository
        ["git", "config", "--global", "--add", "safe.directory", "/app"],  # Add /app as a safe directory for Git
        ["git", "remote", "add", "origin", f"https://{TOKEN_NAME}:{TOKEN}@{GIT_URL}"],
        ["git", "sparse-checkout", "set", ".teamcity"],
        ["git", "fetch", "--depth=1", "origin", BRANCH],
        ["git", "checkout", BRANCH]
    ]

    # Execute each command in order
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            print(f"Error running command: {' '.join(cmd)}")
            print(result.stderr.decode())
        else:
            print(f"Success: {' '.join(cmd)}")
            print(result.stdout.decode())
