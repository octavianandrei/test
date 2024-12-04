import subprocess
import os
import shutil

TEAMCITY_URL = os.environ.get('TEAMCITY_URL', 'https://teamcity.test-digital.com')
TEAMCITY_USERNAME = os.environ.get('TEAMCITY_USERNAME', 'test')
TEAMCITY_PASSWORD = os.environ.get('TEAMCITY_PASSWORD', 'test')

def export_pipelines():

    url = f"{TEAMCITY_URL}/admin/projectExport.html?baseProjectId=_Root"
    zip_file = ".teamcity.zip"
    target_folder = ".teamcity"  # Specify the target folder name
    command = ["curl", "-u", f"{TEAMCITY_USERNAME}:{TEAMCITY_PASSWORD}", "-o", zip_file, url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Decode stdout and stderr, ignoring errors
    stdout_decoded = stdout.decode('utf-8', errors='ignore')
    stderr_decoded = stderr.decode('utf-8', errors='ignore')

    # Unzip the downloaded file to the target folder
    unzip_command = ["unzip", zip_file, "-d", target_folder]
    subprocess.run(unzip_command)

    # Move all folders under /config/projects to be under the root existing folder .teamcity
    source_folder = os.path.join(target_folder, "config", "projects")

    # Check if the source folder exists, and if not, create it
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)  # Create the directory, including any necessary intermediate directories
        print(f"Created directory: {source_folder}")
    else:
        print(f"Directory already exists: {source_folder}")


    for item in os.listdir(source_folder):
        src = os.path.join(source_folder, item)
        dst = os.path.join(target_folder, item)
        shutil.move(src, dst)

    # Remove the config directory
    shutil.rmtree(os.path.join(target_folder, "config"))

    # Remove the .teamcity.zip file
    os.remove(zip_file)

    return stdout_decoded, stderr_decoded
