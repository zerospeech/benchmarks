import requests

from zerospeech.out import console


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
