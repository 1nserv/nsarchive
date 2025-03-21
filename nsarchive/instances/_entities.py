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

        if _data['_class'] == 'user':
            entity = User(id)
            entity._url = f"{self.url}/model/individuals/{id}"

            entity._load(_data)
        elif _data['_class'] == 'organization':
            entity = Organization(id)
            entity._url = f"{self.url}/model/organizations/{id}"

            _owner = _data['owner']

            if _owner['_class'] == 'individuals':
                entity.owner = User(_owner['id'])
                entity.owner._load(_owner)
            elif _owner['class'] == 'organizations':
                entity.owner = Organization(_owner['id'])
                entity.owner._load(_owner)
            else:
                entity.owner = self.get_entity(0x0)

            entity._load(_data)
        else: 
            entity = Entity(id)
            entity._url = f"{self.url}/model/entities/{id}"

        entity.name = _data['name']
        entity.position._load(_data['position']) # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['register_date']

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                entity.additional[key] = int(value[1:])
            else:
                entity.additional[key] = value

        entity.position._url = f"{self.url}/positions/{id}"

        return entity

    def get_entity_groups(self, entity: User) -> list[Organization]:
        print(entity._url)
        res = requests.get(f"{entity._url}/groups", headers = self.default_headers)

        if res.status_code == 200:
            return res.json()
        else:
            res.raise_for_status()
            return []

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
            _data['votes'] = [ NSID(vote) for vote in entity.votes]
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
                entity._url = f"{self.url}/model/individuals/{_entity['id']}"

                entity._load(_entity)
            elif _entity['_class'] == 'organizations':
                entity = Organization(_entity["id"])
                entity._url = f"{self.url}/model/organizations/{_entity['id']}"

                _owner = _entity['owner']
                if _owner['_class'] == 'individuals':
                    entity.owner = User(_owner['id'])
                    entity.owner._load(_owner)
                elif _owner['class'] == 'organizations':
                    entity.owner = Organization(_owner['id'])
                    entity.owner._load(_owner)
                else:
                    entity.owner = self.get_entity(0x0)

                entity._load(_entity)
            else:
                entity = Entity(_entity["id"])
                entity._url = f"{self.url}/model/organizations/{_entity['id']}"

            entity.name = _entity['name']
            entity.position._load(_entity['position'])
            entity.registerDate = _entity['register_date']

            for  key, value in _entity.get('additional', {}).items():
                if isinstance(value, str) and value.startswith('\n'):
                    entity.additional[key] = int(value[1:])
                else:
                    entity.additional[key] = value

            entity.position._url = f"{self.url}/positions/{_entity['id']}"

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
        position._url = f"{self.url}/positions/{id}"
        position.name = _data['name']
        position.permissions.merge(_data['permissions'])
        position.manager_permissions.merge(_data['manager_permissions'])

        return position