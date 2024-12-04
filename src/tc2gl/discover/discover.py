# Import the main functions from the respective files
from tc2gl.discover.pipeline_summary import main as pipeline_summary_main
from tc2gl.discover.parse_teamcity_folder_xml import main as parse_teamcity_folder_main
from tc2gl.discover.get_last_pipeline_build import main as get_last_pipeline_build_main
from tc2gl.discover.pipeline_coverage import main as pipeline_coverage


def generate_pipeline_summary():
    # Directly call the main function in pipeline_summary.py
    pipeline_summary_main()


def generate_pipeline_report():
    # Directly call the main function in parse_teamcity_folder_xml.py
    parse_teamcity_folder_main()


def generate_last_build_for_pipeline():
    # Directly call the main function in get_last_pipeline_build.py
    get_last_pipeline_build_main()

def generate_pipeline_coverage():
    pipeline_coverage()
