from typing import Dict, Any, List, Generator, Optional, Union
from enum import Enum
import json

from requests import Response, Session

from .tools import join_urls, PlanStatus, LayerClass, GeomType


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
                f"Failed to get layer classes: {response.status_code} "
                f"{response.text}"
            )

    def get_ready_layer_classes(self) -> List[str]:
        response = self._make_vrequest("GET", "/base/readyLayers")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get ready layer classes: "
                f"{response.status_code} {response.text}"
            )

    def get_available_actions(self) -> List[str]:
        response = self._make_vrequest("GET", "/base/availableActions")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get available actions: "
                f"{response.status_code} {response.text}"
            )

    # Tools Execution
    def get_tool_required_payload(self, action: str) -> Dict[str, Any]:
        response = self._make_vrequest(
            "GET",
            f"/tool/requiredPayload/{action}",
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get tool required payload: "
                f"{response.status_code} {response.text}"
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

    # Projects
    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        body = {
            "name": name,
        }
        if description:
            body["description"] = description
        response = self._make_vrequest(
            "POST",
            "/project",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to create project: {response.status_code} "
                f"{response.text}"
            )

    def get_projects(
        self,
        page: int,
        per_page: int,
        start_utc: Optional[str] = None,
        end_utc: Optional[str] = None,
        sort_by_updated: bool = False,
        desc: bool = True,
    ) -> List[Dict[str, Any]]:
        response = self._make_vrequest(
            "GET",
            "/project",
            params={
                "page": page,
                "per_page": per_page,
                "start_utc": start_utc,
                "end_utc": end_utc,
                "sort_by_updated": sort_by_updated,
                "desc": desc,
            },
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get projects: {response.status_code} "
                f"{response.text}"
            )

    def get_project(
        self,
        project_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest("GET", f"/project/{project_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get project: {response.status_code} "
                f"{response.text}"
            )

    def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        body = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description
        response = self._make_vrequest(
            "PUT",
            f"/project/{project_id}",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to update project: {response.status_code} "
                f"{response.text}"
            )

    def delete_project(
        self,
        project_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest("DELETE", f"/project/{project_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to delete project: {response.status_code} "
                f"{response.text}"
            )

    # Plans
    def create_plan(
        self,
        project_id: str,
        name: str,
        description: Optional[str] = None,
        status: Optional[PlanStatus] = None,
    ) -> Dict[str, Any]:
        body = {
            "project_id": project_id,
            "name": name,
        }
        if description:
            body["description"] = description
        if status:
            body["status"] = status.value
        response = self._make_vrequest(
            "POST",
            "/plan",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to create plan: {response.status_code} "
                f"{response.text}"
            )

    def get_plans(
        self,
        page: int,
        per_page: int,
        start_utc: Optional[str] = None,
        end_utc: Optional[str] = None,
        sort_by_updated: bool = False,
        desc: bool = True,
        project_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = {
            "page": page,
            "per_page": per_page,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "sort_by_updated": sort_by_updated,
            "desc": desc,
        }
        if project_id:
            params["project_id"] = project_id
        response = self._make_vrequest(
            "GET",
            "/plan",
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get plans: {response.status_code} "
                f"{response.text}"
            )

    def get_plan(
        self,
        plan_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest("GET", f"/plan/{plan_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get plan: {response.status_code} "
                f"{response.text}"
            )

    def update_plan(
        self,
        plan_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[PlanStatus] = None,
    ) -> Dict[str, Any]:
        body = {}
        if name:
            body["name"] = name
        if description:
            body["description"] = description
        if status:
            body["status"] = status.value
        response = self._make_vrequest(
            "PUT",
            f"/plan/{plan_id}",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to update plan: {response.status_code} "
                f"{response.text}"
            )

    def delete_plan(
        self,
        plan_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest("DELETE", f"/plan/{plan_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to delete plan: {response.status_code} "
                f"{response.text}"
            )

    # Layers
    def create_layer(
        self,
        plan_id: str,
        layer_class: LayerClass,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        body = {
            "plan_id": plan_id,
            "lclass": layer_class.value,
        }
        if name:
            body["name"] = name
        response = self._make_vrequest(
            "POST",
            "/layer",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to create layer: {response.status_code} "
                f"{response.text}"
            )

    def get_layers(
        self,
        page: int,
        per_page: int,
        start_utc: Optional[str] = None,
        end_utc: Optional[str] = None,
        sort_by_updated: bool = False,
        desc: bool = True,
        plan_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = {
            "page": page,
            "per_page": per_page,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "sort_by_updated": sort_by_updated,
            "desc": desc,
        }
        if plan_id:
            params["plan_id"] = plan_id
        response = self._make_vrequest(
            "GET",
            "/layer",
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get layers: {response.status_code} "
                f"{response.text}"
            )

    def get_layer(
        self,
        layer_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest(
            "GET",
            f"/layer/{layer_id}",
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get layer: {response.status_code} "
                f"{response.text}"
            )

    def update_layer(
        self,
        layer_id: str,
        layer_class: Optional[LayerClass] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        body = {}
        if layer_class:
            body["lclass"] = layer_class.value
        if name:
            body["name"] = name
        response = self._make_vrequest(
            "PUT",
            f"/layer/{layer_id}",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to update layer: {response.status_code} "
                f"{response.text}"
            )

    def delete_layer(
        self,
        layer_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest("DELETE", f"/layer/{layer_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to delete layer: {response.status_code} "
                f"{response.text}"
            )

    # Features
    def create_feature(
        self,
        layer_id: str,
        geom_type: GeomType,
        coordinates: Union[
            List[float], List[List[float]], List[List[List[float]]]
        ]
    ) -> Dict[str, Any]:
        body = {
            "layer_id": layer_id,
            "geom_type": geom_type.value,
            "coordinates": coordinates,
        }
        response = self._make_vrequest(
            "POST",
            "/feature",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to create feature: {response.status_code} "
                f"{response.text}"
            )

    def create_feature_batch(
        self,
        layer_id: str,
        geom_type: GeomType,
        features_coordinates: List[
            Union[List[float], List[List[float]], List[List[List[float]]]]
        ]
    ) -> Dict[str, Any]:
        body = {
            "layer_id": layer_id,
            "geom_type": geom_type.value,
            "features_coordinates": features_coordinates,
        }
        response = self._make_vrequest(
            "POST",
            "/feature/batch",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to create feature batch: {response.status_code} "
                f"{response.text}"
            )

    def get_features(
        self,
        page: int,
        per_page: int,
        start_utc: Optional[str] = None,
        end_utc: Optional[str] = None,
        sort_by_updated: bool = False,
        desc: bool = True,
        layer_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = {
            "page": page,
            "per_page": per_page,
            "start_utc": start_utc,
            "end_utc": end_utc,
            "sort_by_updated": sort_by_updated,
            "desc": desc,
        }
        if layer_id:
            params["layer_id"] = layer_id
        response = self._make_vrequest(
            "GET",
            "/feature",
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get layers: {response.status_code} "
                f"{response.text}"
            )

    def get_feature(
        self,
        feature_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest(
            "GET",
            f"/feature/{feature_id}",
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to get feature: {response.status_code} "
                f"{response.text}"
            )

    def update_feature(
        self,
        feature_id: str,
        geom_type: Optional[GeomType] = None,
        coordinates: Optional[
            Union[List[float], List[List[float]], List[List[List[float]]]]
        ] = None,
    ) -> Dict[str, Any]:
        body = {}
        if geom_type:
            body["geom_type"] = geom_type.value
        if coordinates:
            body["coordinates"] = coordinates
        response = self._make_vrequest(
            "PUT",
            f"/feature/{feature_id}",
            json=body,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to update feature: {response.status_code} "
                f"{response.text}"
            )

    def delete_feature(
        self,
        feature_id: str,
    ) -> Dict[str, Any]:
        response = self._make_vrequest("DELETE", f"/feature/{feature_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to delete feature: {response.status_code} "
                f"{response.text}"
            )

    def delete_feature_batch(
        self,
        feature_ids: List[str],
    ) -> Dict[str, Any]:
        response = self._make_vrequest(
            "DELETE",
            "/feature/batch",
            json=feature_ids,
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Failed to delete feature batch: {response.status_code} "
                f"{response.text}"
            )
