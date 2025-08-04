import requests
import time

from ..models.base import *
from ..models.justice import *

class JusticeInterface(Interface):
    """
    Gère les procès, sanctions et signalements.
    """

    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)

    """
    SIGNALEMENTS
    """

    def get_report(self, id: NSID) -> Report:
        res = requests.get(
            f"{self.url}/justice/reports/{id}",
            headers = self.default_headers,
        )

        if res.status_code != 200:
            res.raise_for_status()

        report = Report(id)
        report._load(res.json(), f"{self.url}/justice/reports/{id}", self.default_headers)

        return report

    def submit_report(self, target: NSID, reason: str = None, details: str = None) -> Report:
        payload = {}
        if reason: payload['reason'] = reason
        if details: payload['details'] = details

        res = requests.put(
            f"{self.url}/justice/submit_report?target={target}",
            headers = self.default_headers,
            json = payload
        )

        if res.status_code != 200:
            res.raise_for_status()

        report = Report(NSID(res.json()['id']))
        report._load(res.json(), f"{self.url}/justice/reports/{report.id}", self.default_headers)

        return report