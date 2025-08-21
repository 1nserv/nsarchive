import random
import time

from ..models.base import *
from ..models.state import *
from ..models.scale import *

from .. import database as db


class StateInterface(Interface):
    """
    Gère les interactions avec les votes et les officiers.

    ## Informations
    - Liste des partis enregistrés: `.Party`
    - Liste des officiers et candidats: `.Candidate`
    - Résultats des votes: `.Vote`
    """

    def __init__(self, path: str) -> None:
        super().__init__(path)


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
        data = db.get_item(self.path, 'votes', id)

        vote = Vote(id)
        vote._load(data, self.path)

        return vote

    def open_vote(
        self,
        title: str = None, # Titre du vote
        author: NSID = 0x0, # ID de l'auteur du vote
        type: str = 'normal', # Type de vote
        anonymous: bool = True, # Vote anonyme ou non
        options: list[dict | str ] = [], # Options du vote
        start: int = round(time.time()), # Début du vote
        end: int = None, # Fin du vote
        min_choices: int = None, # Nombre minimum de choix
        max_choices: int = None, # Nombre maximum de choix
        majority: int = 50 # Majorité nécessaire à ce vote
    ) -> Vote:


        opts: dict = {}

        for opt in options:
            if isinstance(opt, str) or opt.get('id') is None:
                _opt_id = NSID(random.randint(100000, 999999))
                _opt_title = opt.get('title', _opt_id) if isinstance(opt, dict) else opt
            else:
                if opt['id'] in opts.keys():
                    raise KeyError(f"Option with key '{opt['id']}' already exists.")
                else:
                    _opt_id = NSID(opt['id'])

            opts[_opt_id] = {
                'title': _opt_title,
                'count': 0
                # 'voters': [] | TODO: issue #4
            }

        _TYPES = (
            'normal',
            'partial',
            'full',
            '2pos',
            '3pos'
        )
        
        if type not in _TYPES:
            raise ValueError(f"Type '{type}' not recognized.")
        
        if min_choices > max_choices:
            raise ValueError("Minimimum choices must be smaller than maximum choices.")
        
        if not 50 <= majority <= 100:
            raise ValueError(f"Majority must be between 50 and 100 both included, not {majority}")
        
        if start - 7200 <= time.time(): # 2h avant le vote pour rajouter des options supplémentaires
            if min_choices > len(opts) or max_choices > len(opts):
                pass


        data = {
            'id': NSID(round(time.time() * 1000)),
            'title': title,
            'author': NSID(author),
            'type': type,
            'anonymous': bool(anonymous),
            'min_choices': int(min_choices),
            'max_choices': int(max_choices),
            'majority': int(majority),
            'start_date': int(start),
            'end_date': int(end),
            'options': opts
            # 'voters': []
        }

        db.put_item(self.path, 'votes', data)

        vote = Vote(data['id'])
        vote._load(data, self.path)

        return vote

    # Aucune possibilité de supprimer un vote


    """
    PARTIS
    """

    def get_party(self, id: NSID) -> Party:
        """
        Récupère un parti politique.

        ## Paramètres
        id: `NSID`\n
            ID du parti.

        ## Renvoie
        - `.Party`
        """

        id = NSID(id)
        data = db.get_item(self.path, 'parties', str(id))

        if data is None:
            return

        party = Party(id)
        party._load(data, self.path)

        return party

    def register_party(self, id: NSID, color: int, motto: str = None, scale: dict | Scale = {}) -> Party:
        """
        Enregistre un nouveau parti pour que ses députés puissent s'y présenter.

        ## Paramètres
        - id: `NSID`\n
            ID de l'entreprise à laquelle correspond le parti
        - color: `int`\n
            Couleur du parti
        - motto: `str`\n
            Devise du parti
        - scale: `.Scale`\n
            Résultats du parti au test Politiscales
        """

        data = {
            'id': id,
            'color': color,
            'motto': motto,
            'scale': scale.__dict__ if isinstance(scale, Scale) else scale
        }

        db.put_item(self.path, 'parties', data)


        # TRAITEMENT

        party = Party(data['org_id'])
        party._load(data, self.path)

        return party