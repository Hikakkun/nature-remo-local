import requests
from typing import Callable, Any
from model import IRSignal


class NatureLocalAPIClient:
    def __init__(self, nature_ip_address: str):
        self.__nature_ip_address = nature_ip_address

    def __https_request(
        self,
        request_func: Callable[[str, dict], requests.Response],
        json: dict[str, Any] | None = None,
    ) -> requests.Response:
        url = f"http://{self.__nature_ip_address}/messages"
        headers = {"X-Requested-With": "local", "Content-Type": "application/json"}
        response: requests.Response = request_func(url, headers=headers, json=json)
        response.raise_for_status()
        return response

    def send_ir_signal(self, ir_signal: IRSignal):
        _ = self.__https_request(requests.post, ir_signal.model_dump())

    def get_ir_signal(self) -> IRSignal:
        response = self.__https_request(requests.get)
        return IRSignal(**response.json())
