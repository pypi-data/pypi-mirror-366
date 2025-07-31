import json
import logging
import os
import re
import time
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import pkg_resources
import requests
from huggingface_hub import hf_hub_download, repo_info  # type: ignore[import-untyped]
from requests import Response


def get_version() -> str:
    """
    Returns the version of the guardian-client package.
    """
    try:
        version = pkg_resources.get_distribution("guardian-client").version
    except Exception:
        # Fallback for development scenarios where package is not installed
        version = "0.0.0-dev"

    return version


GUARDIAN_CLIENT_SDK_VERSION = get_version()

from guardian_client.python.credentials import GuardianClientCredentialContext
from guardian_client.python.worker_pool_client import WorkerPoolClient


class GuardianAPIClient:
    """
    Client for Guardian API
    """

    def __init__(
        self,
        base_url: str,
        scan_endpoint: str = "scans",
        api_version: str = "v2",
        log_level: str = "INFO",
    ) -> None:
        """
        Initializes the Guardian API client.
        Args:
            base_url (str): The base URL of the Guardian API.
            scan_endpoint (str, optional): The endpoint for scanning. Defaults to "scans".
            api_version (str, optional): The API version. Defaults to "v2".
            log_level (str, optional): The log level. Defaults to "INFO".
        Raises:
            ValueError: If the log level is not one of "DEBUG", "INFO", "ERROR", or "CRITICAL".
        """
        clean_endpoint = base_url.rstrip("/")
        clean_endpoint = (
            clean_endpoint
            if clean_endpoint.endswith("/guardian")
            else f"{clean_endpoint}/guardian"
        )
        self.scans_endpoint = f"{clean_endpoint}/{api_version}/{scan_endpoint}"
        self.model_versions_endpoint = f"{clean_endpoint}/{api_version}/models/versions"
        log_string_to_level = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        log_level_enum = log_string_to_level.get(log_level.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level_enum,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        logging.info(f"Initialized scanning endpoint: {self.scans_endpoint}")

        # client credential context is tied to a client instance.
        # In it's current state, a new client instance is created on each new call
        # to the guardian scanner, so a new context (and consequently a token)
        # is created for each scan request.
        self._access_token_context = GuardianClientCredentialContext(
            guardian_endpoint=base_url, log_level=log_level
        )

        # Initialize worker pool client lazily
        self._worker_pools: Optional[WorkerPoolClient] = None
        self._base_url = base_url

    @property
    def worker_pools(self) -> WorkerPoolClient:
        """
        Access to Worker Pool management operations.

        Returns:
            WorkerPoolClient: Client for worker pool operations
        """
        if self._worker_pools is None:
            self._worker_pools = WorkerPoolClient(
                self._base_url, self._access_token_context
            )
        return self._worker_pools

    def scan(
        self,
        model_uri: str,
        security_group_uuid: str,
        model_name: Optional[str] = None,
        model_author: Optional[str] = None,
        model_version: Optional[str] = None,
        allow_patterns: Optional[list[str]] = None,
        ignore_patterns: Optional[list[str]] = None,
        poll_interval_secs: int = 5,
    ) -> Dict[str, Any]:
        """
        Submits a scan request for the given URI and polls for the scan status until it is completed.

        Args:
            model_uri (str): The URI to be scanned.
            security_group_uuid (str): The UUID of the security group to evaluate the scan with.
            model_name (str): Name of the model. Defaults to the value of model_uri if the model_uri is determined to not be a HuggingFace URI, otherwise the parameter should not be provided.
            model_author (str): Author of the model. Defaults to "Unknown" if the model_uri is determined to not be a HuggingFace URI, otherwise the parameter should not be provided.
            model_version (str): Version of the model. If the model_uri is a HuggingFace URI, it should be a git SHA or branch-reference name, and defaults to the latest revision from HuggingFace. Otherwise, it defaults to "v1".
            allow_patterns: (list[str]): List of patterns to allow files that match those patterns. Defaults to allowing all files if the model_uri is determined to be a HuggingFace URI, otherwise the parameter should not be provided.
            ignore_patterns: (list[str]): List of patterns to ignore files that match those patterns. Defaults to ignoring no files if the model_uri is determined to be a HuggingFace URI, otherwise the parameter should not be provided.
            poll_interval_secs (int, optional): The interval in seconds to poll for the scan status.
                If <= 0, the function returns immediately after submitting the scan. Defaults to 5.

        Returns:
            dict: A dictionary containing the HTTP status code and the scan status JSON.
                  If an error occurs during the scan submission or polling, the dictionary
                  will also contain the error details.
        """
        if not model_uri:
            logging.error("Model URI is required")
            return {
                "http_status_code": None,
                "error": "Model URI is required",
            }

        if not security_group_uuid:
            logging.error("Security Group UUID is required")
            return {
                "http_status_code": None,
                "error": "Security Group UUID is required",
            }

        if self._is_huggingface_uri(model_uri):
            allow_patterns = ["*"] if allow_patterns is None else allow_patterns
            ignore_patterns = [] if ignore_patterns is None else ignore_patterns
            scan_origin = "HUGGING_FACE"
            model_version, error = self._get_huggingface_model_version(
                model_uri, model_version
            )

            if error:
                return error
        else:
            if allow_patterns is not None or ignore_patterns is not None:
                logging.warning(
                    "allow_patterns and ignore_patterns were provided, but are not supported for non-HuggingFace model URIs. "
                    "Ignoring these parameters."
                )
                allow_patterns = None
                ignore_patterns = None
            model_name = model_uri if model_name is None else model_name
            model_author = "Unknown" if model_author is None else model_author
            model_version = "v1" if model_version is None else model_version
            scan_origin = "PRIVATE_WORKER"

        logging.info(
            f"Submitting scan for model {model_uri} and security group {security_group_uuid}"
        )

        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }
        payload = {
            "model_uri": model_uri,
            "security_group_uuid": security_group_uuid,
            "scan_origin": scan_origin,
            "model_name": model_name,
            "model_author": model_author,
            "model_version": model_version,
            "allow_patterns": allow_patterns,
            "ignore_patterns": ignore_patterns,
        }
        filtered_payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(
            self.scans_endpoint,
            json=filtered_payload,
            headers=headers,
        )
        if response.status_code != HTTPStatus.CREATED:
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        logging.info(
            f"Scan submitted successfully for {model_uri} with status_code: {response.status_code}"
        )

        if poll_interval_secs <= 0:
            return {
                "http_status_code": response.status_code,
                "scan_status_json": response.json(),
            }

        response_json = response.json()
        id = response_json["uuid"]

        # Polling
        scan_status_json = None
        status_response = None

        logging.info(f"Polling for scan outcome for {id} for {model_uri}")
        while True:
            # reload header to check if token is still valid during this processing.
            headers = {
                "Authorization": f"Bearer {self._access_token_context.access_token}",
                "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
            }

            status_response = requests.get(
                url=f"{self.scans_endpoint}/{id}",
                headers=headers,
            )
            if status_response.status_code == HTTPStatus.OK:
                scan_status_json = status_response.json()
                if scan_status_json["aggregate_eval_outcome"] != "PENDING":
                    break
            else:
                return {
                    "http_status_code": status_response.status_code,
                    "error": self._decode_error(status_response),
                }

            logging.debug(
                f"Scan outcome for {id} is {scan_status_json['aggregate_eval_outcome']}. Sleeping for 5 seconds before next check"
            )
            time.sleep(poll_interval_secs)  # Wait for 5 seconds before next check

        logging.info(f"Scan complete for {id} for {model_uri}")

        return {
            "http_status_code": (
                status_response.status_code if status_response else None
            ),
            "scan_status_json": scan_status_json,
        }

    def get_scan(self, scan_uuid: str) -> Dict[str, Any]:
        """
        Retrieves the scan results for a given past scan.

        Args:
            scan_uuid (str): The ID of the scan to retrieve.

        Returns:
            dict: A dictionary containing the HTTP status code and the scan status JSON.
                  If an error occurred during the scan, the dictionary
                  will contain the error details instead of the scan status.
        """
        if not scan_uuid:
            logging.error("Scan UUID is required")
            return {
                "http_status_code": None,
                "error": "Scan UUID is required",
            }

        logging.info(f"Retrieving scan ID {scan_uuid}")

        # reload header to check if token is still valid during this processing.
        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }

        status_response = requests.get(
            url=f"{self.scans_endpoint}/{scan_uuid}",
            headers=headers,
        )
        if status_response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": status_response.status_code,
                "error": self._decode_error(status_response),
            }

        scan_status_json = status_response.json()
        return {
            "http_status_code": (
                status_response.status_code if status_response else None
            ),
            "scan_status_json": scan_status_json,
        }

    def list_scans(
        self,
        limit: int = 10,
        skip: int = 0,
        count: bool = True,
        sort_field: str = "created_at",
        sort_order: str = "desc",
        severities: Optional[List[str]] = None,
        outcome: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Lists scans with optional filters.

        Args:
            limit (int): Maximum number of scans to retrieve. Defaults to 10.
            skip (int): Number of scans to skip. Defaults to 0.
            count (bool): Whether to return a count of scans. Defaults to True.
            sort_field (str): Field to sort the scans by. Choices are "created_at" or "updated_at". Defaults to "created_at".
            sort_order (str): Order of sorting: "asc" or "desc". Defaults to "desc".
            severities (list[str], optional): Severities to filter by. Choices are "LOW", "MEDIUM", "HIGH", or "CRITICAL".
            outcome (str, optional): Outcome filter for scans. Choices are "PASS", "FAIL", or "ERROR".
            start_time (datetime, optional): Start time filter in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
            end_time (datetime, optional): End time filter in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

        Returns:
            dict: A dictionary containing the HTTP status code and the scan list JSON.
                  If an error occurred during the request, the dictionary
                  will contain the error details instead of the scan list.
        """
        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }

        params: Dict[str, str] = {
            "limit": str(limit),
            "skip": str(skip),
            "sort_field": sort_field,
            "sort_order": sort_order,
            "count": str(count).lower(),
        }

        # Dynamically add optional params only if they are provided
        if severities:
            params["severities"] = ",".join(severities)

        if outcome:
            params["outcome"] = outcome

        if start_time:
            params["start_time"] = start_time.isoformat()

        if end_time:
            params["end_time"] = end_time.isoformat()

        status_response = requests.get(
            url=self.scans_endpoint,
            headers=headers,
            params=params,
        )

        if status_response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": status_response.status_code,
                "error": self._decode_error(status_response),
            }

        scan_list_json = status_response.json()
        return {
            "http_status_code": status_response.status_code,
            "scan_list": scan_list_json,
        }

    def scan_3p(
        self,
        repo_id: str,
        revision: str = "",
        allow_patterns: list[str] = ["*"],
        ignore_patterns: list[str] = [],
    ) -> Dict[str, Any]:
        logging.error(f"scan_3p() is deprecated. Please use scan() instead.")
        return {
            "http_status_code": None,
            "error": "scan_3p() is deprecated. Please use scan() instead.",
        }

    def download_from_scan(self, scan_uuid: str, local_dir: str) -> Dict[str, Any]:
        logging.info(f"Downloading file(s) from scan ID {scan_uuid} to {local_dir}")
        scan_response = self.get_scan(scan_uuid)
        if scan_response["http_status_code"] != HTTPStatus.OK:
            return scan_response

        scan_status_json = scan_response["scan_status_json"]
        aggregate_eval_outcome = scan_status_json["aggregate_eval_outcome"]

        file_download_locs = []

        if aggregate_eval_outcome == "ERROR":
            logging.error(
                f"Model is blocked because scan id {scan_uuid} encountered an unexpected error"
            )
            return {
                "http_status_code": HTTPStatus.FORBIDDEN,
                "scan_status_json": scan_status_json,
                "download_locations": [],
            }
        elif aggregate_eval_outcome == "FAIL":
            logging.error(
                f"Model is blocked because scan id {scan_uuid} violated your organization's security policies"
            )
            return {
                "http_status_code": HTTPStatus.FORBIDDEN,
                "scan_status_json": scan_status_json,
                "download_locations": [],
            }

        model_uri = scan_status_json["model_uri"]
        repo_id, error = self._get_huggingface_repo_id(model_uri)

        if error:
            return error

        files_response = self._get_files_for_scan(scan_uuid)
        if files_response["http_status_code"] != HTTPStatus.OK:
            return files_response

        files = files_response["files"]
        if not files:
            return {
                "http_status_code": HTTPStatus.NOT_FOUND,
                "error": f"No files found for scan {scan_uuid}",
            }

        model_version_uuid = scan_status_json["model_version_uuid"]
        model_version_response = self._get_model_version(model_version_uuid)
        if model_version_response["http_status_code"] != HTTPStatus.OK:
            return model_version_response
        revision = model_version_response["model_version"]["revision"]

        for file_ in files_response["files"]:
            download_loc = hf_hub_download(
                repo_id=repo_id,
                revision=revision,
                local_dir=local_dir,
                filename=os.path.basename(file_.get("path")),
                subfolder=os.path.dirname(file_.get("path")),
                # Custom-header indicating a completed scan to use during download.
                headers={"guardian-scan-uuid": scan_uuid},
                token=os.environ.get("HF_TOKEN"),
            )
            file_download_locs.append(download_loc)

        return {
            "http_status_code": HTTPStatus.OK,
            "scan_status_json": scan_status_json,
            "download_locations": file_download_locs,
        }

    def _get_files_for_scan(self, scan_uuid: str) -> Dict[str, Any]:
        skip = 0
        all_files: List[Any] = []

        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }
        while True:
            response = requests.get(
                url=f"{self.scans_endpoint}/{scan_uuid}/files",
                headers=headers,
                params={"skip": skip},
            )

            if response.status_code != HTTPStatus.OK:
                return {
                    "http_status_code": response.status_code,
                    "error": self._decode_error(response),
                }

            response_json = response.json()
            files = response_json.get("files", [])
            if not files:
                break

            all_files.extend(files)
            skip += len(files)

            if len(all_files) >= response_json["pagination"]["total_items"]:
                break

        return {"files": all_files, "http_status_code": HTTPStatus.OK}

    def _get_model_version(self, model_version_uuid: str) -> Dict[str, Any]:
        logging.debug(f"Retrieving model version for {model_version_uuid}")

        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }

        response = requests.get(
            url=f"{self.model_versions_endpoint}/{model_version_uuid}",
            headers=headers,
        )
        if response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        model_version_json = response.json()
        return {
            "http_status_code": response.status_code,
            "model_version": model_version_json,
        }

    def _decode_error(self, response: Response) -> str:
        try:
            response_json = response.json()
            if "detail" in response_json and response_json["detail"]:
                if isinstance(response_json["detail"], list):
                    concat_msg = ""
                    for item_ in response_json["detail"]:
                        concat_msg += f"- {item_['msg']}\n"
                    return concat_msg
                elif isinstance(response_json["detail"], str):
                    return response_json["detail"]

            return "Unknown error"
        except json.JSONDecodeError:
            return "Response is not in JSON format"

    def _is_git_sha(self, in_str: str) -> bool:
        # Git SHAs are 40 characters long (full) or 7-8 characters (short)
        # They only contain hexadecimal characters (0-9, a-f)

        # For both full and short SHA
        pattern_with_short = r"^[0-9a-f]{7,40}$"

        return bool(re.match(pattern_with_short, in_str.lower()))

    def _is_huggingface_uri(self, model_uri: str) -> bool:
        parsed_uri = urlparse(model_uri)
        return parsed_uri.scheme == "https" and parsed_uri.hostname == "huggingface.co"

    def _get_huggingface_repo_id(
        self, model_uri: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        path_parts = urlparse(model_uri).path.split("/")

        if len(path_parts) != 3:
            return None, {
                "http_status_code": HTTPStatus.BAD_REQUEST,
                "error": f"Error: Model URI '{model_uri}' does not follow expected HuggingFace URI format of https://huggingface.co/<model_author>/<model_name>",
            }
        return f"{path_parts[1]}/{path_parts[2]}", None

    def _get_huggingface_model_version(
        self, model_uri: str, model_version: Optional[str]
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        repo_id, error = self._get_huggingface_repo_id(model_uri)

        if error:
            return (None, error)

        if not model_version:
            logging.debug(
                f"Revision not provided. Fetching latest revision for {repo_id} from Hugging Face"
            )
            latest_revision = repo_info(repo_id)
            if not latest_revision:
                logging.error(
                    f"Error: Could not fetch latest revision for {repo_id} from Hugging Face"
                )
                return (
                    None,
                    {
                        "http_status_code": HTTPStatus.BAD_REQUEST,
                        "error": f"Error: Could not fetch latest revision for {repo_id} from Hugging Face",
                    },
                )
            model_version = latest_revision.sha
            logging.debug(
                f"Fetched latest revision from Hugging Face: {repo_id}/{model_version}"
            )

        elif not self._is_git_sha(model_version):
            logging.debug(
                f"Given revision {model_version} is not a SHA. Fetching a valid sha for revision"
            )
            revision_check = repo_info(repo_id=repo_id, revision=model_version)
            if not revision_check:
                logging.error(
                    f"Error: Could not find the revision {model_version} for {repo_id} from Hugging Face"
                )
                return (
                    None,
                    {
                        "http_status_code": HTTPStatus.BAD_REQUEST,
                        "error": f"Error: Could not find the revision {model_version} for {repo_id} from Hugging Face",
                    },
                )
            model_version = revision_check.sha

        return (model_version, None)
