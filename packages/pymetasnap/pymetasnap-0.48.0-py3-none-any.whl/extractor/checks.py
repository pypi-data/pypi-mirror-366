import re
from typing import Dict

import requests

from extractor.logger import logger


class StandardCheck:
    def __init__(self):
        self.project_default_error = "No project url found, please check manually"
        self.version_default_error = "No version url found, please check manually"

    def gh_pattern(self, pattern: str, url: str, custom_error: str = None):
        try:
            found = re.search(pattern, url)
        except Exception as e:
            logger.warning(custom_error) if custom_error else logger.warning(e)
        else:
            return found

    def additional_urls(self, pattern: str, project_urls: str):
        urls = project_urls.items()
        possible_keys = [
            "Code",
            "Source Code",
            "Source code",
            "Source",
            "Homepage",
            "Home",
            "Repository",
            "repository",
            "Download",
            "download",
        ]
        for title, url in urls:
            if _ := self.gh_pattern(pattern, url) and title in possible_keys:
                return url

    def licenses(self, raw_data: Dict) -> str:
        licenses = raw_data["license"]
        if licenses != "" and licenses is not None:
            return licenses
        licenses_pattern = r"^[lL]icense.*"

        for lic in raw_data["classifiers"]:
            if license_found := re.search(licenses_pattern, lic):
                return license_found.group()

    def project_url(self, pattern: str, project_url: str, project_urls: Dict) -> str:
        if project_url != "" and self.gh_pattern(pattern, project_url):
            return project_url

        if project_urls:
            logger.debug("Nested metadata found")
            return self.additional_urls(pattern, project_urls)

    def _url_exists(self, url) -> bool:
        response = requests.get(url)
        return response.status_code != 404

    def _version_handler(self, filtered_data: Dict, version: str):
        exceptions = {
            "pandas": f"v{version}",
            "azure-keyvault-secrets": f"azure-keyvault-secrets_{version}",
            "azure-storage-blob": f"azure-storage-blob_{version}",
            "pyspark": f"pyspark_v{version}",
            "loguru": f"{filtered_data['project_url'].rsplit('/', 1)[0].replace('archive','')}tree/{version}/",
        }

        version = exceptions.get(filtered_data["name"], version)

        if version and version.startswith("azure"):
            return f"{filtered_data['project_url'].replace('main',version)}"

        if version and version.startswith("pyspark"):
            return f"{filtered_data['project_url'].replace('master',version).replace('pyspark_','')}"

        if "loguru" in version:
            return version

        default_url = f"{filtered_data['project_url']}/tree/{version}/"

        return (
            default_url
            if self._url_exists(default_url)
            else f"{filtered_data['project_url']}/tree/v{version}/"
        )

    def version(self, version: str, pattern: str, filtered_data: Dict) -> Dict:
        if version and self.gh_pattern(
            pattern, filtered_data.get("project_url"), self.project_default_error
        ):
            project_url = self._version_handler(filtered_data, version)
            if _ := self._url_exists(project_url):
                filtered_data["version_url"] = self._version_handler(
                    filtered_data, version
                )
            else:
                filtered_data["version_url"] = self.version_default_error
        else:
            filtered_data["version_url"] = self.version_default_error
        return filtered_data
