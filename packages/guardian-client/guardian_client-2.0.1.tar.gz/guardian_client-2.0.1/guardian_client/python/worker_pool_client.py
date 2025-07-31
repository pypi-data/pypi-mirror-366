import logging
from http import HTTPStatus
from typing import Any, Dict, Optional

import pkg_resources
import requests

from .credentials import GuardianClientCredentialContext
from .worker_pool_models import (
    WorkerPoolListResponse,
    WorkerPoolResponse,
    WorkerPoolStatus,
    WorkerPoolUpdateRequest,
)

try:
    GUARDIAN_CLIENT_SDK_VERSION = pkg_resources.get_distribution(
        "guardian-client"
    ).version
except Exception:
    # Fallback for development scenarios where package is not installed
    GUARDIAN_CLIENT_SDK_VERSION = "0.0.0-dev"


class WorkerPoolClient:
    """
    Client for Guardian Worker Pool API operations.
    """

    def __init__(
        self, base_url: str, access_token_context: GuardianClientCredentialContext
    ):
        """
        Initialize the Worker Pool client.

        Args:
            base_url: The base URL of the Guardian API
            access_token_context: Shared credential context for authentication
        """
        clean_endpoint = base_url.rstrip("/")
        # Ensure the API endpoint includes the '/guardian' prefix as required by the Guardian API
        clean_endpoint = (
            clean_endpoint
            if clean_endpoint.endswith("/guardian")
            else f"{clean_endpoint}/guardian"
        )
        self.endpoint = f"{clean_endpoint}/v2/worker-pools/"
        self._access_token_context = access_token_context

    def _build_headers(self, include_content_type: bool = False) -> Dict[str, str]:
        """
        Build common HTTP headers for API requests.

        Args:
            include_content_type: Whether to include Content-Type header for JSON requests

        Returns:
            dict: HTTP headers for the request
        """
        headers = {
            "Authorization": f"Bearer {self._access_token_context.access_token}",
            "User-Agent": f"guardian-sdk/{GUARDIAN_CLIENT_SDK_VERSION}",
        }
        if include_content_type:
            headers["Content-Type"] = "application/json"
        return headers

    def list(self) -> Dict[str, Any]:
        """
        List all worker pools.

        Returns:
            dict: A dictionary containing the HTTP status code and worker pool list data.
                  If an error occurs, the dictionary will contain error details.
        """

        headers = self._build_headers()

        response = requests.get(self.endpoint, headers=headers)

        if response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        try:
            response_data = response.json()
            # Validate response structure using Pydantic
            worker_pool_list = WorkerPoolListResponse.model_validate(response_data)

            return {
                "http_status_code": response.status_code,
                "worker_pools": worker_pool_list.model_dump(mode="json"),
            }
        except Exception as e:
            logging.error(f"Failed to parse worker pool list response: {e}")
            return {
                "http_status_code": response.status_code,
                "error": f"Failed to parse response: {str(e)}",
            }

    def get(self, pool_id: str) -> Dict[str, Any]:
        """
        Get details for a specific worker pool.

        Args:
            pool_id: The Keycloak client ID of the worker pool

        Returns:
            dict: A dictionary containing the HTTP status code and worker pool data.
                  If an error occurs, the dictionary will contain error details.
        """
        if not pool_id:
            logging.error("Pool ID is required")
            return {
                "http_status_code": 400,
                "error": "Pool ID is required",
            }

        headers = self._build_headers()

        response = requests.get(f"{self.endpoint}{pool_id}", headers=headers)

        if response.status_code != HTTPStatus.OK:
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        try:
            response_data = response.json()
            # Validate response structure using Pydantic
            worker_pool = WorkerPoolResponse.model_validate(response_data)

            return {
                "http_status_code": response.status_code,
                "worker_pool": worker_pool.model_dump(mode="json"),
            }
        except Exception as e:
            logging.error(f"Failed to parse worker pool response: {e}")
            return {
                "http_status_code": response.status_code,
                "error": f"Failed to parse response: {str(e)}",
            }

    def update(
        self,
        pool_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[WorkerPoolStatus] = None,
    ) -> Dict[str, Any]:
        """
        Update a worker pool's metadata or status.

        Args:
            pool_id: The Keycloak client ID of the worker pool
            name: Optional new name for the worker pool
            description: Optional new description for the worker pool
            status: Optional new status for the worker pool

        Returns:
            dict: A dictionary containing the HTTP status code and updated worker pool data.
                  If an error occurs, the dictionary will contain error details.
        """
        if not pool_id:
            logging.error("Pool ID is required")
            return {
                "http_status_code": 400,
                "error": "Pool ID is required",
            }

        if status is not None and not isinstance(status, WorkerPoolStatus):
            logging.error("Status must be a WorkerPoolStatus enum")
            return {
                "http_status_code": 400,
                "error": "Status must be a WorkerPoolStatus enum",
            }

        if not any([name, description, status]):
            logging.error(
                "At least one field (name, description, or status) must be provided"
            )
            return {
                "http_status_code": 400,
                "error": "At least one field (name, description, or status) must be provided",
            }

        headers = self._build_headers(include_content_type=True)

        # Create and validate request payload
        request_data = WorkerPoolUpdateRequest(
            name=name, description=description, status=status
        )

        response = requests.patch(
            f"{self.endpoint}{pool_id}",
            json=request_data.model_dump(exclude_none=True),
            headers=headers,
        )

        if response.status_code not in [HTTPStatus.OK, HTTPStatus.NO_CONTENT]:
            return {
                "http_status_code": response.status_code,
                "error": self._decode_error(response),
            }

        # Handle cases where API might return 204 No Content vs 200 with data
        if response.status_code == HTTPStatus.NO_CONTENT:
            return {
                "http_status_code": response.status_code,
                "message": f"Worker pool {pool_id} updated successfully",
            }

        try:
            response_data = response.json()
            # Validate response structure using Pydantic
            worker_pool = WorkerPoolResponse.model_validate(response_data)

            return {
                "http_status_code": response.status_code,
                "worker_pool": worker_pool.model_dump(mode="json"),
            }
        except Exception as e:
            logging.error(f"Failed to parse worker pool update response: {e}")
            return {
                "http_status_code": response.status_code,
                "error": f"Failed to parse response: {str(e)}",
            }

    def _decode_error(self, response) -> str:
        """
        Decode error from HTTP response.

        Args:
            response: The HTTP response object

        Returns:
            str: Decoded error message
        """
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
        except Exception:
            return "Response is not in JSON format"

    def update_status(self, pool_id: str, status: WorkerPoolStatus) -> Dict[str, Any]:
        """
        Update the status of a worker pool (backward compatibility method).

        Args:
            pool_id: The Keycloak client ID of the worker pool
            status: The new status for the worker pool

        Returns:
            dict: A dictionary containing the HTTP status code and updated worker pool data.
                  If an error occurs, the dictionary will contain error details.
        """
        return self.update(pool_id=pool_id, status=status)
