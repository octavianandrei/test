import os
import sys
import xmltodict
import requests
from tc2gl.excel.excel_writer import write_to_excel

# Define the path to the .teamcity folder
teamcity_folder_path = ".teamcity"
TEAMCITY_URL = os.environ.get('TEAMCITY_URL', 'https://teamcity.test-digital.com')
TEAMCITY_USERNAME = os.environ.get('TEAMCITY_USERNAME', 'test')
TEAMCITY_PASSWORD = os.environ.get('TEAMCITY_PASSWORD', 'test')
EXCEL_FILE = 'TC2GL.xlsx'

# Headers based on the order in the XML structure
HEADERS_ORDER = [
    "@branchName", "@buildTypeId", "@composite", "@defaultBranch", "@href", "@id", "@number", "@state", "@status", "@webUrl",
    "artifacts.@count", "buildType.@c", "buildType.@projectId", "buildType.@name", "buildType.@projectName",
    "buildType.@id", "finishDate", "properties.@count", "snapshot-dependencies.@count",
    "snapshot-dependencies.build.@buildTypeId", "startDate", "statistics.@href", "triggered.@type", "triggered.build.@buildTypeId",
    "triggered.build.@composite", "triggered.buildType.@id", "triggered.buildType.@name", "triggered.buildType.@projectId",
    "triggered.buildType.@projectName", "lastChanges.change.@date", "lastChanges.change.@href",
    "lastChanges.change.@id", "lastChanges.change.@username", "lastChanges.change.@version", "lastChanges.change.@webUrl",
    "queuedDate", "relatedIssues.@href", "revisions.@count", "revisions.revision.@vcsBranchName", "revisions.revision.@version",
    "revisions.revision.vcs-root-instance.@href", "revisions.revision.vcs-root-instance.@id",
    "revisions.revision.vcs-root-instance.@name", "revisions.revision.vcs-root-instance.@vcs-root-id", "snapshot-dependencies.@count",
    "snapshot-dependencies.build.@branchName", "snapshot-dependencies.build.@buildTypeId", "snapshot-dependencies.build.@defaultBranch",
    "snapshot-dependencies.build.@href", "snapshot-dependencies.build.@id", "snapshot-dependencies.build.@number",
    "snapshot-dependencies.build.@state", "snapshot-dependencies.build.@status", "snapshot-dependencies.build.@webUrl",
    "snapshot-dependencies.build.finishOnAgentDate", "statusText", "testOccurrences.@count", "testOccurrences.@href",
    "testOccurrences.@passed", "triggered.@date", "triggered.@details", "triggered.@type", "triggered.build.@branchName",
    "triggered.build.@buildTypeId", "triggered.build.@composite", "triggered.build.@defaultBranch", "triggered.build.@href",
    "triggered.build.@id", "triggered.build.@number", "triggered.build.@state", "triggered.build.@status", "triggered.build.@webUrl",
    "triggered.build.finishOnAgentDate", "triggered.buildType.@href", "triggered.buildType.@id", "triggered.buildType.@name",
    "triggered.buildType.@projectId", "triggered.buildType.@projectName", "triggered.buildType.@webUrl",
    "versionedSettingsRevision.@vcsBranchName", "versionedSettingsRevision.@version", "versionedSettingsRevision.vcs-root-instance.@href",
    "versionedSettingsRevision.vcs-root-instance.@id", "versionedSettingsRevision.vcs-root-instance.@name",
    "versionedSettingsRevision.vcs-root-instance.@vcs-root-id"
]

SUMMARY_HEADERS = [
    "@branchName", "@buildTypeId", "@composite", "@href", "@id", "@number", "@state", "@status", "@webUrl",
    "artifacts.@count", "buildType.@description", "buildType.@projectId", "buildType.@name", "buildType.@projectName",
    "buildType.@id", "finishDate", "properties.@count", "snapshot-dependencies.@count",
    "snapshot-dependencies.build.@buildTypeId", "startDate", "statistics.@href", "triggered.@type", "triggered.build.@buildTypeId",
    "triggered.build.@composite", "triggered.buildType.@id", "triggered.buildType.@name", "triggered.buildType.@projectId",
    "triggered.buildType.@projectName", "project.properties"
]

def get_filenames_minus_extension(folder_path):
    """
    Traverse the given folder path and collect filenames without their extensions.

    Args:
        folder_path (str): The path to traverse.

    Returns:
        list: A list of filenames without extensions.
    """
    filenames = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.xml'):
                filename_without_extension = os.path.splitext(file)[0]
                filenames.append(filename_without_extension)
    return filenames

