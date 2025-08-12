import requests
import time
import typing

from .base import NSID

from .. import errors

class Permission:
    def __init__(self, initial: str = "----"):
        self.append: bool = False
        self.manage: bool = False
        self.edit: bool = False
        self.read: bool = False

        self.load(initial)

    def load(self, val: str) -> None:
        if 'a' in val: self.append = True
        if 'm' in val: self.manage = True
        if 'e' in val: self.edit = True
        if 'r' in val: self.read = True

class PositionPermissions:
    """
    Permissions d'une position à l'échelle du serveur. Certaines sont attribuées selon l'appartenance à divers groupes ayant une position précise
    """

    def __init__(self) -> None:
        self.aliases = Permission() # APPEND = faire une requête au nom d'une autre entité, MANAGE = /, EDIT = /, READ = /
        self.bots = Permission() # APPEND = /, MANAGE = proposer d'héberger un bot, EDIT = changer les paramètres d'un bot, READ = /
        self.candidacies = Permission() # APPEND = se présenter à une élection, MANAGE = gérer les candidatures d'une élection, EDIT = modifier une candidature, READ = /
        self.constitution = Permission() # APPEND = /, MANAGE = /, EDIT = modifier la constitution, READ = /
        self.database = Permission() # APPEND = créer des sous-bases de données, MANAGE = gérer la base de données, EDIT = modifier les éléments, READ = avoir accès à toutes les données sans exception
        self.inventories = Permission("a---") # APPEND = ouvrir un ou plusieurs comptes/inventaires, MANAGE = voir les infos globales concernant les comptes en banque ou inventaires, EDIT = gérer des comptes en banque (ou inventaires), READ = voir les infos d'un compte en banque ou inventaire
        self.items = Permission("---r") # APPEND = créer un item, MANAGE = gérer les items, EDIT = modifier des items, READ = voir tous les items
        self.laws = Permission() # APPEND = proposer un texte de loi, MANAGE = accepter ou refuser une proposition, EDIT = modifier un texte, READ = /
        self.loans = Permission() # APPEND = prélever de l'argent sur un compte, MANAGE = gérer les prêts/prélèvements, EDIT = modifier les prêts, READ = voir tous les prêts
        self.members = Permission("---r") # APPEND = créer des entités, MANAGE = modérer des entités (hors Discord), EDIT = modifier des entités, READ = voir le profil des entités
        self.mines = Permission("----") # APPEND = générer des matières premières, MANAGE = gérer les accès aux réservoirs, EDIT = créer un nouveau réservoir, READ = récupérer des matières premières
        self.money = Permission("----") # APPEND = générer ou supprimer de la monnaie, MANAGE = /, EDIT = /, READ = /
        self.national_channel = Permission() # APPEND = prendre la parole sur la chaîne nationale, MANAGE = voir qui peut prendre la parole, EDIT = modifier le planning de la chaîne nationale, READ = /
        self.organizations = Permission("---r") # APPEND = créer une nouvelle organisation, MANAGE = exécuter des actions administratives sur les organisations, EDIT = modifier des organisations, READ = voir le profil de n'importe quelle organisation
        self.reports = Permission() # APPEND = déposer plainte, MANAGE = accépter ou refuser une plainte, EDIT = /, READ = accéder à des infos supplémentaires pour une plainte
        self.sales = Permission("---r") # APPEND = vendre, MANAGE = gérer les ventes, EDIT = modifier des ventes, READ = accéder au marketplace
        self.sanctions = Permission() # APPEND = sanctionner un membre, MANAGE = gérer les sanctions d'un membre, EDIT = modifier une sanction, READ = accéder au casier d'un membre
        self.state_budgets = Permission() # APPEND = débloquer un nouveau budget, MANAGE = gérer les budjets, EDIT = gérer les sommes pour chaque budjet, READ = accéder aux infos concernant les budgets
        self.votes = Permission() # APPEND = déclencher un vote, MANAGE = fermer un vote, EDIT = /, READ = lire les propriétés d'un vote avant sa fermeture

    def merge(self, permissions: dict[str, str] | typing.Self):
        if isinstance(permissions, PositionPermissions):
            permissions = permissions.__dict__

        for key, val in permissions.items():
            perm: Permission = self.__getattribute__(key)
            perm.load(val)


class Position:
    """
    Position légale d'une entité

    ## Attributs
    - id: `str`\n
        Identifiant de la position
    - name: `str`\n
        Titre de la position
    - is_global_scope: `str`\n
        Permet de savoir si la position a des permissions en dehors de sa zone
    - permissions: `.PositionPermissions`\n
        Permissions accordées à l'utilisateur
    - manager_permissions: `.PositionPermissions`\n
        Permissions nécessaires pour gérer la position
    """

    def __init__(self, id: str = 'member') -> None:
        self._url: str = ""
        self._headers: dict = {}

        self.id = id
        self.name: str = "Membre"
        self.is_global_scope: bool = True
        self.permissions: PositionPermissions = PositionPermissions()
        self.manager_permissions: PositionPermissions = PositionPermissions()


    def __repr__(self):
        return self.id

    def update_permisions(self, **permissions: str):
        query = "&".join(f"{k}={v}" for k, v in permissions.items())

        res = requests.post(f"{self._url}/update_permissions?{query}", headers = self._headers)

        if res.status_code == 200:
            self.permissions.merge(permissions)
        elif 500 <= res.status_code < 600:
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

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url + '/model/positions/' + _data['id']
        self._headers = headers

        self.id = _data['id']
        self.name = _data['name']
        self.is_global_scope = _data['is_global_scope']
        self.permissions.merge(_data['permissions'])
        self.manager_permissions.merge(_data['manager_permissions'])

