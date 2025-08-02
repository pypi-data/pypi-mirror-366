from typing import Dict, Any, List, Generator
from enum import Enum
import json

from requests import Response, Session

from .tools import join_urls


class ExecStatus(Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"


class LiRAYSApiClient:

    def __init__(
        self,
        base_url: str = "https://api.lirays.com",
        version: str = "v1",
    ):
        self.base_url = base_url.rstrip("/")
        self.session = Session()
        self.version = version
        self.access_token = None
        self.refresh_token = None
        self.email = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def _make_request(
        self,
        base: str,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Response:
        url = join_urls(base, endpoint)
        headers = kwargs.get("headers", {})
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        kwargs["headers"] = headers

        response = self.session.request(method, url, **kwargs)

        if response.status_code == 401:
            if self.refresh_token():
                response = self.session.request(method, url, **kwargs)
            else:
                raise Exception("Failed to refresh token")

        return response

    def _make_vrequest(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> Response:
        return self._make_request(
            join_urls(self.base_url, f"/api/{self.version}"),
            method,
            endpoint,
            **kwargs,
        )

    def close(self):
        """Close the session and clean up resources."""
        if self.session:
            self.session.close()
            self.session = None
            self.access_token = None
            self.refresh_token = None
            self.email = None

    def reset(self, base_url: str = None, version: str = None):
        if base_url:
            self.base_url = base_url.rstrip("/")
        if version:
            self.version = version
        self.close()
        self.session = Session()

    # Auth
    def login(self, email: str, password: str) -> bool:
        body = {
            "email": email,
            "password": password,
        }
        response = self._make_vrequest("POST", "/auth/login", json=body)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["session"]["access_token"]
            self.refresh_token = data["session"]["refresh_token"]
            self.email = data["user"]["email"]
            return True
        return False

    def logout(self):
        self.reset()

    def refresh_token(self) -> bool:
        if self.refresh_token:
            body = {"refresh_token": self.refresh_token}
            response = self._make_vrequest("POST", "/auth/refresh", json=body)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["session"]["access_token"]
                self.refresh_token = data["session"]["refresh_token"]
                self.email = data["user"]["email"]
                return True
        return False

    # Default
    def health_check(self) -> bool:
        try:
            response = self._make_request(f"{self.base_url}", "GET", "/")
            print(response.text)
            return response.status_code == 200 and response.text == "OK"
        except Exception:
            return False

    # Base
    def get_layer_classes(self) -> List[str]:
        response = self._make_vrequest("GET", "/base/layers")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get layer classes: {response.status_code} {response.text}"
            )

    def get_ready_layer_classes(self) -> List[str]:
        response = self._make_vrequest("GET", "/base/readyLayers")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get ready layer classes: {response.status_code} {response.text}"
            )

    def get_available_actions(self) -> List[str]:
        response = self._make_vrequest("GET", "/base/availableActions")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get available actions: {response.status_code} {response.text}"
            )

    # Tools Execution
    def get_tool_required_payload(self, action: str) -> Dict[str, Any]:
        response = self._make_vrequest("GET", f"/tool/required_payload/{action}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get tool required payload: {response.status_code} {response.text}"
            )

    def execute_action(
        self,
        action: str,
        config: Dict[str, Any],
        input_: Dict[str, Any],
    ) -> Generator[dict, None, None]:
        request_data = {
            "action": action,
            "config": config,
            "input": input_,
        }

        response = self._make_vrequest(
            "POST",
            "/tool/execute",
            json=request_data,
            stream=True,
            headers={"Accept": "application/json"},
        )

        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    yield data
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    # Handle malformed response lines
                    yield {
                        "status": "failed",
                        "progress": 0,
                        "partial_result": {
                            "error": f"Failed to parse response: {str(e)}"
                        },
                    }
                    break
