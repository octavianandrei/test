import shutil
import os

def delete_tc_folder(folder):
    """
    Deletes the contents of the specified folder without removing the folder itself.

    Args:
        folder (str): The folder to clear. Defaults to ".teamcity".

    Returns:
        None
    """
    # Check if the folder exists
    if os.path.exists(folder):
        # Loop through the folder and delete each file/subfolder
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the entire directory
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