class Entity:
    """
    Classe de référence pour les entités

    ## Attributs
    - id: `NSID`\n
        Identifiant NSID
    - name: `str`\n
        Nom d'usage
    - register_date: `int`\n
        Date d'enregistrement
    - zone: `int`:\n
        Zone civile
    - position: `.Position`\n
        Position civile
    - additional: `dict`\n
        Infos supplémentaires exploitables par différents services
    """

    def __init__(self, id: NSID) -> None:
        self._base_url: str = ''
        self._url: str = '' # URL de l'entité pour une requête
        self._headers: dict = {}

        self.id: NSID = NSID(id) # ID hexadécimal de l'entité
        self.name: str = "Entité Inconnue"
        self.register_date: int = 0
        self.zone: int = 20 # 10 = Serveur test, 20 = Serveur principal, 30 = Serveur de patientage
        self.position: Position = Position()
        self.additional: dict = {}

    def _load(self, _data: dict, url: str, headers: dict):
        self._base_url = url
        self._url = url + '/model/' + _data['_class'] + '/' + _data['id']
        self._headers = headers

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.zone = _data['zone']
        self.position._load(_data['position'], url, headers)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

    def set_name(self, new_name: str) -> None:
        if len(new_name) > 32:
            raise ValueError(f"Name length mustn't exceed 32 characters.")

        res = requests.post(f"{self._url}/rename?name={new_name}", headers = self._headers)

        if res.status_code == 200:
            self.name = new_name
        elif 500 <= res.status_code < 600:
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

    def set_position(self, position: str | Position) -> None:
        if isinstance(position, Position):
            position: str = position.id

        res = requests.post(f"{self._url}/change_position?position={position}", headers = self._headers)

        if res.status_code == 200:
            self.position = position
        else:
            res.raise_for_status()

    def add_link(self, key: str, value: str | int) -> None:
        if isinstance(value, str):
            _class = "string"
        elif isinstance(value, int):
            _class = "integer"
        else:
            raise TypeError("Only strings and integers can be recorded as an additional link")

        params = {
            "link": key,
            "value": value,
            "type": _class
        }

        query = "&".join(f"{k}={v}" for k, v in params.items())

        res = requests.post(f"{self._url}/add_link?{query}", headers = self._headers)

        if res.status_code == 200:
            self.additional[key] = value
        elif 500 <= res.status_code < 600:
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

    def unlink(self, key: str) -> None:
        res = requests.post(f"{self._url}/remove_link?link={key}", headers = self._headers)

        if res.status_code == 200:
            del self.additional[key]
        elif 500 <= res.status_code < 600:
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

