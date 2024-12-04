import os
import xml.etree.ElementTree as ET
import numpy as np
from tc2gl.excel.excel_writer import write_to_excel

# Define the path to the .teamcity folder
teamcity_folder_path = ".teamcity"
EXCEL_FILE = 'TC2GL.xlsx'

# Define weights for the criteria
weights = {
    "Total Build Steps": 0.0875,
    "Total Dependencies": 0.0875,
    "Total Artifact Dependencies": 0.0875,
    "Pipeline Secrets": 0.0875,
    "Project Secrets": 0.0875,
    "Number of Integrations": 0.0875,
    "Total Build Step Params": 0.0875,
    "Total Project Parameters": 0.0875,
    "Total Lines Of Code": 0.0375,
    "Total Build Extensions": 0.0375,
    "Total Build Extension Params": 0.0375,
    "Total Build Triggers": 0.0375,
    "Total Project Extensions": 0.0375,
    "Total Project Extension Params": 0.0375,
    "Unique Plugins": 0.0375,
    "Plugin Data Subfolders": 0.0375
}

# Normalize weights to ensure they sum to 1
total_weight = sum(weights.values())
normalized_weights = {key: value / total_weight for key, value in weights.items()}

def parse_xml(file_path):
    """Parse an XML file and return its root and tree."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root, tree

def count_elements(element, *tags):
    """Count the number of elements with a specific tag in the XML element."""
    count = 0
    for tag in tags:
        count += len(element.findall(f".//{tag}"))
    return count

def count_params(element, *tags):
    """Count the number of parameters in elements with a specific tag."""
    count = 0
    for tag in tags:
        for item in element.findall(f".//{tag}"):
            count += len(item.findall(".//param"))
    return count

def count_secrets(element):
    """Count the number of secure parameters in the XML element."""
    count = 0
    for param in element.findall(".//param") + element.findall(".//property"):
        param_name = param.attrib.get("name", "")
        param_value = param.attrib.get("value", "")
        if param_name.startswith("secure:") or param_value.startswith("zxx"):
            count += 1
    return count

def count_lines(file_path):
    """Count the number of lines in a file."""
    return sum(1 for _ in open(file_path))

def count_integrations(element):
    """Count the number of integrations in the XML element."""
    integrations = set()
    for param in element.findall(".//param") + element.findall(".//property"):
        param_value = param.attrib.get("value", "").lower()
        if any(integration in param_value for integration in ['datadog', 'aws', 'gcp', 'azure', 'vault']):
            integrations.add(param_value)
    return len(integrations)

def count_unique_plugins(element):
    """Count the number of unique plugins in the XML element."""
    plugins = set()
    for param in element.findall(".//param") + element.findall(".//property"):
        param_name = param.attrib.get("name", "").lower()
        if param_name.startswith("plugin."):
            plugin_type = param_name.split(".")[1]
            plugins.add(plugin_type)
    return len(plugins)

def count_plugin_data_subfolders(subfolder_path):
    """Count the number of subfolders in the plugin data directory."""
    plugin_data_path = os.path.join(subfolder_path, 'pluginData')
    if os.path.exists(plugin_data_path) and os.path.isdir(plugin_data_path):
        return len([name for name in os.listdir(plugin_data_path) if os.path.isdir(os.path.join(plugin_data_path, name))])
    return 0

def count_build_extensions(element):
    """Count the number of build extensions in the XML element. Handles both XML 1 and XML 2 structures."""
    # XML 1 uses <extension>, XML 2 uses <features> and <feature>
    return len(element.findall(".//features/feature")) + len(element.findall(".//extension"))

def count_build_extension_params(element):
    """Count the number of properties inside build extensions, handling both XML 1 and XML 2 structures."""
    count = 0
    # XML 1 uses <extension> and <param>, XML 2 uses <feature> and <property>
    for feature in element.findall(".//features/feature") + element.findall(".//extension"):
        properties = feature.find(".//properties")
        if properties is not None:
            count += len(properties.findall(".//property"))  # For XML 2 <properties>
        count += len(feature.findall(".//param"))  # For XML 1 <param>
    return count

def count_step_params(root_element):
    """Count the number of parameters in all step elements, handling both XML 1 and XML 2 structures."""
    count = 0
    # XML 1 uses <runner> and <param>, XML 2 uses <step> and <property>
    for step in root_element.findall(".//step") + root_element.findall(".//runner"):
        properties = step.find(".//properties")
        if properties is not None:
            count += len(properties.findall(".//property"))  # For XML 2 <properties>
        count += len(step.findall(".//param"))  # For XML 1 <param>
    return count

def count_total_build_steps(root_element):
    """Count the total number of build steps from the XML structure, handling both XML 1 and XML 2 structures."""
    # XML 1 uses <runner>, XML 2 uses <step>
    steps_element = root_element.find(".//steps")
    if steps_element is not None:
        return len(steps_element.findall(".//step"))
    return len(root_element.findall(".//runner"))

def generate_summary_for_pipeline(file_path):
    """Generate a summary of metrics for a pipeline, supports both XML formats."""
    root_element, tree = parse_xml(file_path)
    pipeline_name = os.path.splitext(os.path.basename(file_path))[0]

    summary = {
        'Pipeline': pipeline_name,
        'Total Lines Of Code': count_lines(file_path),
        'Total Build Steps': count_total_build_steps(root_element),
        'Total Build Step Params': count_step_params(root_element),
        'Total Build Extensions': count_build_extensions(root_element),
        'Total Build Extension Params': count_build_extension_params(root_element),
        'Total Dependencies': count_elements(root_element, 'depend-on', 'snapshot-dependency'),
        'Total Artifact Dependencies': count_elements(root_element, 'dependency', 'artifact-dependency'),
        'Total Build Triggers': count_elements(root_element, 'build-trigger', 'trigger'),
        'Pipeline Secrets': count_secrets(root_element),
        'Number of Integrations': count_integrations(root_element),
        'Unique Plugins': count_unique_plugins(root_element)
    }
    return summary

def generate_summary_for_project(file_path):
    """Generate a summary of metrics for a project."""
    root_element, tree = parse_xml(file_path)
    summary = {
        'Total Project Extensions': count_elements(root_element, 'project-extensions/extension'),
        'Total Project Extension Params': count_params(root_element, 'project-extensions/extension'),
        'Total Project Parameters': count_elements(root_element, 'parameters/param'),
        'Project Secrets': count_secrets(root_element),
        'Total Lines Of Code': count_lines(file_path),
        'Number of Integrations': count_integrations(root_element),
        'Unique Plugins': count_unique_plugins(root_element)
    }
    return summary

def traverse_teamcity_folder(folder_path):
    """Traverse the TeamCity folder and generate summaries for pipelines and projects."""
    summaries = {}
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)
        if os.path.isdir(subfolder_path):
            if subfolder not in summaries:
                summaries[subfolder] = {
                    'Subfolder': subfolder,
                    'Pipeline': '',
                    'Total Lines Of Code': 0,
                    'Total Build Steps': 0,
                    'Total Build Step Params': 0,
                    'Total Build Extensions': 0,
                    'Total Build Extension Params': 0,
                    'Total Dependencies': 0,
                    'Total Artifact Dependencies': 0,
                    'Total Build Triggers': 0,
                    'Total Project Extensions': 0,
                    'Total Project Extension Params': 0,
                    'Total Project Parameters': 0,
                    'Pipeline Secrets': 0,
                    'Project Secrets': 0,
                    'Number of Integrations': 0,
                    'Unique Plugins': 0,
                    'Plugin Data Subfolders': 0
                }

            # Process buildTypes XML files
            build_types_path = os.path.join(subfolder_path, 'buildTypes')
            if os.path.exists(build_types_path):
                for root, dirs, files in os.walk(build_types_path):
                    for file in files:
                        if file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            pipeline_summary = generate_summary_for_pipeline(file_path)
                            summaries[subfolder]['Pipeline'] = pipeline_summary['Pipeline']
                            for key, value in pipeline_summary.items():
                                if key != 'Pipeline':
                                    summaries[subfolder][key] += value

            # Process project-config.xml file
            project_config_path = os.path.join(subfolder_path, 'project-config.xml')
            if os.path.exists(project_config_path):
                project_summary = generate_summary_for_project(project_config_path)
                for key, value in project_summary.items():
                    summaries[subfolder][key] += value

            # Count plugin data subfolders
            summaries[subfolder]['Plugin Data Subfolders'] = count_plugin_data_subfolders(subfolder_path)

    return list(summaries.values())

def normalize_data(data, epsilon=1e-6):
    """Normalize the data to ensure it scales properly."""
    return (data + epsilon) / (np.max(data, axis=0) + epsilon)

def calculate_wsm_score(data, weights):
    """Calculate the Weighted Sum Model (WSM) score for the data."""
    normalized_data = normalize_data(data)
    weighted_data = normalized_data * weights
    scores = np.sum(weighted_data, axis=1)
    return scores

def add_wsm_scores_to_summaries(summaries):
    """Add WSM scores to the summaries."""
    relevant_columns = ["Total Build Steps", "Total Dependencies", "Total Artifact Dependencies", "Pipeline Secrets",
                        "Project Secrets", "Number of Integrations", "Total Build Step Params",
                        "Total Project Parameters", "Total Lines Of Code", "Total Build Extensions",
                        "Total Build Extension Params", "Total Build Triggers", "Total Project Extensions",
                        "Total Project Extension Params", "Unique Plugins", "Plugin Data Subfolders"]

    # Prepare data array by collecting the relevant columns from each summary
    data = np.array([[summary.get(col, 0) for col in relevant_columns] for summary in summaries])

    # Convert normalized_weights to an array corresponding to the relevant columns
    weights_array = np.array([normalized_weights[col] for col in relevant_columns])

    # Calculate WSM scores
    scores = calculate_wsm_score(data, weights_array)

    # Add WSM score to each summary
    for i, score in enumerate(scores):
        summaries[i]['WSM Score'] = score

    # Rank the summaries based on WSM scores
    sorted_summaries = sorted(summaries, key=lambda x: x['WSM Score'], reverse=True)

    # Add ranks to summaries based on the sorted order
    for rank, summary in enumerate(sorted_summaries, start=1):
        summary['Rank'] = rank

def format_summary_for_spreadsheet(summaries):
    """Format the summaries for writing to a spreadsheet."""
    headers = ["Subfolder", "Pipeline", "Total Lines Of Code", "Total Build Steps", "Total Build Step Params",
               "Total Build Extensions", "Total Build Extension Params", "Total Dependencies",
               "Total Artifact Dependencies", "Total Build Triggers", "Total Project Extensions",
               "Total Project Extension Params", "Total Project Parameters", "Pipeline Secrets", "Project Secrets",
               "Number of Integrations", "Unique Plugins", "Plugin Data Subfolders", "WSM Score", "Rank"]
    formatted_data = [headers]
    for summary in summaries:
        row = [summary.get(header, 'N/A') for header in headers]
        formatted_data.append(row)
    return formatted_data

def main():
    """Main function to generate pipeline summaries, calculate WSM scores, and write data to an Excel file."""
    summaries = traverse_teamcity_folder(teamcity_folder_path)  # Traverse the TeamCity folder and generate summaries
    add_wsm_scores_to_summaries(summaries)  # Add WSM scores to the summaries

    formatted_data = format_summary_for_spreadsheet(summaries)  # Format the summaries for the spreadsheet

    # Write to the same workbook
    write_to_excel(EXCEL_FILE, formatted_data, 'Complexity')  # Write the data to the Excel file

    print(f"Local spreadsheet '{EXCEL_FILE}' updated with pipeline summary, WSM scores, and ranks in 'Complexity' worksheet.")  # Print confirmation message

if __name__ == "__main__":
    main()  # Run the main function if the script is executed directly
