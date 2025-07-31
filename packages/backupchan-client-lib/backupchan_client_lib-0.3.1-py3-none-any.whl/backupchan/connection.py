import requests
import json

class Connection:
    def __init__(self, host: str, port: int, api_key: str):
        # TODO check these
        self.api_key = api_key

        if host.startswith("http://") or host.startswith("https://"):
            server_host = host.rstrip("/")
        else:
            server_host = f"http://{host.rstrip('/')}"
        self.base_url = f"{server_host}:{port}"

    def endpoint_url(self, endpoint: str) -> str:
        return f"{self.base_url}/api/{endpoint.rstrip('/')}"
    
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}"}

    def get(self, endpoint: str, raise_on_error=False) -> tuple[dict, int]:
        response = requests.get(self.endpoint_url(endpoint), headers=self.headers())
        if raise_on_error:
            response.raise_for_status()
        return response.json(), response.status_code

    def post(self, endpoint: str, data: dict, raise_on_error=False) -> tuple[dict, int]:
        response = requests.post(self.endpoint_url(endpoint), headers=self.headers(), json=data)
        if raise_on_error:
            response.raise_for_status()
        return response.json(), response.status_code

    def post_form(self, endpoint: str, data: dict, files: dict, raise_on_error=False) -> tuple[dict, int]:
        response = requests.post(self.endpoint_url(endpoint), headers=self.headers(), data=data, files=files)
        if raise_on_error:
            response.raise_for_status()
        return response.json(), response.status_code

    def patch(self, endpoint: str, data: dict, raise_on_error=False) -> tuple[dict, int]:
        response = requests.patch(self.endpoint_url(endpoint), headers=self.headers(), json=data)
        if raise_on_error:
            response.raise_for_status()
        return response.json(), response.status_code

    def delete(self, endpoint: str, data: dict, raise_on_error=False) -> tuple[dict, int]:
        response = requests.delete(self.endpoint_url(endpoint), headers=self.headers(), json=data)
        if raise_on_error:
            response.raise_for_status()
        return response.json(), response.status_code
