from typing import Any, Dict, Optional

import httpx

from .exceptions import (
    ERROR_CODE_MAPPING,
    DifyAPIError,
    DifyAuthenticationError,
    DifyConflictError,
    DifyConnectionError,
    DifyNotFoundError,
    DifyServerError,
    DifyTimeoutError,
    DifyValidationError,
)


class BaseClient:
    """Base HTTP client for Dify API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.dify.ai",
        timeout: float = 30.0
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout)
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "dify-sdk-python/0.1.0"
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {"status": "success"}
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                error_code = error_data.get("code", "unknown")
                message = ERROR_CODE_MAPPING.get(error_code, error_data.get("message", "Bad request"))
                raise DifyValidationError(message, response.status_code, error_code)
            elif response.status_code == 401:
                raise DifyAuthenticationError("Invalid API key", response.status_code)
            elif response.status_code == 403:
                error_data = response.json() if response.content else {}
                error_code = error_data.get("code", "forbidden")
                message = ERROR_CODE_MAPPING.get(error_code, "Forbidden")
                raise DifyValidationError(message, response.status_code, error_code)
            elif response.status_code == 404:
                raise DifyNotFoundError("Resource not found", response.status_code)
            elif response.status_code == 409:
                error_data = response.json() if response.content else {}
                error_code = error_data.get("code", "conflict")
                message = ERROR_CODE_MAPPING.get(error_code, "Conflict")
                raise DifyConflictError(message, response.status_code, error_code)
            elif response.status_code == 413:
                raise DifyValidationError("File too large", response.status_code, "file_too_large")
            elif response.status_code == 415:
                raise DifyValidationError("Unsupported file type", response.status_code, "unsupported_file_type")
            elif response.status_code >= 500:
                raise DifyServerError("Server error", response.status_code)
            else:
                raise DifyAPIError(f"Unexpected status code: {response.status_code}", response.status_code)
        except httpx.HTTPError as e:
            raise DifyConnectionError(f"Connection error: {str(e)}") from e

    def _request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make HTTP request."""
        url = f"{self.base_url}{path}"

        try:
            kwargs = {
                "method": method,
                "url": url,
                "params": params
            }

            if files:
                kwargs["files"] = files
                if data:
                    kwargs["data"] = data
                # Remove Content-Type header for multipart requests
                headers = self._get_headers()
                headers.pop("Content-Type", None)
                kwargs["headers"] = headers
            else:
                kwargs["json"] = json
                kwargs["headers"] = self._get_headers()

            response = self._client.request(**kwargs)
            return self._handle_response(response)

        except httpx.TimeoutException as e:
            raise DifyTimeoutError("Request timeout") from e
        except httpx.ConnectError as e:
            raise DifyConnectionError("Failed to connect to Dify API") from e
        except httpx.HTTPError as e:
            raise DifyConnectionError(f"HTTP error: {str(e)}") from e

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make GET request."""
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Make POST request."""
        return self._request("POST", path, json=json, files=files, data=data)

    def patch(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        """Make PATCH request."""
        return self._request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:
        """Make DELETE request."""
        return self._request("DELETE", path)

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
