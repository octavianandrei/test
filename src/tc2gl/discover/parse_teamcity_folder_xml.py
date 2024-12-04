import os
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from tc2gl.excel.excel_writer import write_to_excel

# Define the path to the .teamcity folder
teamcity_folder_path = ".teamcity"
EXCEL_FILE = 'TC2GL.xlsx'

# This script traverses a `.teamcity` folder, parses XML files, flattens their data,
# merges the data, formats it for a spreadsheet, and writes the results into an Excel file.

def parse_xml(file_path):
    """Parse an XML file and return its root element."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def flatten_element(element, parent_key='', sep='.'):
    """Flatten an XML element into an OrderedDict, concatenating keys for nested elements."""
    items = OrderedDict()
    if element.attrib:
        for k, v in element.attrib.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items[new_key] = v

    if element.text and element.text.strip():
        items[parent_key] = element.text.strip()

    child_count = {}
    for child in element:
        child_tag = child.tag
        if child_tag not in child_count:
            child_count[child_tag] = 0
        child_count[child_tag] += 1

        new_key = f"{parent_key}{sep}{child_tag}{child_count[child_tag]}" if parent_key else f"{child_tag}{child_count[child_tag]}"

        if child_tag in ["runner", "extension", "build-trigger", "snapshot-dependency", "artifact-dependency", "options", "parameters", "project-extension", "parameter"]:
            params = OrderedDict()
            for param in child.findall(".//param"):
                param_name = param.attrib.get("name")
                param_value = param.attrib.get("value")
                if param_name and param_value:
                    params[param_name] = param_value

            for option in child.findall(".//option"):
                option_name = option.attrib.get("name")
                option_value = option.attrib.get("value")
                if option_name and option_value:
                    params[option_name] = option_value

            items[new_key] = '; '.join(f"{k}={v}" for k, v in params.items())
        else:
            items.update(flatten_element(child, new_key, sep=sep))

    return items

def merge_data(subfolder, build_types, flattened_data):
    """Merge flattened data into the build_types dictionary under the specified subfolder."""
    if subfolder in build_types:
        for key, value in flattened_data.items():
            if key in build_types[subfolder]:
                build_types[subfolder][key] += f" | {value}"
            else:
                build_types[subfolder][key] = value
    else:
        build_types[subfolder] = flattened_data

def traverse_teamcity_folder(folder_path):
    """Traverse the .teamcity folder, parse XML files, flatten and merge their data."""
    build_types = defaultdict(OrderedDict)
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            build_types_path = os.path.join(subfolder_path, 'buildTypes')
            if os.path.exists(build_types_path):
                for root, dirs, files in os.walk(build_types_path):
                    for file in files:
                        if file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            root_element = parse_xml(file_path)
                            flattened_data = flatten_element(root_element)
                            merge_data(subfolder, build_types, flattened_data)
            project_config_path = os.path.join(subfolder_path, 'project-config.xml')
            if os.path.exists(project_config_path):
                root_element = parse_xml(project_config_path)
                flattened_data = flatten_element(root_element)
                merge_data(subfolder, build_types, flattened_data)

    return list(build_types.values())

def format_data_for_spreadsheet(data):
    """Format the flattened data for writing to a spreadsheet."""
    if not data:
        return []

    headers = sorted(set(key for item in data for key in item.keys()))
    formatted_data = [headers]
    for item in data:
        row = [item.get(header, 'N/A') for header in headers]
        formatted_data.append(row)
    return formatted_data

def main():
    """Main function to traverse the .teamcity folder, parse and flatten XML files, and write the data to an Excel file."""
    build_types_data = traverse_teamcity_folder(teamcity_folder_path)
    formatted_data = format_data_for_spreadsheet(build_types_data)

    # Write to the same workbook
    write_to_excel(EXCEL_FILE, formatted_data, 'Inventory')

    print(f"Local spreadsheet '{EXCEL_FILE}' updated with pipeline information in 'Inventory' worksheet.")

if __name__ == "__main__":
    main()
