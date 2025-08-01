import os
from pathlib import Path
from typing import Dict

import pandas as pd
import requests
from ghapi.all import GhApi
from rich.progress import track

from extractor.checks import StandardCheck
from extractor.logger import logger
from extractor.render import Requirements

PYPI_URL_BASE = "https://pypi.org/pypi"
GITHUB_URL_BASE = "https://github.com"
IAC_EXCEPTIONS_LIST = [
    "hashicorp/terraform",
    "databricks/terraform-provider-databricks",
]


def is_python(project: str) -> bool:
    """
    Check if the project is a Python project.

    Args:
        project: The name of the project.

    Returns:
        A boolean value.
    """
    return project.startswith("python/")


def is_iac_project(project: str) -> bool:
    """
    Check if the project is an IAC project.

    Args:
        project: The name of the project.

    Returns:
        A boolean value.
    """
    return project in IAC_EXCEPTIONS_LIST


def get_raw_data_from_github(project: str, version: str) -> Dict[str, str]:
    """
    Retrieve raw metadata for a project from a given URL.

    Args:
        project: The name of the project.
        version: The version of the project.

    Returns:
        A dictionary containing the raw metadata of the project.
    """
    api = GhApi()
    owner, repo = project.split("/")
    data = api.repos.get_content(owner=owner, repo=repo, path="LICENSE", ref=version)
    license_url = data.get("html_url")
    return {
        "name": project,
        "version": version,
        "license": license_url,
        "pypi_release_url": "",
        "version_url": license_url.replace("/LICENSE", ""),
    }


def get_raw_data_from_pypi(project: str) -> Dict[str, str]:
    """
    Retrieve raw metadata for a project from a given URL.

    Args:
        project: The name of the project.

    Returns:
        A dictionary containing the raw metadata of the project.
    """
    try:
        r = requests.get(
            f"{PYPI_URL_BASE}/{project}/json",
            headers={"Accept": "application/json"},
            timeout=5,
        )
    except Exception as e:
        logger.error(e)
    else:
        if r.status_code == 404:
            logger.error(f"Project {project} not found")
            return {}
        return r.json()["info"]


def get_raw_data(project: str, version: str = "") -> Dict[str, str]:
    """
    Retrieve raw metadata for a project from a given URL.

    Args:
        project: The name of the project.

    Returns:
        A dictionary containing the raw metadata of the project.
    """
    if is_iac_project(project) or is_python(project):
        return get_raw_data_from_github(project, version)
    else:
        return get_raw_data_from_pypi(project)


def filter_data(raw_data: Dict[str, str], version: str) -> Dict[str, str]:
    """
    Filter relevant metadata from raw data.

    Args:
        raw_data: The raw metadata of a project.
        version: The version of the project.

    Returns:
        A dictionary containing filtered metadata.
    """
    if raw_data:
        project_name = raw_data["name"]
        project_url = raw_data["project_url"]
        project_urls = raw_data["project_urls"]
        project_version = version or raw_data["version"]
        check = StandardCheck()
        pypi_url = f"https://pypi.org/project/{project_name}/{project_version}/"
        gh_url_pattern = r"(https:\/\/|http:\/\/)github\.com"
        project_url = check.project_url(gh_url_pattern, project_url, project_urls)
        filtered_data = {
            "name": project_name,
            "version": project_version,
            "license": check.licenses(raw_data),
            # "homepage": raw_data["home_page"],
            "pypi_release_url": pypi_url,
            "project_url": check.project_url(gh_url_pattern, project_url, project_urls),
        }

        logger.info(f"Searching GitHub url for: {project_name}")

        filtered_data = check.version(version, gh_url_pattern, filtered_data)
        filtered_data["version_url"] = (
            filtered_data["version_url"]
            if filtered_data["version_url"]
            not in [check.project_default_error, check.version_default_error]
            else pypi_url
        )
        del filtered_data["project_url"]
        return filtered_data

    return {}


def extract_data(source_path: Path, format: str) -> None:
    """
    Extract data based on the specified requirements format.

    Args:
        source_path: The path to the requirements file.
        format: The format of the requirements file.

    Returns:
        pd.DataFrame
    """
    logger.info("Starting process")
    logger.debug(f"Retrieving: {source_path}")
    result = Requirements().render(source_path, format)
    pkgs_raw_metadata = []
    for pkg in track(result):
        if is_iac_project(pkg[0]) or is_python(pkg[0]):
            filtered_data = get_raw_data(pkg[0], pkg[1])
        else:
            filtered_data = filter_data(
                get_raw_data(pkg[0]), pkg[1] if len(pkg) > 1 else None
            )
        if filtered_data:
            pkgs_raw_metadata.append(filtered_data)
    output = pd.DataFrame(pkgs_raw_metadata)
    # output["uppercased_name"] = output["name"].str.upper()
    # output = output.sort_values(by=["uppercased_name"])
    # output = output.drop_duplicates(subset=["uppercased_name"], keep="first")
    # del output["uppercased_name"]
    output["uppercased_version_url"] = output["version_url"].str.upper()
    output = output.sort_values(by=["uppercased_version_url"])
    output = output.drop_duplicates(subset=["uppercased_version_url"], keep="first")
    del output["uppercased_version_url"]
    return output


def save_data(data: pd.DataFrame, output: Path):
    # Extract directory from the output string
    raw_name = str(output).split(".")[0]
    output_directory = os.path.dirname(output)
    only_version_url_list = data.copy()
    only_version_url_list["Commit ID"] = only_version_url_list["version_url"]
    # only_version_url_list["Version Number"] = only_version_url_list["version"]
    only_version_url_list_df = only_version_url_list[["Commit ID"]]
    # only_version_url_list_df = only_version_url_list_df.copy().pivot_table(by=["Commit ID", "Version Number"])
    logger.info(f"Storing into: {output}")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    if str(output).endswith(".csv"):
        data.to_csv(output, index=False)
        only_version_url_path = f"{raw_name}_only_version_urls.csv"
        only_version_url_list_df.to_csv(only_version_url_path, index=False)
        logger.info(f"Only urls version stored into: {only_version_url_path}")
        logger.info("All done! Have a Great day")
    elif str(output).endswith(".xlsx"):
        data.to_excel(output, index=False)
        only_version_url_path = f"{raw_name}_only_version_urls.xlsx"
        only_version_url_list_df.to_excel(only_version_url_path, index=False)
        logger.info(f"Only urls version stored into: {only_version_url_path}")
        logger.info("All done! Have a Great day")
    else:
        logger.error("Not supported format.")