def traverse_teamcity_folder(folder_path):
    """
    Traverse the .teamcity folder to collect all XML filenames minus their extensions.

    Args:
        folder_path (str): The path to the .teamcity folder.

    Returns:
        list: A list of all filenames minus their extensions.
    """
    all_filenames = []
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        print(f"Checking subfolder: {subfolder_path}")

        if os.path.isdir(subfolder_path):
            print(f"Subfolder is a directory {subfolder_path}")
            build_types_path = os.path.join(subfolder_path, 'buildTypes')
            if os.path.exists(build_types_path):
                print(f"'buildTypes directory found {build_types_path}")
                filenames = get_filenames_minus_extension(build_types_path)
                all_filenames.extend(filenames)

    print(f"All Filenames collected: {all_filenames}")
    return all_filenames

def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten a nested dictionary.

    Args:
        d (dict): The dictionary to flatten.
        parent_key (str): The base key to start with.
        sep (str): Separator to use between keys.

    Returns:
        dict: The flattened dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, sub_v in enumerate(v):
                items.extend(flatten_dict(sub_v, f"{new_key}{sep}{i}", sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def combine_properties(properties):
    """
    Combine properties from a list or dictionary into a single string.

    Args:
        properties (list or dict): Properties to combine.

    Returns:
        str: Combined properties as a string.
    """
    combined_properties = []
    if isinstance(properties, list):
        for prop in properties:
            name = prop.get('@name')
            value = prop.get('@value')
            combined_properties.append(f"{name}={value}")
    elif isinstance(properties, dict):
        name = properties.get('@name')
        value = properties.get('@value')
        combined_properties.append(f"{name}={value}")
    return '; '.join(combined_properties)

def collect_data(filenames, headers, summary_headers):
    """
    Collect data from the TeamCity API for given filenames.

    Args:
        filenames (list): List of filenames to process.
        headers (list): List of headers for the main data.
        summary_headers (list): List of headers for the summary data.

    Returns:
        tuple: Two lists containing the main data and summary data.
    """
    data = [headers]
    summary_data = [summary_headers]
    for filename in filenames:
        url = f"{TEAMCITY_URL}/httpAuth/app/rest/builds/buildType:(id:{filename}),count:1"
        headers_request = {'Accept': 'application/xml'}

        row = ["N/A"] * len(headers)
        summary_row = ["N/A"] * len(summary_headers)
        try:
            print(f"Processing build type ID: {filename}")
            response = requests.get(url, headers=headers_request, verify=False, auth=(TEAMCITY_USERNAME, TEAMCITY_PASSWORD))
            response.raise_for_status()
            build_info_dict = xmltodict.parse(response.content)
            print("Build info dictionary:", build_info_dict)

            if 'build' in build_info_dict:
                flattened_build_info = flatten_dict(build_info_dict['build'])
                properties = build_info_dict['build'].get('properties', {}).get('property', [])
                combined_properties = combine_properties(properties)
                for key, value in flattened_build_info.items():
                    if key in headers:
                        row[headers.index(key)] = value
                    if key in summary_headers and key != 'project.properties':
                        summary_row[summary_headers.index(key)] = value
                row[headers.index('project.properties')] = combined_properties
                summary_row[summary_headers.index('project.properties')] = combined_properties
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                print(f"No build found for: {filename}")
            else:
                print(f"HTTP error occurred for {filename}: {http_err}")
        except Exception as err:
            print(f"Error occurred for {filename}: {err}")
        data.append(row)
        summary_data.append(summary_row)
    return data, summary_data

def remove_duplicates(headers):
    """
    Remove duplicate headers.

    Args:
        headers (list): List of headers to process.

    Returns:
        list: List of unique headers.
    """
    seen = set()
    unique_headers = []
    for header in headers:
        if header not in seen:
            unique_headers.append(header)
            seen.add(header)
    return unique_headers

def main():
    """
    Main function to collect build information from TeamCity and write it to an Excel file.
    """
    filenames = traverse_teamcity_folder(teamcity_folder_path)
    print(filenames)
    print("Python executable path:", sys.executable)

    headers = remove_duplicates(HEADERS_ORDER)
    summary_headers = remove_duplicates(SUMMARY_HEADERS)

    # Ensure 'project.properties' is not duplicated in headers and summary_headers
    headers = [header for header in headers if header != 'project.properties']
    headers.append('project.properties')

    summary_headers = [header for header in summary_headers if header != 'project.properties']
    summary_headers.append('project.properties')

    data, summary_data = collect_data(filenames, headers, summary_headers)

    write_to_excel(EXCEL_FILE, data, 'Builds')
    # write_to_excel(EXCEL_FILE, summary_data, 'Last_Pipeline_Build_Info_Summary')

    print(f"Local spreadsheet '{EXCEL_FILE}' updated with pipeline information in 'Builds")

if __name__ == "__main__":
    main()
