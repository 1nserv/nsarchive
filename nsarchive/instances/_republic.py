import time

from ..cls.base import *
from ..cls.archives import *
from ..cls.republic import *


class RepublicInstance(Instance):
    """
        *INDISPONIBLE DANS CETTE VERSION.*\n
    Gère les interactions avec les votes, les archives de la république, et les fonctionnaires.

    ## Informations
    - Résultats des votes et procès: `.Vote | .Referendum | .Lawsuit`
    - Différentes institutions: `.State | .Administration | .Government | .Assembly | .Court | .PoliceForces`
    - Occupants des différents rôles et historique de leurs actions: `.Official`
    """

    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)
    
    """
    ---- VOTES & REFERENDUMS ----
    """

    def get_vote(self, id: NSID) -> Vote | Referendum | Lawsuit:
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Récupère un vote spécifique.

        ## Paramètres
        id: `NSID`\n
            ID du vote.

        ## Renvoie
        - `.Vote | .Referendum | .Lawsuit`
        """

        return Vote(NSID(id), "Vote Inconnu") # Provisoire

        id = NSID(id)
        _data = self._get_by_ID('votes', id)

        if not _data: # Pas dans les votes -> peut-être dans les procès
            _data = self._get_by_ID('lawsuits', id)

        if not _data: # Le vote n'existe juste pas
            return None
        elif '_type' not in _data.keys(): # Le vote est un procès
            _data['_type'] = "lawsuit"

        if _data['_type'] == 'vote':
            vote = Vote(id, _data['title'])
        elif _data['_type'] == 'referendum':
            vote = Referendum(id, _data['title'])
            vote.choices = []
        elif _data['_type'] == 'lawsuit':
            vote = Lawsuit(id, _data['title'])
            vote.choices = []
        else:
            vote = Vote('0', 'Unknown Vote')

        vote.author = _data['author_id']
        vote.startDate = _data['start_date']
        vote.endDate = _data['end_date']

        for opt in _data['choices']:
            option = VoteOption(opt["id"], opt["title"])
            option.count = opt["count"]

            vote.choices.append(option)

        return vote

    def save_vote(self, vote: Vote | Referendum | Lawsuit):
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Sauvegarde un vote dans la base de données.

        ## Paramètres
        - vote: `.Vote`\n
            Vote à sauvegarder
        """

        return # Provisoire

        vote.id = NSID(vote.id)

        _data = {
            '_type':'vote' if type(vote) == Vote else\
                    'referendum' if type(vote) == Referendum else\
                    'lawsuit' if type(vote) == Lawsuit else\
                    'unknown',
            'id': NSID(vote.id),
            'title': vote.title,
            'author_id': NSID(vote.author),
            'start_date': vote.startDate,
            'end_date': vote.endDate,
            'choices': [ opt.__dict__ for opt in vote.choices ]
        }

        if type(vote) == Lawsuit:
            del _data['_type']
            self._put_in_db('lawsuits', _data)
        else:
            self._put_in_db('votes', _data)

    # Aucune possibilité de supprimer un vote

    """
    ---- INSTITUTION & MANDAT ----
    """

    def get_official(self, id: NSID, current_mandate: bool = True) -> Official:
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Récupère les informations d'un fonctionnaire (mandats, contributions).

        ## Paramètres
        id: `NSID`\n
            ID du fonctionnaire.
        current_mandate: `bool`\n
            Indique si l'on doit récupérer le mandat actuel ou les anciens mandats.

        ## Renvoie
        - `.Official`
        """

        return Official(NSID(id)) # Provisoire

        id = NSID(id)

        base = 'mandate' if current_mandate else 'archives'

        _contributions = self.fetch(base, author = id, _type = 'contrib')
        _mandates = self.fetch(base, target = id, _type = 'election') +\
                    self.fetch(base, target = id, _type = 'promotion')

        user = Official(id)
        for mandate in _mandates:
            if mandate['details']['position'].startswith('MIN'):
                mandate['details']['position'] = 'MIN'

            try:
                user.mandates[mandate['details']['position']] += 1
            except KeyError:
                user.mandates[mandate['details']['position']] = 1

        for contrib in _contributions:
            try:
                user.contributions[contrib['action']] += 1
            except KeyError:
                user.contributions[contrib['action']] = 1

        return user

    def get_institutions(self) -> State:
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Récupère l'état actuel des institutions de la république.
        """

        return State()

        admin = Administration()
        gov = Government(Official('0'))
        assembly = Assembly()
        court = Court()
        police_forces = PoliceForces()

        _get_position: list[dict] = lambda pos : self._select_from_db('functions', 'id', pos)[0]['users']

        admin.members = [ self.get_official(user) for user in _get_position('ADMIN') ]
        admin.president = self.get_official(0xF7DB60DD1C4300A) # happex (remplace Kheops pour l'instant)

        gov.president = self.get_official(0x0)

        minister = lambda code : self.get_official(_get_position(f'MIN_{code}')[0])
        gov.prime_minister = minister('PRIM')
        gov.economy_minister = minister('ECO')
        gov.inner_minister = minister('INN')
        gov.press_minister = minister('AUD')
        gov.justice_minister = minister('JUS')
        gov.outer_minister = minister('OUT')

        assembly.president = self.get_official(_get_position('PRE_AS')[0])
        assembly.members = [ self.get_official(user) for user in _get_position('REPR') ]

        court.president = gov.justice_minister
        court.members = [ self.get_official(user) for user in _get_position('JUDGE') ]

        police_forces.president = gov.inner_minister
        police_forces.members = [ self.get_official(user) for user in _get_position('POLICE') ]

        instits = State()
        instits.administration = admin
        instits.government = gov
        instits.court = court
        instits.assembly = assembly
        instits.police = police_forces

        return instits

    def update_institutions(self, institutions: State):
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Fonction communément appelée après un vote législatif ou une nomination.\n
        Celle-ci met à jour: Le gouvernement (président, ministres), les différents députés et leur président, les différents juges, les différents policiers.\n

        ## Paramètres
        institutions: `.State`\n
            Le nouvel état des institutions, à sauvegarder.
        """

        return # Provisoire

        get_ids = lambda institution : [ member.id for member in institutions.__getattribute__(institution).members ]

        self._put_in_db('functions', { 'id': 'ADMIN', 'users': get_ids('administration') })
        self._put_in_db('functions', { 'id': 'REPR', 'users': get_ids('assembly') })
        self._put_in_db('functions', { 'id': 'JUDGE', 'users': get_ids('court') })
        self._put_in_db('functions', { 'id': 'POLICE', 'users': get_ids('police') })

        self._put_in_db('functions', { 'id': 'PRE_AS', 'users': [ institutions.assembly.president.id ] })
        self._put_in_db('functions', { 'id': 'PRE_REP', 'users': [ institutions.government.president.id ] })

        self._put_in_db('functions', { 'id': 'MIN_PRIM', 'users': [ institutions.government.prime_minister.id ] })
        self._put_in_db('functions', { 'id': 'MIN_INN', 'users': [ institutions.government.inner_minister.id ] })
        self._put_in_db('functions', { 'id': 'MIN_JUS', 'users': [ institutions.government.justice_minister.id ] })
        self._put_in_db('functions', { 'id': 'MIN_ECO', 'users': [ institutions.government.economy_minister.id ] })
        self._put_in_db('functions', { 'id': 'MIN_AUD', 'users': [ institutions.government.press_minister.id ] })
        self._put_in_db('functions', { 'id': 'MIN_OUT', 'users': [ institutions.government.outer_minister.id ] })

    def new_mandate(self, institutions: State, weeks: int = 4):
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Fonction qui amène à supprimer toutes les archives du mandat précédent

        ## Paramètres
        - institutions: `.State`\n
            Nouvel État à sauvegarder
        - weeks: `int`\n
            Nombre de semaines du mandat
        """

        return # Provisoire

        for item in self.fetch('mandate'):
            if item['date'] >= round(time.time()) - weeks * 604800: # On évite de supprimer les informations écrites lors de la période définie
                self._delete_by_ID('mandate', item['id'])

        self.update_institutions(institutions)

    """
    ---- ARCHIVES ----
    """

    def _add_archive(self, archive: Archive):
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Ajoute une archive d'une action (élection, promotion, ou rétrogradation) dans la base de données.

        ## Paramètres
        - archive: `.Archive`\n
            Archive à ajouter
        """

        return # Provisoire

        archive.id = NSID(archive.id)
        _data = archive.__dict__.copy()

        if type(archive) == Election:
            _data['_type'] = "election"
        elif type(archive) == Promotion:
            _data['_type'] = "promotion"
        elif type(archive) == Demotion:
            _data['_type'] = "demotion"
        else:
            _data['_type'] = "unknown"

        self._put_in_db('archives', _data)
        self._put_in_db('mandate', _data) # Ajouter les archives à celle du mandat actuel

    def _get_archive(self, id: NSID) -> Archive | Election | Promotion | Demotion:
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Récupère une archive spécifique.

        ## Paramètres
        id: `NSID`\n
            ID de l'archive.

        ## Renvoie
        - `.Archive | .Election | .Promotion | .Demotion`
        """

        return Archive(NSID(id)) # Provisoire

        id = NSID(id)
        _data = self._get_by_ID('archives', id)

        if _data is None:
            return None

        if _data['_type'] == "election":
            archive = Election(_data['author'], _data['target'], _data['details']['position'])
        elif _data['_type'] == "promotion":
            archive = Promotion(_data['author'], _data['target'], _data['details']['position'])
        elif _data['_type'] == "demotion":
            archive = Demotion(_data['author'], _data['target'])
        else:
            archive = Archive(_data['author'], _data['target'])

        archive.id = id
        archive.action = _data['action']
        archive.date = _data['date']
        archive.details = _data['details']

        return archive

    def _fetch_archives(self, **query) -> list[ Archive | Election | Promotion | Demotion ]:
        """
        *INDISPONIBLE DANS CETTE VERSION.*\n
        Récupère une liste d'archives correspondant à la requête.

        ## Paramètres
        query: `dict`\n
            Requête pour filtrer les archives.

        ## Renvoie
        - `list[.Archive | .Election | .Promotion | .Demotion]`
        """

        return [] # Provisoire

        _res = self.fetch('archives', **query)
        
        return [ self._get_archive(archive['id']) for archive in _res ]
