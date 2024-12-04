import os
import json
import requests
import xmltodict

# Import the main functions from the respective scripts
from tc2gl.fetch.export_tc_pipelines_to_repo import export_pipelines as export_pipelines
from tc2gl.fetch.download_pipelines_from_gitlab_using_git import download_pipelines_git as download_pipelines_git
from tc2gl.fetch.download_pipelines_from_gitlab_https import download_pipelines_https as download_pipelines_https

# TeamCity server configuration fetched from environment variables
TEAMCITY_URL = os.environ.get('TEAMCITY_URL', 'https://teamcity.test-digital.com')
TEAMCITY_USERNAME = os.environ.get('TEAMCITY_USERNAME', 'test')
TEAMCITY_PASSWORD = os.environ.get('TEAMCITY_PASSWORD', 'test')


def save_xml(pipelines_dict, build_types, separate_summary_files=False):
    """
    Save the pipelines data in XML format.

    Args:
        pipelines_dict (dict): Dictionary containing all pipelines data.
        build_types (list): List of individual pipeline data.
        separate_summary_files (bool): If True, saves each pipeline as a separate file. If False, saves all in one summary file.

    Returns:
        None
    """
    os.makedirs('.teamcity/xml', exist_ok=True)
    if separate_summary_files:
        for pipeline in build_types:
            pipeline_id = pipeline['@id']
            with open(f'.teamcity/xml/{pipeline_id}.xml', 'w') as xml_file:
                xml_file.write(xmltodict.unparse({'buildType': pipeline}, pretty=True) + '\n')
    else:
        with open('.teamcity/xml/pipelines_summary.xml', 'w') as xml_file:
            xml_file.write(xmltodict.unparse({'buildTypes': pipelines_dict}, pretty=True) + '\n')


def save_json(build_types, separate_summary_files=False):
    """
    Save the pipelines data in JSON format.

    Args:
        build_types (list): List of individual pipeline data.
        separate_summary_files (bool): If True, saves each pipeline as a separate file. If False, saves all in one summary file.

    Returns:
        None
    """
    os.makedirs('.teamcity/json', exist_ok=True)
    if separate_summary_files:
        for pipeline in build_types:
            pipeline_id = pipeline['@id']
            with open(f'.teamcity/json/{pipeline_id}.json', 'w') as json_file:
                json.dump(pipeline, json_file, indent=4)
    else:
        with open('.teamcity/json/pipelines_summary.json', 'w') as json_file:
            json.dump(build_types, json_file, indent=4)


def get_teamcity_pipelines_by_server_api_export_query():
    """
    Call the function from the external script to export pipelines from TeamCity to a repository using a server API query.
    """
    export_pipelines()


def get_teamcity_pipelines_by_server_api_query(format_type, separate_files=False):
    """
    Fetch pipelines from TeamCity server using an API query and save in the specified format.

    Args:
        format_type (str): The format to save the pipelines data ('xml', 'json', or 'both').
        separate_files (bool): If True, saves each pipeline as a separate file. If False, saves all in one summary file.

    Returns:
        list: List of build types (pipelines) fetched from the server.
    """
    url = f"{TEAMCITY_URL}/httpAuth/app/rest/buildTypes"
    headers = {'Accept': 'application/xml'}
    response = requests.get(url, headers=headers, auth=(TEAMCITY_USERNAME, TEAMCITY_PASSWORD))
    response.raise_for_status()  # This will raise an error for bad responses

    pipelines_dict = xmltodict.parse(response.content)
    build_types = pipelines_dict.get('buildTypes', {}).get('buildType', [])

    if format_type in ['xml', 'both']:
        save_xml(pipelines_dict, build_types, separate_files)
        print(f"Pipelines saved in {format_type} format.")

    if format_type in ['json', 'both']:
        save_json(build_types, separate_files)
    return build_types


def get_teamcity_pipelines_from_gitlab_git_query():
    """
    Call the function from the external script to download pipelines from GitLab using Git.
    """
    download_pipelines_git()


def get_teamcity_pipelines_by_gitlab_https_query():
    """
    Call the function from the external script to download pipelines from GitLab using HTTPS.
    """
    download_pipelines_https()
