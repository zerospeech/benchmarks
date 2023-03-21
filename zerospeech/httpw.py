""" Wrapper around HTTP requests """
import requests

from zerospeech.out import console


class APIHTTPException(Exception):
    def __init__(self, method: str, status_code: int, message: str, trace: str = ""):
        self.method = method
        self.status_code = status_code
        self.msg = message
        self.trace = trace
        super().__init__(message)

    def __str__(self):
        """ String representation """
        return f"{self.method}: returned {self.status_code} => {self.msg}"

    @classmethod
    def from_request(cls, method_name: str, response: requests.Response):
        """ Make APIHTTPException from a request Response """
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            data = dict()

        reason = data.get('detail', '')
        msg = data.get('message', '')
        return APIHTTPException(
            method=method_name, status_code=response.status_code,
            message=f"{reason}{msg}", trace=data.get('trace', '')
        )


def post(url: str, debug: bool = False, **kwargs) -> requests.Response:
    """ Wrapper around HTTP POST request using requests library  """
    if debug:
        console.print(f"POST {url}")
        console.print(kwargs)
    return requests.post(url, **kwargs)


def get(url: str, debug: bool = False, **kwargs) -> requests.Response:
    """ Wrapper around HTTP GET request using requests library  """
    if debug:
        console.print(f"GET {url}")
        console.print(kwargs)
    return requests.get(url, **kwargs)
