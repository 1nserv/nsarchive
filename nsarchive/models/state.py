from __future__ import annotations

import json
import time

from .base import NSID
from .. import database as db


class VoteOption:
    """
    Option disponible lors d'un vote

    ## Attributs
    - title: `str`\n
        Label de l'option
    - count: `int`\n
        Nombre de sympathisants pour cette option
    """

    def __init__(self, title: str):
        self.title: str = title
        self.count: int = 0
        # self.voters: list = [] | TODO: issue #4

    def __repr__(self) -> dict:
        return json.dumps(self.__dict__)

    def _load(self, _data: dict):
        self.title = str(_data['title'])
        self.count = int(_data['count'])
        # self.voters = list(map(NSID, _data['voters'])) | TODO: issue #4

class Vote:
    """
    Classe de référence pour les différents votes du serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant du vote
    - title: `str`\n
        Titre du vote
    - author: `NSID`\n
        Identifiant de l'auteur du vote
    - type: `str`\n
        Type du vote (`normal`, `partial`, `full`, `2pos`, `3pos`)
    - majority: `int` de 50 à 100 inclus\n
        Pourcentage nécessaire pour qu'une option soit retenue
    - min_choices: `int`\n
        Nombre minimum de choix possibles
    - max_choices: `int`\n
        Nombre maximum de choix possibles
    - start_date: `int`\n
        Date de début du vote
    - end_date: `int`\n
        Date limite pour voter
    - options: dict[str, .VoteOption]\n
        Liste des choix disponibles
    """

    def __init__(self, id: NSID = None) -> None:
        self._path: str = ''

        self.id: NSID = id if id else NSID(0)
        self.title: str = ""
        self.author: NSID = NSID(0)

        """
        ## Types de vote

        - Vote normal: `normal`
        - Législatives: `partial`
        - Présidentielles: `full`
        - Pour/Contre: `2pos`
        - Pour/Contre/Blanc: `3pos`
        """

        self.type: str = 'normal'
        self.anonymous: bool = True

        self.min_choices: int = 1
        self.max_choices: int = 1
        self.majority: int = 50 # Entre 50% et 100% inclus

        self.start_date: int = round(time.time())
        self.end_date: int = 0
        # self.voters: list[NSID] = [] | TODO: issue #4

        self.options: dict[str, VoteOption] = {}

    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = NSID(_data['id'])
        self.title = _data['title']
        self.author = _data['author']

        self.type = _data['type']
        self.majority = _data['majority']

        self.start_date = _data['start']
        self.end_date = _data['end']
        # self.voters = list(map(NSID, _data['voters'])) | TODO: issue #4

        self.options = {}

        for _opt_id, opt in _data['options'].items():
            option = VoteOption(opt['title'])
            option._load(opt)

            self.options[_opt_id] = option

    def _to_dict(self) -> dict:
        """
        TODO: issue #4

        if self.anonymous:
            for opt in self.options.values():
                opt.voters.clear()
        """

        return {
            'id': str(self.id),
            'title': self.title,
            'author': str(self.author),
            'type': self.type,
            'majority': self.majority,
            'start': self.start_date,
            'end': self.end_date,
            # 'voters': list(map(str, self.voters)) | TODO: issue #4
            'options': [ opt.__dict__ for opt in self.options ]
        }

    def save(self):
        db.put_item(self._path, 'votes', self._to_dict())


    def get(self, id: str) -> VoteOption:
        if id in self.options.keys():
            return self.options[id]
        else:
            raise KeyError(f"Option {id} not found in vote {self.id}")

    def add_vote(self, id: str, _save: bool = True): # author: NSID):
        """
        Ajoute un vote à l'option spécifiée
        """

        self.get(id).count += 1
        # self.get(id).voters.append(author) | # TODO: issue #4
        # self.voters.append(author) | TODO: issue #4

        if _save:
            self.save()

    def add_votes(self, *ids: str): # author: NSID):
        """
        Ajoute un vote aux loptions spécifiées
        """

        for id in ids:
            self.add_vote(id, _save = False)

        self.save()

    def close(self):
        """
        Ferme le vote
        """

        self.end_date = round(time.time())
        self.save()


class Party:
    def __init__(self, id: NSID):
        self._path: str = ''

        self.id = id

        self.color: int = 0x000000
        self.motto: str = None
        self.scale: dict = {}

    def _load(self, _data: dict, path: str ):
        self._path = path

        self.id = _data['id']

        self.color = _data['color']
        self.motto = _data['motto']
        self.scale = _data['politiscales']

    def _to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'color': self.color,
            'motto': self.motto,
            'scale': self.scale,
        }

    def save(self):
        db.put_item(self._path, 'parties', self._to_dict())


# class Candidate | TODO: issue #6