from __future__ import annotations

import requests

from .base import NSID
from .republic import Vote
from .. import errors

class Party:
    def __init__(self, org_id: NSID):
        self._url: str = ''
        self._headers: dict = {}

        self.org_id = org_id

        self.color: int = 0x000000
        self.motto: str = None
        self.scale: dict = {}
        self.last_election: int = None

    def _load(self, _data: dict, url: str = None, headers: dict = None):
        self._url = url
        self._headers = headers

        self.org_id = _data['org_id']

        self.color = _data['color']
        self.motto = _data['motto']
        self.scale = _data['politiscales']
        self.last_election = _data['last_election']

    def cancel_candidacy(self, election: Election):
        election.cancel_candidacy()

class Election:
    def __init__(self, id: NSID):
        self._url: str = ''
        self._headers: dict = {}

        self.id = id
        self.type: str = 'full' # Partial = législatives, full = totales
        self.vote: Vote = None

    def _load(self, _data: dict, url: str = None, headers: str = None):
        self._url = url
        self._headers = headers

        self.id = _data['id']
        self.type = _data['type']

        self.vote = Vote(_data['vote']['id'])
        self.vote._load(_data['vote'], url, headers)

    def close(self):
        if self.vote:
            self.vote.close()
        else:
            return

    def add_vote(self, id: str):
        if self.vote:
            self.vote.add_vote(id)
        else:
            return

    def submit_candidacy(self):
        res = requests.put(f"{self._url}/submit")

        if 500 <= res.status_code < 600:
            raise errors.globals.ServerDownError()

        _data = res.json()

        if res.status_code == 400:
            if _data['message'] == "MissingParam":
                raise errors.globals.MissingParamError(f"Missing parameter '{_data['param']}'.")
            elif _data['message'] == "InvalidParam":
                raise errors.globals.InvalidParamError(f"Invalid parameter '{_data['param']}'.")
            elif _data['message'] == "InvalidToken":
                raise errors.globals.AuthError("Token is not valid.")

        elif res.status_code == 401:
            raise errors.globals.AuthError(_data['message'])

        elif res.status_code == 403:
            raise errors.globals.PermissionError(_data['message'])

        elif res.status_code == 404:
            raise errors.globals.NotFoundError(_data['message'])

    def cancel_candidacy(self):
        res = requests.put(f"{self._url}/cancel_candidacy")

        if 500 <= res.status_code < 600:
            raise errors.globals.ServerDownError()

        _data = res.json()

        if res.status_code == 400:
            if _data['message'] == "MissingParam":
                raise errors.globals.MissingParamError(f"Missing parameter '{_data['param']}'.")
            elif _data['message'] == "InvalidParam":
                raise errors.globals.InvalidParamError(f"Invalid parameter '{_data['param']}'.")
            elif _data['message'] == "InvalidToken":
                raise errors.globals.AuthError("Token is not valid.")

        elif res.status_code == 401:
            raise errors.globals.AuthError(_data['message'])

        elif res.status_code == 403:
            raise errors.globals.PermissionError(_data['message'])

        elif res.status_code == 404:
            raise errors.globals.NotFoundError(_data['message'])