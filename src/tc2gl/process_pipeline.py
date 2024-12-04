import os
import xmltodict
import requests
from tc2gl.parse_pipelines_folder import parse
# Define the path to the .teamcity folder
teamcity_folder_path = "./../../.teamcity"
TEAMCITY_URL = os.environ.get('TEAMCITY_URL', 'https://teamcity.test-digital.com')
TEAMCITY_USERNAME = os.environ.get('TEAMCITY_USERNAME', 'test')
TEAMCITY_PASSWORD = os.environ.get('TEAMCITY_PASSWORD', 'test')


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


def process_build_types_server_api_query(build_types):
    for pipeline in build_types:
        pipeline_id = pipeline['@id']
        pipeline_href = pipeline['@href']
        url = f"{TEAMCITY_URL}{pipeline_href}"
        headers = {'Accept': 'application/xml'}
        response = requests.get(url, headers=headers, auth=(TEAMCITY_USERNAME, TEAMCITY_PASSWORD))
        response.raise_for_status()
        pipeline_info = xmltodict.parse(response.content)
        #Define the path to the file
        file_path = f'.teamcity/{pipeline_id}/buildTypes/{pipeline_id}.xml'
        # Ensure the parent directories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(f'.teamcity/{pipeline_id}/buildTypes/{pipeline_id}.xml', 'w') as xml_file:
            xml_file.write(xmltodict.unparse({'buildType': pipeline_info}, pretty=True) + '\n')

def process_pipeline_folder():
    parse()

# def main():
#     filenames = traverse_teamcity_folder(teamcity_folder_path)
#     print(filenames)
#     print("Python executable path:", sys.executable)
#     for filename in filenames:
#         url = f"{TEAMCITY_URL}/httpAuth/app/rest/builds/buildType:(id:{filename}),count:1"
#         headers = {'Accept': 'application/xml'}
#
#         try:
#             response = requests.get(url, headers=headers, auth=(TEAMCITY_USERNAME, TEAMCITY_PASSWORD))
#             response.raise_for_status()  # This is where we raise the error for bad status codes
#             # Convert XML response to Python dictionary directly
#             build_info_dict = xmltodict.parse(response.content)
#         except requests.exceptions.HTTPError as http_err:
#             if response.status_code == 404:
#                 build_info_dict = {"filename": filename, "error": "no build found"}
#             else:
#                 build_info_dict = {"filename": filename, "error": str(http_err)}
#         except Exception as err:
#             build_info_dict = {"filename": filename, "error": str(err)}
#
#         print(build_info_dict)
#
#
# if __name__ == "__main__":
#     main()
