import os
import sys
import xmltodict
import requests
import pandas as pd
from openpyxl import load_workbook

# Define the path to the .teamcity folder
teamcity_folder_path = "./../../.teamcity"
TEAMCITY_URL = os.environ.get('TEAMCITY_URL', 'https://teamcity.test-digital.com')
TEAMCITY_USERNAME = os.environ.get('TEAMCITY_USERNAME', 'test')
TEAMCITY_PASSWORD = os.environ.get('TEAMCITY_PASSWORD', 'test')
EXCEL_FILE = 'TC2GL.xlsx'

def get_filenames_minus_extension(folder_path):
    filenames = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xml'):
                filename_without_extension = os.path.splitext(file)[0]
                filenames.append(filename_without_extension)
    return filenames

def traverse_teamcity_folder(folder_path):
    all_filenames = []
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            build_types_path = os.path.join(subfolder_path, 'buildTypes')
            if os.path.exists(build_types_path):
                filenames = get_filenames_minus_extension(build_types_path)
                all_filenames.extend(filenames)
    return all_filenames

def extract_build_info(build_info):
    data = {}
    for key, value in build_info.items():
        if isinstance(value, dict):
            nested_data = extract_build_info(value)
            for nested_key, nested_value in nested_data.items():
                data[f"{key}.{nested_key}"] = nested_value
        else:
            data[key] = value
    return data

def write_to_excel(filename, data, sheet_name):
    if os.path.exists(filename):
        # Load existing workbook and add a new sheet with the given name
        with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
            df = pd.DataFrame(data[1:], columns=data[0])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Create a new workbook and add the sheet with the given name
        with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
            df = pd.DataFrame(data[1:], columns=data[0])
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def main():
    filenames = traverse_teamcity_folder(teamcity_folder_path)
    print(filenames)
    print("Python executable path:", sys.executable)

    # Prepare data for Excel
    data = []

    # Extract build info keys for header row
    header_row = ["Pipeline ID", "Filename"]
    if filenames:
        url = f"{TEAMCITY_URL}/httpAuth/app/rest/builds/buildType:(id:{filenames[0]}),count:1"
        headers = {'Accept': 'application/xml'}
        response = requests.get(url, headers=headers, auth=(TEAMCITY_USERNAME, TEAMCITY_PASSWORD))
        response.raise_for_status()
        build_info_dict = xmltodict.parse(response.content)
        if 'build' in build_info_dict:
            sample_build_info = extract_build_info(build_info_dict['build'])
            header_row.extend(sample_build_info.keys())

    data.append(header_row)

    for filename in filenames:
        url = f"{TEAMCITY_URL}/httpAuth/app/rest/builds/buildType:(id:{filename}),count:1"
        headers = {'Accept': 'application/xml'}

        try:
            response = requests.get(url, headers=headers, auth=(TEAMCITY_USERNAME, TEAMCITY_PASSWORD))
            response.raise_for_status()  # This is where we raise the error for bad status codes
            # Convert XML response to Python dictionary directly
            build_info_dict = xmltodict.parse(response.content)
            if 'build' in build_info_dict:
                build_info = extract_build_info(build_info_dict['build'])
                row = [filename, filename] + [build_info.get(key, 'N/A') for key in sample_build_info.keys()]
            else:
                row = [filename, filename] + ['N/A'] * len(sample_build_info.keys())
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                row = [filename, filename] + ["no build found"] * len(sample_build_info.keys())
            else:
                row = [filename, filename] + [str(http_err)] * len(sample_build_info.keys())
        except Exception as err:
            row = [filename, filename] + [str(err)] * len(sample_build_info.keys())

        data.append(row)

    # Write the data to the local Excel file
    write_to_excel(EXCEL_FILE, data, 'last_builds')

    print(f"Local spreadsheet '{EXCEL_FILE}' updated with pipeline information in 'last_builds' worksheet.")

if __name__ == "__main__":
    main()