class User(Entity):
    """
    Entité individuelle

    ## Attributs
    - Tous les attributs de la classe `.Entity`
    - xp: `int`\n
        Points d'expérience de l'entité
    - boosts: `dict[str, int]`\n
        Ensemble des boosts dont bénéficie l'entité 
    - votes: `list[NSID]`\n
        Liste des votes auxquels a participé l'entité
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(NSID(id))

        self.xp: int = 0
        self.boosts: dict[str, int] = {}
        self.votes: list[NSID] = []

    def _load(self, _data: dict, url: str, headers: dict):
        self._base_url = url
        self._url = url + '/model/individuals/' + _data['id']
        self._headers = headers

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.zone = _data['zone']
        self.position._load(_data['position'], url, headers)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

        self.xp = _data['xp']
        self.boosts = _data['boosts']

        self.votes = [ NSID(vote) for vote in _data['votes'] ]

    def get_level(self) -> None:
        i = 0
        while self.xp > int(round(25 * (i * 2.5) ** 2, -2)):
            i += 1

        return i

    def add_xp(self, amount: int) -> None:
        boost = 0 if 0 in self.boosts.values() or amount <= 0 else max(list(self.boosts.values()) + [ 1 ])
        res = requests.post(f"{self._url}/add_xp?amount={amount * boost}", headers = self._headers)

        if res.status_code == 200:
            self.xp += amount * boost
        elif 500 <= res.status_code < 600:
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

    def edit_boost(self, name: str, multiplier: int = -1) -> None:
        res = requests.post(f"{self._url}/edit_boost?boost={name}&multiplier={multiplier}", headers = self._headers)

        if res.status_code == 200:
            if multiplier >= 0:
                self.boosts[name] = multiplier
            else:
                del self.boosts[name]
        elif 500 <= res.status_code < 600:
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

    def get_groups(self) -> list[Entity]:
        res = requests.get(f"{self._url}/groups", headers = self._headers)

        if res.status_code == 200:
            data = res.json()
            groups = []

            for grp in data:
                if grp is None: continue

                group = Organization(grp["id"])
                group._load(grp, self._base_url, self._headers)

                groups.append(group)

            return groups
        elif 500 <= res.status_code < 600:
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

class GroupMember:
    """
    Membre au sein d'une entité collective

    ## Attributs
    - level: `int`\n
        Niveau d'accréditation d'un membre au sein d'un groupe
    - manager: `bool`\n
        Permission ou non de modifier le groupe
    """

    def __init__(self, id: NSID) -> None:
        self._group_url: str
        self._headers: dict

        self.id = id
        self.level: int = 1 # Plus un level est haut, plus il a de pouvoir sur les autres membres
        self.manager: bool = False

    def _load(self, _data: dict, group_url: str, headers: dict):
        self._group_url = group_url
        self._headers = headers

        self.level = _data['level']
        self.manager = _data['manager']

    def edit(self, level: int = None, manager: bool = None) -> None:
        params = {
            "member": self.id
        }

        if level is not None: params['level'] = level
        if manager is not None: params['manager'] = str(manager).lower()

        res = requests.post(f"{self._group_url}/edit_member", params = params, headers = self._headers)

        if res.status_code == 200:
            if level:
                self.level = level
            else:
                return

            if manager is not None:
                self.manager = manager

        elif 500 <= res.status_code < 600:
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

    def promote(self, level: int = None):
        if level is None:
            level = self.level + 1

        self.edit(level = level)

    def demote(self, level: int = None):
        if level is None:
            level = self.level - 1

        self.edit(level = level)


class Organization(Entity):
    """
    Entité collective

    ## Attributs
    - Tous les attributs de la classe `.Entity`
    - owner: `.Entity`\n
        Utilisateur ou entreprise propriétaire de l'entité collective
    - avatar_url: `str`\n
        Url du logo de l'entité collective
    - certifications: `dict[str, Any]`\n
        Liste des certifications et de leur date d'ajout
    - members: `list[.GroupMember]`\n
        Liste des membres de l'entreprise
    """

    def __init__(self, id: NSID) -> None:
        super().__init__(NSID(id))

        self.owner: Entity = User(NSID(0x0))
        self.avatar_url: str = self._url + '/avatar'

        self.certifications: dict = {}
        self.members: dict[NSID, GroupMember] = {}

    def _load(self, _data: dict, url: str, headers: dict):
        self._base_url = url
        self._url = url + '/model/organizations/' + _data['id']
        self.avatar_url = self._url + '/avatar'
        self._headers = headers

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.zone = _data['zone']
        self.position._load(_data['position'], url, headers)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

        _owner = _data['owner']

        if _owner['_class'] == 'individuals':
            self.owner = User(_owner['id'])
        elif _owner['_class'] == 'organizations':
            self.owner = Organization(_owner['id'])
        else:
            self.owner = Entity(_owner['id'])

        self.owner._load(_owner, url, headers)

        for _id, _member in _data['members'].items():
            member = GroupMember(_id)
            member._load(_member, self._url, headers)

            self.members[member.id] = member

        self.certifications = _data['certifications']

    def add_certification(self, certification: str, __expires: int = 2419200) -> None:
        res = requests.post(f"{self._url}/add_certification?name={certification}&duration={__expires}", headers = self._headers)

        if res.status_code == 200:
            self.certifications[certification] = int(round(time.time()) + __expires)
        elif 500 <= res.status_code < 600:
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

    def has_certification(self, certification: str) -> bool:
        return certification in self.certifications.keys()

    def remove_certification(self, certification: str) -> None:
        res = requests.post(f"{self._url}/remove_certification?name={certification}", headers = self._headers)

        if res.status_code == 200:
            del self.certifications[certification]
        elif 500 <= res.status_code < 600:
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

    def add_member(self, member: NSID) -> GroupMember:
        if not isinstance(member, NSID):
            raise TypeError("L'entrée membre doit être de type NSID")

        res = requests.post(f"{self._url}/add_member?member={member}", headers = self._headers, json = {})

        if res.status_code == 200:
            member = GroupMember(member)
            member._group_url = self._url
            member._headers = self._headers

            self.members[member.id] = member
            return member
        elif 500 <= res.status_code < 600:
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

    def remove_member(self, member: GroupMember) -> None:
        member.demote(level = 0)

        del self.members[member.id]

    def set_owner(self, member: User) -> None:
        self.owner = member

    def get_member(self, id: NSID) -> GroupMember:
        return self.members.get(id)

    def get_members_by_attr(self, attribute: str = "id") -> list[str]:
        return [ member.__getattribute__(attribute) for member in self.members.values() ]

    def save_avatar(self, data: bytes = None):
        pass