import requests
from urllib.parse import urljoin


class Search:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "search/")

    def query_book(self, **kwargs) -> int:
        json = kwargs
        url = urljoin(self.url_prefix, "query_book")
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("books")