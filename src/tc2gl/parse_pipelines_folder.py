import os
import xml.etree.ElementTree as ET

# Defines a function to safely get attributes from an XML element
def safe_get(element, key, default=None):
    if element is not None:
        return element.get(key, default)
    return default

# Defines a function to parse an XML file and extract required attributes
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    build_type = root.find('buildType')
    uuid = safe_get(build_type, 'id')
    name = safe_get(build_type, 'name')

    build_runners = []
    steps = build_type.find('steps')
    if steps is not None:
        for step in steps.findall('step'):
            runner_id = safe_get(step, 'id')
            runner_name = safe_get(step, 'name')
            runner_type = safe_get(step, 'type')
            runner_params = {safe_get(param, 'name'): safe_get(param, 'value') for param in step.findall('properties/property')}
            build_runners.append({
                'id': runner_id,
                'name': runner_name,
                'type': runner_type,
                'params': runner_params
            })

    build_extensions = []
    features = build_type.find('features')
    if features is not None:
        for feature in features.findall('feature'):
            extension_id = safe_get(feature, 'id')
            extension_type = safe_get(feature, 'type')
            extension_params = {safe_get(param, 'name'): safe_get(param, 'value') for param in feature.findall('properties/property')}
            build_extensions.append({
                'id': extension_id,
                'type': extension_type,
                'params': extension_params
            })

    triggers = []
    triggers_element = build_type.find('triggers')
    if triggers_element is not None:
        for trigger in triggers_element.findall('trigger'):
            trigger_id = safe_get(trigger, 'id')
            trigger_type = safe_get(trigger, 'type')
            trigger_params = {safe_get(param, 'name'): safe_get(param, 'value') for param in trigger.findall('properties/property')}
            triggers.append({
                'id': trigger_id,
                'type': trigger_type,
                'params': trigger_params
            })

    snapshot_dependencies = []
    snapshot_dependencies_element = build_type.find('snapshot-dependencies')
    if snapshot_dependencies_element is not None:
        print("Snapshot dependencies element found")
        for child in snapshot_dependencies_element.findall('snapshot-dependency'):
            print(f"Snapshot child element: {ET.tostring(child, encoding='unicode')}")
            snapshot_id = safe_get(child, 'id')
            snapshot_params = {safe_get(param, 'name'): safe_get(param, 'value') for param in child.findall('properties/property')}
            source_build_type = child.find('source-buildType')
            source_build_type_info = {
                'id': safe_get(source_build_type, 'id'),
                'name': safe_get(source_build_type, 'name'),
                'description': safe_get(source_build_type, 'description'),
                'projectName': safe_get(source_build_type, 'projectName'),
                'projectId': safe_get(source_build_type, 'projectId'),
                'href': safe_get(source_build_type, 'href'),
                'webUrl': safe_get(source_build_type, 'webUrl')
            } if source_build_type is not None else {}
            snapshot_dependencies.append({
                'id': snapshot_id,
                'params': snapshot_params,
                'source_build_type': source_build_type_info
            })
        print(f"Snapshot dependencies: {snapshot_dependencies}")
    else:
        print("No snapshot dependencies element found")

    artifact_dependencies = []
    artifact_dependencies_element = build_type.find('artifact-dependencies')
    if artifact_dependencies_element is not None:
        print("Artifact dependencies element found")
        for child in artifact_dependencies_element.findall('artifact-dependency'):
            print(f"Artifact child element: {ET.tostring(child, encoding='unicode')}")
            artifact_id = safe_get(child, 'id')
            artifact_params = {safe_get(param, 'name'): safe_get(param, 'value') for param in child.findall('properties/property')}
            source_build_type = child.find('source-buildType')
            source_build_type_info = {
                'id': safe_get(source_build_type, 'id'),
                'name': safe_get(source_build_type, 'name'),
                'description': safe_get(source_build_type, 'description'),
                'projectName': safe_get(source_build_type, 'projectName'),
                'projectId': safe_get(source_build_type, 'projectId'),
                'href': safe_get(source_build_type, 'href'),
                'webUrl': safe_get(source_build_type, 'webUrl')
            } if source_build_type is not None else {}
            artifact_dependencies.append({
                'id': artifact_id,
                'params': artifact_params,
                'source_build_type': source_build_type_info
            })
        print(f"Artifact dependencies: {artifact_dependencies}")
    else:
        print("No artifact dependencies element found")

    return uuid, name, build_runners, build_extensions, triggers, snapshot_dependencies, artifact_dependencies

