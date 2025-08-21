import os
import time

from ..models.base import *
from ..models.justice import *

from .. import database as db


class JusticeInterface(Interface):
    """
    Gère les procès, sanctions et signalements.
    """

    def __init__(self, path: str) -> None:
        super().__init__(os.path.join(path, 'justice'))

    """
    SIGNALEMENTS
    """

    def get_report(self, id: NSID) -> Report:
        data = db.get_item(self.path, 'reports', id)

        report = Report(id)
        report._load(data, self.path)

        return report

    def submit_report(self, author: NSID, target: NSID, reason: str = None, details: str = None) -> Report:
        data = {
            'id': NSID(round(time.time() * 1000)),
            'author': NSID(author),
            'target': NSID(target),
            'date': round(time.time()),
            'status': 0,
            'reason': reason,
            'details': details
        }

        db.put_item(self.path, 'reports', data)


        # TRAITEMENT

        report = Report(NSID(data['id']))
        report._load(data, self.path)

        return report

    def fetch_reports(self, **query) -> list[Report]:
        res = db.fetch(f"{self.path}:reports", **query)

        reports = []

        for elem in res:
            report = Report(elem['id'])
            report._load(elem, self.path)

            reports.append(report)

        return reports


    """
    PROCÈS
    """

    def get_lawsuit(self, id: NSID) -> Lawsuit:
        data = db.get_item(self.path, 'lawsuits', id)

        lawsuit = Lawsuit(id)
        lawsuit._load(data, self.path)

        return lawsuit

    def open_lawsuit(self, target: NSID, judge: NSID, title: str = None, report: Report = None, private: bool = True) -> Lawsuit:
        data = {
            'id': report.id or NSID(round(time.time() * 1000)),
            'target': NSID(target),
            'judge': NSID(judge),
            'title': title,
            'date': round(time.time()),
            'report': report.id or None,
            'is_private': private,
            'is_open': False
        }

        lawsuit = Lawsuit(NSID(data['id']))
        lawsuit._load(data, self.path)

        return lawsuit

    def fetch_lawsuits(self, **query) -> list[Lawsuit]:
        res = db.fetch(f"{self.path}:lawsuits", **query)

        lawsuits = []

        for elem in res:
            lawsuit = Lawsuit(elem['id'])
            lawsuit._load(elem, self.path)

            lawsuits.append(lawsuit)

        return lawsuits


    """
    SANCTIONS
    """

    def get_sanction(self, id: NSID) -> Sanction:
        data = db.get_item(self.path, 'sanctions', self.id)

        sanction = Sanction(id)
        sanction._load(data, self.path)

        return sanction

    def add_sanction(self, target: NSID, _type: str, duration: int = None, title: str = None, lawsuit: Lawsuit = None) -> Sanction:
        data = {
            'id': lawsuit.id if lawsuit else NSID(round(time.time() * 1000)),
            'target': NSID(target),
            'type': _type,
            'date': round(time.time()),
            'duration': duration,
            'title': title,
            'lawsuit': lawsuit.id or None
        }

        db.put_item(self.path, 'lawsuits', data)

        sanction = Sanction(NSID(data['id']))
        sanction._load(data, self.path)

        return sanction

    def fetch_sanctions(self, **query) -> list[Sanction]:
        res = db.fetch(f"{self.path}:sanctions", **query)

        sanctions = []

        for elem in res:
            sanction = Sanction(elem['id'])
            sanction._load(elem, self.path)

            sanctions.append(sanction)

        return sanctions