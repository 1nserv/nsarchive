import requests
import time

from nsarchive.cls.base import NSID

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

    def __init__(self, id: str, title: str = None, count: int = 0):
        self.id = id
        self.title = title if title else id
        self.count = count

class Vote:
    """
    Classe de référence pour les différents votes du serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant du vote
    - title: `str`\n
        Titre du vote
    - options: list[.VoteOption]\n
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

        self.options: list[VoteOption] = []

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url + '/votes/' + _data['id']
        self._headers = headers

        self.id = NSID(_data['id'])
        self.title = _data['title']
        self.author = _data['author_id']

        self.startDate = _data['start_date']
        self.endDate = _data['end_date']

        self.options = []

        for opt in _data['options']:
            option = VoteOption(opt["id"], opt["title"])
            option.count = opt["count"]

            self.options.append(option)

    def get(self, id: str) -> VoteOption:
        for opt in self.options:
            if opt.id == id:
                return opt
        else:
            raise ValueError(f"Option {id} not found in vote {self.id}")

    def add_vote(self, id: str):
        """
        Ajoute un vote à l'option spécifiée
        """

        res = requests.post(f"{self._url}/vote?choice={id}", headers = self._headers)

        if res.status_code == 200:
            for opt in self.options:
                if opt.id == id:
                    opt.count += 1
                    break
            else:
                raise ValueError(f"Option {id} not found in vote {self.id}")
        else:
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

class Lawsuit(Vote):
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