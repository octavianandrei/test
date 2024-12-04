import requests
import os
from urllib.parse import quote

# Set your variables
GITLAB_API_URL = os.environ.get('GITLAB_API_URL', 'https://gitlab.com/api/v4')
REPO_ID = os.environ.get('REPO_ID', '58422563')  # You can use project ID or the URL-encoded path
TOKEN = os.environ.get('TOKEN')
FOLDER_PATH = ".teamcity"
BRANCH = os.environ.get('BRANCH', "master")  # Branch name or tag, adjust as necessary

# API endpoint to list the contents of a directory
list_files_url = f"{GITLAB_API_URL}/projects/{REPO_ID}/repository/tree"

# Headers for authentication
headers = {
    "PRIVATE-TOKEN": TOKEN
}

# Parameters for the request
params = {
    "path": FOLDER_PATH,
    "ref": BRANCH,
    "recursive": True
}

def listFiles():
    # Send the request to list the folder contents
    response = requests.get(list_files_url, headers=headers, params=params)


    if response.status_code == 200:
        files = response.json()
        print("Files in .teamcity folder:")
        for file in files:
            print(file['path'])
        return files
    else:
        print("Failed to list folder contents:", response.status_code, response.text)
        exit()


# Function to download a file
def download_file(file_path):
    # API endpoint to get the raw file
    encoded_file_path = quote(file_path, safe='')

    # GitLab API endpoint to get the file content
    url = f'https://gitlab.com/api/v4/projects/{REPO_ID}/repository/files/{encoded_file_path}/raw?ref={BRANCH}'

    headers = {
    'Private-Token': TOKEN
    }
    response = requests.get(url, headers=headers)

    print(response)
    if response.status_code == 200:
        # Save the file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {file_path}")
    else:
        print(f"Failed to download {file_path}: {response.status_code} {response.text}")


def download_pipelines_https():
    files = listFiles()
    # Download each file in the .teamcity folder
    for file in files:
        if file['type'] == 'blob':  # Ensure it's a file and not a directory
            download_file(file['path'])
