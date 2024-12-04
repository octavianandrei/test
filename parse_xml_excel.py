import os
import xml.etree.ElementTree as ET
from tc2gl.excel.excel_writer import write_to_excel

# Define the path to the .teamcity folder
teamcity_folder_path = ".teamcity"

EXCEL_FILE = 'TC2GL.xlsx'

# Function to parse an XML file and extract required attributes
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    uuid = root.attrib.get('uuid')
    name = root.find('name').text if root.find('name') is not None else "Unknown"

    build_runners = []
    for runner in root.findall(".//build-runners/runner"):
        runner_id = runner.attrib.get('id')
        runner_name = runner.attrib.get('name')
        runner_type = runner.attrib.get('type')
        runner_params = {param.attrib.get('name'): param.attrib.get('value') for param in runner.findall(".//param")}
        build_runners.append({
            'id': runner_id,
            'name': runner_name,
            'type': runner_type,
            'params': runner_params
        })

    build_extensions = []
    for extension in root.findall(".//build-extensions/extension"):
        extension_id = extension.attrib.get('id')
        extension_type = extension.attrib.get('type')
        extension_params = {param.attrib.get('name'): param.attrib.get('value') for param in extension.findall(".//param")}
        build_extensions.append({
            'id': extension_id,
            'type': extension_type,
            'params': extension_params
        })

    return uuid, name, build_runners, build_extensions

# Function to traverse subfolders within .teamcity and parse XML files in buildTypes subfolder
def traverse_and_parse(folder_path):
    build_types = {}

    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            build_types_path = os.path.join(subfolder_path, 'buildTypes')
            if os.path.exists(build_types_path):
                for root, dirs, files in os.walk(build_types_path):
                    for file in files:
                        if file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            uuid, name, build_runners, build_extensions = parse_xml(file_path)
                            if uuid not in build_types:
                                build_types[uuid] = {
                                    'name': name,
                                    'files': [],
                                    'build_runners': [],
                                    'build_extensions': []
                                }
                            build_types[uuid]['files'].append(file_path)
                            build_types[uuid]['build_runners'].extend(build_runners)
                            build_types[uuid]['build_extensions'].extend(build_extensions)

    return build_types

def main():
    # Traverse and parse XML files from the folder
    build_types = traverse_and_parse(teamcity_folder_path)

    # Prepare data for Excel
    data = [["UUID", "Name", "Files", "Build Runner ID", "Build Runner Name", "Build Runner Type", "Build Runner Params", "Extension ID", "Extension Type", "Extension Params"]]

    for uuid, details in build_types.items():
        files = ', '.join(details['files'])
        for runner in details['build_runners']:
            runner_params = ', '.join([f"{key}: {value}" for key, value in runner['params'].items()])
            data.append([uuid, details['name'], files, runner['id'], runner['name'], runner['type'], runner_params, "", "", ""])

        for extension in details['build_extensions']:
            extension_params = ', '.join([f"{key}: {value}" for key, value in extension['params'].items()])
            data.append([uuid, details['name'], files, "", "", "", "", extension['id'], extension['type'], extension_params])

    # Write the data to the local Excel file
    write_to_excel(EXCEL_FILE, data, 'build_types')

    print(f"Local spreadsheet '{EXCEL_FILE}' updated with build type information.")

if __name__ == "__main__":
    main()
