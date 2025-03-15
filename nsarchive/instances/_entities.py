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

        entities.default_headers = self.default_headers

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
        elif "xp" in _data.keys():
            _data['_type'] = 'user'
        elif "parts" in _data.keys():
            _data['_type'] = 'organization'
        else:
            _data['_type'] = 'entity'

        if _data['_type'] == 'user':
            entity = User(id)
            entity._url = f"{self.url}/model/individuals/{id}"

            entity.xp = _data['xp']
            entity.boosts = _data['boosts']

            entity.votes = [ NSID(vote) for vote in _data['votes'] ]
            entity.groups = [ NSID(group) for group in _data['groups'] ]
        elif _data['_type'] == 'organization':
            entity = Organization(id)
            entity._url = f"{self.url}/model/organizations/{id}"

            res = requests.get(f"{entity._url}/avatar")

            if res.status_code == 200:
                entity.avatar = res.content
            else:
                warnings.warn(f"Failed to get avatar for {id}")

            entity.owner = self.get_entity(NSID(_data['owner_id']))

            for _member in _data['members']:
                member = GroupMember(_member['id'])
                member.permission_level = _member['level']

                entity.append(member)

            entity.parts = []

            for attrs in _data['parts']:
                owner = attrs["owner"]
                entity.parts.extend(attrs['count'] * [ Share(NSID(owner), attrs['worth'] // attrs['count']) ])

            entity.certifications = _data['certifications']
        else: 
            entity = Entity(id)

        entity.name = _data['name']
        entity.position = self.get_position(_data['position']) # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['register_date']

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                entity.additional[key] = int(value[1:])
            else:
                entity.additional[key] = value

        return entity

    def save_entity(self, entity: Entity):
        """
        Fonction permettant de créer ou modifier une entité.

        ## Paramètres
        entity: `.Entity`\n
            L'entité à sauvegarder
        """

        entity.id = NSID(entity.id)

        _data = {
            'id': entity.id,
            'name': entity.name,
            'position': entity.position.id,
            'register_date': entity.registerDate,
            'additional': {},
        }

        for key, value in entity.additional.items():
            if isinstance(value, int) and len(str(int)) >= 15:
                _data['additional'][key] = '\n' + str(value)
            elif type(value) in (str, int):
                _data['additional'][key] = value

        if type(entity) == Organization:
            _data['owner_id'] = NSID(entity.owner.id) if entity.owner else NSID("0")
            _data['members'] = []
            _data['certifications'] = entity.certifications
            _data['parts'] = entity.get_shares(True)

            for member in entity.members:
                _member = {
                    'id': NSID(member.id),
                    'level': member.permission_level
                }

                _data['members'] += [_member]

            entity.save_avatar()
        elif type(entity) == User:
            _data['xp'] = entity.xp
            _data['boosts'] = entity.boosts
            # _data['votes'] = [ NSID(vote) for vote in entity.votes]
        else:
            return

        self._put_in_db(
            f"/new_model/{'individuals' if isinstance(entity, User) else 'organizations'}?id={urllib.parse.quote(entity.id)}&name={urllib.parse.quote(entity.name)}",
            _data,
            headers = self.default_headers,
            use_PUT = True
        )

        entity._url = f"{self.url}/model/{'individuals' if isinstance(entity, User) else 'organizations'}/{entity.id}"


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

        if "_type" in query.keys():
            if query["_type"] == "individual":
                del query["_type"]
                _res = self.fetch('individuals', **query)
            elif query["_type"] == "organization":
                del query["_type"]
                _res = self.fetch('organizations', **query)
            else:
                del query["_type"]
                _res = self.fetch('entities', **query)
        else:
            _res = self.fetch('entities', **query)

        return [ self.get_entity(NSID(entity['id'])) for entity in _res if entity is not None ]

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
        position.name = _data['name']
        position.permissions.merge(_data['permissions'])

        return position