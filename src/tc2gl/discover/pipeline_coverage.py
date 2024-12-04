import os
import xml.etree.ElementTree as ET
from xml.sax.saxutils import unescape
import numpy as np
import pandas as pd
from tc2gl.excel.excel_writer import write_to_excel, sheet_exists, create_initial_excel_file, is_excel_file, delete_sheet_if_exists


def extract_teamcity_data(xml_file):
    """
    Extract build steps from a TeamCity XML configuration file (supports both XML 1 and XML 2).

    :param xml_file: Path to the TeamCity XML configuration file
    :return: List of build steps extracted from the XML file
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    build_steps = []

    # XML 1: Runners are under <runner>
    for runner in root.findall('.//runner'):
        step = {
            'id': runner.get('name'),
            'type': runner.get('type'),
            'params': {}
        }
        # Extract parameters for each runner
        for param in runner.findall('.//param'):
            name = param.get('name')
            value = param.get('value')
            if value:
                # Handle CDATA sections in the XML
                if value.startswith('<![CDATA[') and value.endswith(']]>'):
                    value = value[9:-3]  # Strip CDATA tags
                value = unescape(value)
            else:
                value = param.text if param.text else ''  # Get text content if value attribute is empty
            step['params'][name] = value

        build_steps.append(step)

    # XML 2: Steps are under <step>, and parameters are inside <properties>
    for step_elem in root.findall('.//steps/step'):
        step = {
            'id': step_elem.get('id'),
            'type': step_elem.get('type'),
            'params': {}
        }
        # Extract parameters inside <properties>
        properties = step_elem.find('.//properties')
        if properties is not None:
            for prop in properties.findall('.//property'):
                name = prop.get('name')
                value = prop.get('value')
                if value:
                    # Handle CDATA sections in the XML
                    if value.startswith('<![CDATA[') and value.endswith(']]>'):
                        value = value[9:-3]  # Strip CDATA tags
                    value = unescape(value)
                else:
                    value = prop.text if prop.text else ''  # Get text content if value attribute is empty
                step['params'][name] = value

        build_steps.append(step)

    return build_steps


def read_completion_weight_from_config(config_file, job_name):
    """
    Reads the completion weight for a specific job from the configuration file.

    :param config_file: Path to the configuration file
    :param job_name: Name of the job
    :return: Completion weight as a float, or None if the job name is not found
    """
    try:
        with open(config_file, 'r') as file:
            lines = file.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            if key.strip().lower() == job_name.lower():
                return float(value.strip())
        return None  # Job name not found in the config file
    except (ValueError, IOError) as e:
        print(f"Error reading completion weight from config file: {e}")
        return None


def update_completion_weight(job_name, job_names):
    """
    Update the completion weight in the Excel sheet.

    :param job_name: Name of the job
    :param job_names: List of job names
    """
    file_path = 'TC2GL.xlsx'
    sheet_name = 'Coverage'
    config_file = './completion_weight.config'
    # Read the existing data
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    for step in job_names:
        # Read completion weight from configuration file for each job
        step = step.get("type")
        completion_weight = read_completion_weight_from_config(config_file, step)
        if completion_weight is None:
            print(f"Invalid completion weight for {step}. Skipping update.")
            continue

        df.loc[(df['Pipeline'] == job_name) & (df['Steps'].str.lower() == step.lower()), 'Completion Weight'] = completion_weight

    df = df[['Pipeline', 'Steps', 'Completion Weight', 'Docker image']]
    write_to_excel(file_path, [['Pipeline', 'Steps', 'Completion Weight', 'Docker image']] + df.values.tolist(), sheet_name, ensure_columns=['Pipeline', 'Steps', 'Completion Weight', 'Docker image'])
    print(f"Updated completion weight for {job_name}")



def add_initial_pipeline_details(job_name, build_steps):
    """
    Add initial pipeline details to the Excel file.

    This function adds each step of a pipeline to the Excel file with an initial completion
    weight set to 0.

    :param job_name: Name of the pipeline job
    :param build_steps: List of build steps for the pipeline
    """
    file_path = 'TC2GL.xlsx'
    sheet_name = 'Coverage'

    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Add each build step to the DataFrame
    for step in build_steps:
        step_name = step['type']
        runtime = step.get('params', {}).get('plugin.docker.imageId', "")
        df = pd.concat([df, pd.DataFrame({'Pipeline': [job_name], 'Steps': [step_name], 'Docker image': [runtime], 'Completion Weight': [0]})], ignore_index=True)

    df = df[['Pipeline', 'Steps', 'Docker image', 'Completion Weight']]

    write_to_excel(file_path, [['Pipeline', 'Steps', 'Docker image', 'Completion Weight']] + df.values.tolist(), sheet_name, ensure_columns=['Pipeline', 'Steps', 'Docker image', 'Completion Weight'])

def main():
    """Main function to generate pipeline coverage sheet."""
    teamcity_folder_path = ".teamcity"
    file_path = 'TC2GL.xlsx'
    sheet_name = 'Coverage'
    delete_sheet_if_exists(file_path, sheet_name)

    if not os.path.exists(file_path) or not sheet_exists(file_path, sheet_name):
        create_initial_excel_file(file_path, sheet_name)

    for subfolder in os.listdir(teamcity_folder_path):
        subfolder_path = os.path.join(teamcity_folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            build_types_path = os.path.join(subfolder_path, 'buildTypes')
            if os.path.exists(build_types_path):
                # Walk through the buildTypes directory
                for root, dirs, files in os.walk(build_types_path):
                    for file in files:
                        if file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            build_steps = extract_teamcity_data(file_path)
                            job_name = os.path.splitext(file)[0]  # Use the file name without extension as the job name
                            add_initial_pipeline_details(job_name, build_steps)
                            update_completion_weight(job_name, build_steps)

if __name__ == "__main__":
    main()
