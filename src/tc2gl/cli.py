import argparse

# from tc2gl.translate.extractor import translate_pipeline_folder
from tc2gl.delete_tc_folder import delete_tc_folder as delete_tc_folder
from tc2gl.fetch.fetch import (
    get_teamcity_pipelines_by_server_api_query,
    get_teamcity_pipelines_by_server_api_export_query,
    get_teamcity_pipelines_by_gitlab_https_query,
    get_teamcity_pipelines_from_gitlab_git_query,
)
from tc2gl.process_pipeline import (
    process_build_types_server_api_query,
    process_pipeline_folder
)
from tc2gl.discover.discover import (
    generate_pipeline_summary,
    generate_pipeline_report,
    generate_last_build_for_pipeline,
    generate_pipeline_coverage,
)


def fetch(source, include_summary_pipelines):
    """
    Fetch data from the specified source and process it.

    Args:
        source (str): The source from which to fetch data.
        include_summary_pipelines (bool): Whether to include summary pipelines.
    """
    print(f"clean .teamcity folder if it exists")
    delete_tc_folder(".teamcity")
    print(f"clean .gitlab folder if it exists")
    delete_tc_folder(".gitlab")
    print(f"Fetching data from: {source}")
    print(f"Include summary pipelines: {include_summary_pipelines}")

    if source == "server-api-query":
        build_types = get_teamcity_pipelines_by_server_api_query(include_summary_pipelines)
        process_build_types_server_api_query(build_types)
        process_pipeline_folder()
    elif source == "server-api-export-query":
        get_teamcity_pipelines_by_server_api_export_query()
    elif source == "gitlab-api-https-query":
        get_teamcity_pipelines_by_gitlab_https_query()
    elif source == "gitlab-api-git-query":
        get_teamcity_pipelines_from_gitlab_git_query()


def discover():
    """
    Discover Pipeline information.
    """
    print("Discovering information")
    generate_pipeline_summary()
    generate_pipeline_report()
    generate_last_build_for_pipeline()
    generate_pipeline_coverage()

def main():
    parser = argparse.ArgumentParser(description="A CLI tool with fetch and discover commands.")
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    # Fetch subcommand
    parser_fetch = subparsers.add_parser('fetch', help='Fetch pipelines from the Server URL and credentials should be set as environment variables')
    parser_fetch.add_argument('--source', choices=['server-api-query', 'server-api-export-query', 'gitlab-api-https-query', 'gitlab-api-git-query'], default='server-api-query', help='Enter source to retrieve pipelines from')
    parser_fetch.add_argument('--include-summary-pipelines', action='store_true', help='Include summary of the pipelines')

    # Discover subcommand
    parser_discover = subparsers.add_parser('discover', help='Discover information')
    parser_discover.set_defaults(func=discover)

    args = parser.parse_args()

    if args.command == 'fetch':
        fetch(args.source, args.include_summary_pipelines)
    elif args.command == 'discover':
        discover()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
