import json
import requests
import time

from .base import NSID

# Votes

class VoteOption:
    """
    Option disponible lors d'un vote

    ## Attributs
    - id: `str`\n
        Identifiant de l'option
    - title: `str`\n
        Label de l'option
    - count: `int`\n
        Nombre de sympathisants pour cette option
    """

    def __init__(self, title: str, count: int = 0):
        self.title: str = title
        self.count: int = count

    def __repr__(self) -> dict:
        return json.dumps({
            'title': self.title,
            'count': self.count
        })

    def _load(self, _data: dict):
        self.title = str(_data['title'])
        self.count = int(_data['count'])

class Vote:
    """
    Classe de référence pour les différents votes du serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant du vote
    - title: `str`\n
        Titre du vote
    - options: dict[str, .VoteOption]\n
        Liste des choix disponibles
    - author: `NSID`\n
        Identifiant de l'auteur du vote
    - startDate: `int`\n
        Date de début du vote
    - endDate: `int`\n
        Date limite pour voter
    """

    def __init__(self, id: NSID = None) -> None:
        self._url: str
        self._headers: dict

        self.id: NSID = id if id else NSID(0)
        self.title: str = ''
        self.author: NSID = NSID(0)

        self.startDate: int = round(time.time())
        self.endDate: int = 0

        self.options: dict[str, VoteOption] = {}

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url
        self._headers = headers

        self.id = NSID(_data['id'])
        self.title = _data['title']
        self.author = _data['author']

        self.startDate = _data['start']
        self.endDate = _data['end']

        self.options = {}

        for _opt_id, opt in _data['options'].items():
            option = VoteOption(*tuple(opt.values()))

            self.options[_opt_id] = option

    def get(self, id: str) -> VoteOption:
        if id in self.options.keys():
            return self.options[id]
        else:
            raise ValueError(f"Option {id} not found in vote {self.id}")

    def add_vote(self, id: str):
        """
        Ajoute un vote à l'option spécifiée
        """

        res = requests.post(f"{self._url}/vote?option={id}", headers = self._headers)

        if res.status_code == 200:
            self.get(id).count += 1
        else:
            print(res.json())
            res.raise_for_status()

    def close(self):
        """
        Ferme le vote
        """

        res = requests.post(f"{self._url}/close", headers = self._headers)

        if res.status_code == 200:
            self.endDate = round(time.time())
        else:
            res.raise_for_status()

class LawsuitVote(Vote):
    """
    Vote à trois positions pour un procès
    """

    def __init__(self, id: NSID, title: str) -> None:
        super().__init__(id, title)

        self.options = [
            VoteOption('guilty', 'Coupable'),
            VoteOption('innocent', 'Innocent'),
            VoteOption('blank', 'Pas d\'avis'),
        ]