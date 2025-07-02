from ..cls.base import *
from ..cls.entities import *

from ..cls import entities # Pour les default_headers

class EntityInstance(Instance):
    """
    Instance qui vous permettra d'interagir avec les profils des membres ainsi que les différents métiers et secteurs d'activité.

    ## Informations disponibles
    - Profil des membres et des entreprises: `.User | .Organization | .Entity`
    - Participation d'un membre à différent votes: `.User | .Organization | .Entity`
    - Appartenance et permissions d'un membre dans un groupe: `.GroupMember.MemberPermissions`
    - Position légale et permissions d'une entité: `.Position.Permissions`
    - Sanctions et modifications d'une entité: `.Action[ .AdminAction | .Sanction ]`
    """

    def __init__(self, url: str, token: str = None) -> None:
        super().__init__(url, token)

    """
    ---- ENTITÉS ----
    """

    def get_entity(self, id: NSID, _class: str = None) -> User | Organization | Entity:
        """
        Fonction permettant de récupérer le profil public d'une entité.\n

        ## Paramètres
        id: `NSID`
            ID héxadécimal de l'entité à récupérer
        _class: `str`
            Classe du modèle à prendre (`.User` ou `.Organization`)

        ## Renvoie
        - `.User` dans le cas où l'entité choisie est un membre
        - `.Organization` dans le cas où c'est un groupe
        - `.Entity` dans le cas où c'est indéterminé
        """

        id = NSID(id)

        if _class == "user":
            _data = self._get_by_ID('individuals', id)
        elif _class == "group":
            _data = self._get_by_ID('organizations', id)
        else:
            _data = self._get_by_ID('entities', id)

        if _data is None: # ID inexistant chez les entités
            return None

        if _data['_class'] == 'individuals':
            entity = User(id)
        elif _data['_class'] == 'organizations':
            entity = Organization(id)
        else: 
            entity = Entity(id)

        entity._load(_data, self.url, self.default_headers)

        return entity

    def create_entity(self, id: NSID, name: str, _class: str, position: str = 'membre', zone: int = 10):
        """
        Fonction permettant de créer ou modifier une entité.

        ## Paramètres
        - id (`NSID`): Identifiant NSID
        - name (`str`): Nom d'usage
        - _class (`"user"` ou `"group"`): Type de l'entité
        - position (`str`, optionnel): ID de la position civile
        - zone (`int`, optionnel): ID de la zone civile
        """

        id = NSID(id)

        if _class in ('group', 'organization'):
            _class = 'organizations'
        elif _class in ('user', 'individual'):
            _class = 'individuals'
        else:
            return

        self._put_in_db(
            f"/new_model/{_class}?id={urllib.parse.quote(id)}&name={urllib.parse.quote(name)}&position={urllib.parse.quote(position)}&zone={urllib.parse.quote(zone)}",
            headers = self.default_headers,
            use_PUT = True
        )

        entity = self.get_entity(id)

        if _class == "individuals":
            entity._url = f"{self.url}/model/individuals/{id}"
        elif isinstance(entity, Organization):
            entity._url = f"{self.url}/model/organizations/{id}"
            entity.avatar_url = f"{entity._url}/avatar"
        else:
            entity._url = f"{self.url}/model/entities/{id}"

        return entity


    def delete_entity(self, entity: Entity):
        """
        Fonction permettant de supprimer le profil d'une entité

        ## Paramètres
        entity: `.Entity`\n
            L'entité à supprimer
        """

        res = requests.post(f"{entity._url}/delete", headers = self.default_headers,)

        if res.status_code != 200:
            res.raise_for_status()

    def fetch_entities(self, **query: typing.Any) -> list[ Entity | User | Organization ]:
        """
        Récupère une liste d'entités en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les entités.

        ## Renvoie
        - `list[.Entity | .User | .Organization]`
        """

        if "_class" in query.keys():
            if query["_class"] == "individuals":
                del query["_class"]
                _res = self.fetch('individuals', **query)
            elif query["_class"] == "organizations":
                del query["_class"]
                _res = self.fetch('organizations', **query)
            else:
                del query["_class"]
                _res = self.fetch('entities', **query)
        else:
            _res = self.fetch('entities', **query)

        res = []

        for _entity in _res:
            if _entity is None: continue

            if _entity['_class'] == 'individuals':
                entity = User(_entity["id"])
            elif _entity['_class'] == 'organizations':
                entity = Organization(_entity["id"])
            else:
                entity = Entity(_entity["id"])

            entity._load(_entity, self.url, self.default_headers)

            res.append(entity)

        return res



    def get_position(self, id: str) -> Position:
        """
        Récupère une position légale (métier, domaine professionnel).

        ## Paramètres
        id: `str`\n
            ID de la position (SENSIBLE À LA CASSE !)

        ## Renvoie
        - `.Position`
        """

        _data = self._get_by_ID('positions', id)

        if _data is None:
            return None

        position = Position(id)
        position._load(_data, self.url, self.default_headers)

        return position

    def fetch_positions(self, **query: typing.Any) -> list[Position]:
        """
        Récupère une liste de positions en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les positions.

        ## Renvoie
        - `list[.Position]`
        """

        _res = self.fetch('positions', **query)
        res = []

        for _data in _res:
            pos = Position()
            pos._load(_data, self.url, self.default_headers)

            res.append(pos)

        return res