import logging
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import jwt
import requests

logger = logging.getLogger(__name__)


class GuardianClientInvalidConfigException(Exception):
    """
    Raised when required environment variables for the client are missing.
    """


class InvalidAuthTokenException(Exception):
    """
    Raised when we fail to obtain an access token from the auth provider
    """


class GuardianClientCredentialContext:
    def __init__(
        self,
        guardian_endpoint: str,
        client_id: str = "",
        client_secret: str = "",
        log_level: str = "INFO",
    ) -> None:
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

        # Guardian endpoint should be suffixed with /guardian
        clean_endpoint = guardian_endpoint.rstrip("/")
        clean_endpoint = (
            clean_endpoint
            if clean_endpoint.endswith("/guardian")
            else f"{clean_endpoint}/guardian"
        )
        logger.debug(
            f"Initializing guardian client credential context for endpoint: {clean_endpoint}"
        )

        self._token_endpoint = f"{clean_endpoint}/v2/auth/client_auth/token"

        # authentication credentials
        api_client_id_env = os.getenv("GUARDIAN_API_CLIENT_ID")
        scanner_client_id_env = os.getenv("GUARDIAN_SCANNER_CLIENT_ID")
        if scanner_client_id_env and not api_client_id_env:
            logger.warning(
                "GUARDIAN_SCANNER_CLIENT_ID is deprecated, please use GUARDIAN_API_CLIENT_ID instead"
            )
        self._client_id = client_id or api_client_id_env or scanner_client_id_env

        api_client_secret_env = os.getenv("GUARDIAN_API_CLIENT_SECRET")
        scanner_client_secret_env = os.getenv("GUARDIAN_SCANNER_CLIENT_SECRET")
        if scanner_client_secret_env and not api_client_secret_env:
            logger.warning(
                "GUARDIAN_SCANNER_CLIENT_SECRET is deprecated, please use GUARDIAN_API_CLIENT_SECRET instead"
            )
        self._client_secret = (
            client_secret or api_client_secret_env or scanner_client_secret_env
        )
        for val, name in [
            (self._client_id, "GUARDIAN_API_CLIENT_ID"),
            (self._client_secret, "GUARDIAN_API_CLIENT_SECRET"),
        ]:
            if not val:
                logger.error(f"Failed to read {name} from the environment")
                raise GuardianClientInvalidConfigException(
                    f"Failed to read {name} from the environment"
                )

        self._access_token: Optional[str] = None
        logger.info("New guardian-client credential context initialized")

    @property
    def access_token(self) -> str:
        if not self._access_token or self._is_credential_expired():
            # request for a fresh token and return when done.
            logger.info(
                f"Existing access token is {'not present' if not self._access_token else 'expired'}; fetching a new token from token endpoint"
            )
            self._access_token = self._load_access_token()

        return self._access_token

    def _load_access_token(self) -> str:
        # SDK is authenticated using the Client Credential flow
        access_token = self._request_access_token(
            token_url=str(self._token_endpoint),
            client_id=str(self._client_id),
            client_secret=str(self._client_secret),
        )

        if access_token is None:
            logger.critical(
                """
                Failed to obtain an access token. Check the logs for more information.
                Make sure env variables are properly set.
                """
            )
            raise InvalidAuthTokenException("Failed to obtain an access token")

        logger.debug("Obtained a valid access token from auth provider")

        return access_token

    def _is_credential_expired(self) -> bool:
        if not self._access_token:
            raise InvalidAuthTokenException("Access token is not valid")

        token_exp = self._get_token_expiration_timestamp(self._access_token)

        expiration_datetime = datetime.fromtimestamp(token_exp, tz=timezone.utc)

        # Add a random jitter to space out the token refreshes
        jitter = random.randint(10, 30)
        return datetime.now(timezone.utc) > expiration_datetime - timedelta(
            seconds=jitter
        )

    def _get_token_expiration_timestamp(self, token: str) -> float:
        try:
            decoded_token = jwt.decode(token, options={"verify_signature": False})

            exp = decoded_token.get("exp")
            if exp is None:
                raise InvalidAuthTokenException("Access token missing expiration")
            return float(exp)
        except jwt.DecodeError as e:
            logger.critical("Failed to decode JWT access token", exc_info=e)
            raise InvalidAuthTokenException("Access token is not valid")

    def _request_access_token(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
    ) -> Optional[str]:
        """
        Retrieves a JWT access token using client credentials flow.

        Arguments:
            token_url: The URL of the /token endpoint on the API we're calling
            client_id: The client ID
            client_secret: The client secret
        """
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
        }

        access_token: Optional[str] = None
        response = None
        try:
            logger.debug(f"Requesting access token from token endpoint {token_url}")
            response = requests.post(
                token_url,
                json=payload,
                timeout=2,
            )

            if response and response.status_code:
                logger.debug(f"Got {response.status_code} response from token endpoint")
            response.raise_for_status()
            response_json = response.json()

            # Check if the response is a valid JSON object, otherwise throw an error
            # String responses (and possibly others) do NOT raise JSONDecodeError, so we have to check the type
            if isinstance(response_json, dict):
                logger.debug("Got JSON response from token endpoint")
                access_token = response_json.get("access_token")
            else:
                logger.error(
                    "Got non-JSON response from token endpoint: %s", response.content
                )
        except requests.ConnectionError:
            logger.exception(
                f"Failed to connect to the token endpoint {token_url}, is the Guardian API available?"
            )
        except requests.HTTPError:
            status_code: Union[str, int] = "Unknown"
            if response is not None and response.status_code:
                status_code = response.status_code
            logger.exception(f"{status_code} HTTP error while retrieving access token")
        except requests.JSONDecodeError:
            if response and response.content:
                logger.error("Got non-JSON response: %s", response.content)
            else:
                logger.error("Got empty response from the token endpoint")
            logger.exception("Failed to decode JSON response from the token endpoint")
        except Exception:
            logger.exception("Unexpected error while retrieving access token")

        if access_token and type(access_token) is str:
            return access_token
        else:
            raise InvalidAuthTokenException(
                "Access token requests failed; check Guardian client logs for details"
            )
