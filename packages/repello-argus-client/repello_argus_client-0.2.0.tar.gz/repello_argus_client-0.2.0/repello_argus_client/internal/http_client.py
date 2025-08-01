from typing import Any, Dict, Optional, Set

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from .. import __version__
from ..enums.core import InteractionType
from ..errors import (
    ArgusAPIError,
    ArgusAuthenticationError,
    ArgusConnectionError,
    ArgusInternalServerError,
    ArgusNotFoundError,
    ArgusPermissionError,
    ArgusValueError,
)
from ..types.core import ApiResult, Metadata, Policy

RUNTIME_SEC_BASE_URL = "https://argusapi.repello.ai/sdk/v1"
PLAYGROUND_BASE_URL = "https://hodorapi.repello.ai/sdk/v1"
DEFAULT_TIMEOUT = 30.0


def is_server_error(exception: Exception) -> bool:
    if (
        isinstance(exception, httpx.HTTPStatusError)
        and exception.response.status_code >= 500
    ):
        return True
    if isinstance(exception, ArgusInternalServerError):
        return True
    return False


class HttpClient:
    def __init__(self, api_key: str, base_url: str):
        self._api_key = api_key
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"repello-argus-python-sdk/{__version__}",
        }
        if base_url == RUNTIME_SEC_BASE_URL:
            headers["X-API-Key"] = f"{self._api_key}"
        elif base_url == PLAYGROUND_BASE_URL:
            headers["Authorization"] = f"Bearer {self._api_key}"
        elif base_url.startswith("http") or base_url.startswith("https"):
            headers["X-API-Key"] = f"{self._api_key}"
        else:
            raise ValueError("Invalid base URL provided.")

        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )

        self._access_level_cache: Optional[int] = None
        self._verified_assets_cache: Set[str] = set()

    def verify_api_key(self) -> int:
        if self._access_level_cache is not None:
            return self._access_level_cache
        try:
            response = self._client.get("/verify/api-key")
            response.raise_for_status()
            data = response.json()
            if not data.get("valid"):
                raise ArgusAuthenticationError("API key is not valid.", 401, data)
            access_level = data.get("access_level", 1)
            self._access_level_cache = access_level
            return access_level
        except httpx.HTTPStatusError as e:
            self._handle_api_error(e)
        except httpx.RequestError as e:
            raise ArgusConnectionError(
                f"Network error during API key verification: {e}"
            ) from e

    def verify_asset(self, asset_id: str):
        if asset_id in self._verified_assets_cache:
            return
        try:
            response = self._client.get("/verify/asset", params={"asset_id": asset_id})
            response.raise_for_status()
            data = response.json()
            if not data.get("valid"):
                raise ArgusValueError(
                    f"Asset ID '{asset_id}' is not valid or accessible."
                )
            self._verified_assets_cache.add(asset_id)
        except httpx.HTTPStatusError as e:
            self._handle_api_error(e)
        except httpx.RequestError as e:
            raise ArgusConnectionError(
                f"Network error during asset verification: {e}"
            ) from e

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10) + wait_random(0, 1),
        stop=stop_after_attempt(3),
        retry=(
            retry_if_exception_type(httpx.NetworkError)
            | retry_if_exception(is_server_error)
        ),
        reraise=True,
    )
    def post_scan(
        self,
        text: str,
        interaction_type: InteractionType,
        asset_id: str,
        session_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
        policy: Optional[Policy] = None,
        save: bool = False,
    ) -> ApiResult:
        endpoint, scan_data_key = self._get_scan_details(interaction_type)

        payload: Dict[str, Any] = {
            "asset_id": asset_id,
            "scan_data": {scan_data_key: text},
            "save": save,
        }
        if policy:
            payload["policies"] = policy
        if session_id:
            payload["session_id"] = session_id
        if metadata:
            payload["metadata"] = metadata

        try:
            response = self._client.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_api_error(e)
        except httpx.RequestError as e:
            raise ArgusConnectionError(
                f"Network error while communicating with Argus API: {e}"
            ) from e

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10) + wait_random(0, 1),
        stop=stop_after_attempt(3),
        retry=(
            retry_if_exception_type(httpx.NetworkError)
            | retry_if_exception(is_server_error)
        ),
        reraise=True,
    )
    def post_event(self, payload: Dict[str, Any]) -> ApiResult:
        """
        Posts a single trace event (with or without an evaluation) to the backend.
        """
        endpoint = "/events/record"
        try:
            response = self._client.post(endpoint, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self._handle_api_error(e)
        except httpx.RequestError as e:
            raise ArgusConnectionError(
                f"Network error while posting trace event to Argus API: {e}"
            ) from e

    def _get_scan_details(self, interaction_type: InteractionType) -> tuple[str, str]:
        if interaction_type == InteractionType.PROMPT:
            return "/analyze/prompt", "prompt"
        elif interaction_type == InteractionType.RESPONSE:
            return "/analyze/response", "response"
        raise ValueError(f"Invalid interaction type: {interaction_type}")

    def _handle_api_error(self, e: httpx.HTTPStatusError) -> None:
        try:
            response_body = e.response.json()
        except ValueError:
            response_body = {"error": e.response.text}
        status = e.response.status_code
        message = response_body.get("error", "An unknown API error occurred.")

        if status == 401:
            raise ArgusAuthenticationError(message, status, response_body) from e
        if status == 403:
            raise ArgusPermissionError(message, status, response_body) from e
        if status == 404:
            raise ArgusNotFoundError(message, status, response_body) from e
        if 500 <= status < 600:
            raise ArgusInternalServerError(message, status, response_body) from e

        raise ArgusAPIError(message, status, response_body) from e

    def close(self):
        self._client.close()