# Defines a function to traverse the XML folder and parse XML files
def traverse_and_parse():
    build_types = {}
    folder_path = ".teamcity"
    # Traverse the folder structure
    for root, dirs, files in os.walk(folder_path):
        # Check if the current directory is named 'buildtypes'
        if os.path.basename(root) == "buildTypes":
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    try:
                        uuid, name, build_runners, build_extensions, triggers, snapshot_dependencies, artifact_dependencies = parse_xml(file_path)
                        if uuid not in build_types:
                            build_types[uuid] = {
                                'name': name,
                                'files': [],
                                'build_runners': [],
                                'build_extensions': [],
                                'triggers': [],
                                'snapshot_dependencies': [],
                                'artifact_dependencies': []
                            }
                        build_types[uuid]['files'].append(file_path)
                        build_types[uuid]['build_runners'].extend(build_runners)
                        build_types[uuid]['build_extensions'].extend(build_extensions)
                        build_types[uuid]['triggers'].extend(triggers)
                        build_types[uuid]['snapshot_dependencies'].extend(snapshot_dependencies)
                        build_types[uuid]['artifact_dependencies'].extend(artifact_dependencies)
                    except ET.ParseError as e:
                        print(f"Error parsing XML from file {file_path}: {e}")
                    except KeyError as e:
                        print(f"KeyError for file {file_path}: missing key {e}")
                    except Exception as e:
                        print(f"Unexpected error for file {file_path}: {e}")

    return build_types

def parse():
    build_types =  traverse_and_parse()
    print(build_types)
    # Writes the organized data to a file
    output_file = 'parsed_pipelines_folder_xml.txt'
    with open(output_file, 'w') as file:
        for uuid, data in build_types.items():
            file.write(f"UUID: {uuid}\n")
            file.write(f"Name: {data['name']}\n")
            file.write("Files:\n")
            for file_path in data['files']:
                file.write(f"  - {file_path}\n")

            file.write("Build Runners:\n")
            for runner in data['build_runners']:
                file.write(f"  ID: {runner['id']}\n")
                file.write(f"  Name: {runner['name']}\n")
                file.write(f"  Type: {runner['type']}\n")
                file.write("  Params:\n")
                for param_name, param_value in runner['params'].items():
                    file.write(f"    {param_name}: {param_value}\n")

            file.write("Build Extensions:\n")
            for extension in data['build_extensions']:
                file.write(f"  ID: {extension['id']}\n")
                file.write(f"  Type: {extension['type']}\n")
                file.write("  Params:\n")
                for param_name, param_value in extension['params'].items():
                    file.write(f"    {param_name}: {param_value}\n")

            file.write("Triggers:\n")
            for trigger in data['triggers']:
                file.write(f"  ID: {trigger['id']}\n")
                file.write(f"  Type: {trigger['type']}\n")
                file.write("  Params:\n")
                for param_name, param_value in trigger['params'].items():
                    file.write(f"    {param_name}: {param_value}\n")

            file.write("Snapshot Dependencies:\n")
            for snapshot in data['snapshot_dependencies']:
                file.write(f"  ID: {snapshot['id']}\n")
                file.write("  Params:\n")
                for param_name, param_value in snapshot['params'].items():
                    file.write(f"    {param_name}: {param_value}\n")
                file.write("  Source Build Type:\n")
                for key, value in snapshot['source_build_type'].items():
                    file.write(f"    {key}: {value}\n")

            file.write("Artifact Dependencies:\n")
            for artifact in data['artifact_dependencies']:
                file.write(f"  ID: {artifact['id']}\n")
                file.write("  Params:\n")
                for param_name, param_value in artifact['params'].items():
                    file.write(f"    {param_name}: {param_value}\n")
                file.write("  Source Build Type:\n")
                for key, value in artifact['source_build_type'].items():
                    file.write(f"    {key}: {value}\n")
                file.write("\n")

    print(f"Data written to {output_file}")
