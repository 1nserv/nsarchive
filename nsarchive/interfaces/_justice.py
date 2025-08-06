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

    """
    PROCÈS
    """

    def get_lawsuit(self, id: NSID) -> Lawsuit:
        res = requests.get(
            f"{self.url}/justice/lawsuits/{id}",
            headers = self.default_headers,
        )

        if res.status_code != 200:
            res.raise_for_status()

        lawsuit = Lawsuit(id)
        lawsuit._load(res.json(), f"{self.url}/justice/lawsuits/{id}", self.default_headers)

        return lawsuit

    def open_lawsuit(self, target: NSID, title: str = None, report: Report = None) -> Lawsuit:
        payload = {}
        if title: payload['title'] = title

        res = requests.put(
            f"{self.url}/justice/open_lawsuit?target={target}{('&report=' + report.id) if report else ''}",
            headers = self.default_headers,
            json = payload
        )

        if res.status_code != 200:
            res.raise_for_status()

        lawsuit = Lawsuit(NSID(res.json()['id']))
        lawsuit._load(res.json(), f"{self.url}/justice/lawsuits/{report.id}", self.default_headers)

        return lawsuit

    """
    SANCTIONS
    """

    def get_sanction(self, id: NSID) -> Sanction:
        res = requests.get(
            f"{self.url}/justice/sanctions/{id}",
            headers = self.default_headers,
        )

        if res.status_code != 200:
            res.raise_for_status()

        sanction = Sanction(id)
        sanction._load(res.json(), f"{self.url}/justice/sanctions/{id}", self.default_headers)

        return sanction

    def add_sanction(self, target: NSID, _type: str, duration: int = None, title: str = None, lawsuit: Lawsuit = None) -> Sanction:
        payload = {}
        if title: payload['title'] = title

        res = requests.put(
            f"{self.url}/justice/add_sanction?type={_type}&target={target}&date={str(round(time.time()))}{('&duration=' + str(duration)) if duration else ''}{('&case=' + lawsuit.id) if lawsuit else ''}",
            headers = self.default_headers,
            json = payload
        )

        if res.status_code != 200:
            res.raise_for_status()

        sanction = Sanction(NSID(res.json()['id']))
        sanction._load(res.json(), f"{self.url}/justice/sanctions/{sanction.id}", self.default_headers)

        return sanction