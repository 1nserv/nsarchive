import time

from ..cls.base import *
from ..cls.archives import *
from ..cls.republic import *


class StateInstance(Instance):
    """
    Gère les interactions avec les votes et les officiers.

    ## Informations
    - Liste des partis enregistrés: `.Party`
    - Liste des élections: `.Election`
    - Liste des officiers et candidats: `.Officer | .Candidate`
    - Résultats des votes: `.Vote`
    """

    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)

    """
    ---- VOTES ----
    """

    def get_vote(self, id: NSID) -> Vote:
        """
        Récupère un vote.

        ## Paramètres
        id: `NSID`\n
            ID du vote.

        ## Renvoie
        - `.Vote`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/votes/{id}", headers = self.default_headers)

        if not res:
            return None

        _data = res.json()

        vote = Vote(id, _data['title'])
        vote._load(_data, url = f"{self.url}/votes/{id}", headers = self.default_headers)

        return vote

    def open_vote(self, title: str = None, options: list[dict] = [], end: int = 0) -> Vote:
        """
        Déclenche un vote dans la base de données.

        ## Paramètres
        - title: `str`\n
            Titre du vote
        - options: list[dict]\n
            Liste des choix disponibles
        - end: `int`\n
            Fin du vote (timestamp)
        """

        payload = {
            "options": options,
            "end_date": end
        }

        if title:
            payload['title'] = title

        res = requests.put(f"{self.url}/open_vote", headers = self.default_headers, json = _data)

        if res.status_code == 200:
            _data = res.json()

            vote = Vote()
            vote._load(_data, url = f"{self.url}/votes/{_data['id']}", headers = self.default_headers)
        else:
            res.raise_for_status()

    # Aucune possibilité de supprimer un vote