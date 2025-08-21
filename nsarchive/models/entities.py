import time
import typing

from .base import NSID

from .. import database as db

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
        self._path: str = ""

        self.id = id
        self.name: str = "Membre"
        self.is_global_scope: bool = True
        self.permissions: PositionPermissions = PositionPermissions()
        self.manager_permissions: PositionPermissions = PositionPermissions()


    def __repr__(self):
        return self.id

    def __eq__(self, value):
        return 0        

    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = _data['id']
        self.name = _data['name']
        self.is_global_scope = _data['is_global_scope']
        self.permissions.merge(_data['permissions'])
        self.manager_permissions.merge(_data['manager_permissions'])

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'is_global_scope': self.is_global_scope,
            'permissions': {}, # TODO: issue #2
            'manager_permissions': {} # TODO: issue #2
        }

    def save(self):
        db.put_item(self._path, 'positions', self._to_dict(), True)

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
    - position: `.Position`\n
        Position civile
    - additional: `dict`\n
        Infos supplémentaires exploitables par différents services
    """

    def __init__(self, id: NSID) -> None:
        self._path: str = '' # Chemin de la db

        self.id: NSID = NSID(id) # ID hexadécimal de l'entité
        self.name: str = "Entité Inconnue"
        self.register_date: int = 0
        self.position: Position = Position()
        self.additional: dict = {}

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.position._load(_data['position'], path)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

    def save(self):
        pass

    def set_name(self, name: str) -> None:
        self.name = name
        self.save()

    def set_position(self, position: Position) -> None:
        self.position = position
        self.save()

    def add_link(self, key: str, value: str | int) -> None:
        self.additional[key] = value
        self.save()

    def unlink(self, key: str) -> None:
        del self.additional[key]
        self.save()

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

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.position._load(_data['position'], path)

        for  key, value in _data.get('additional', {}).items():
            if isinstance(value, str) and value.startswith('\n'):
                self.additional[key] = int(value[1:])
            else:
                self.additional[key] = value

        self.xp = _data['xp']
        self.boosts = _data['boosts']

        self.votes = [ NSID(vote) for vote in _data['votes'] ] # TODO: issue #4

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position.id,
            'register_date': self.register_date,
            # 'certifications': {}, | TODO: issue #3
            'xp': self.xp,
            'boosts': self.boosts,
            'additional': self.additional
        }

    def save(self):
        db.put_item(self.path, 'individuals', self._to_dict(), True)

    def get_level(self) -> None:
        i = 0
        while self.xp > int(round(25 * (i * 2.5) ** 2, -2)):
            i += 1

        return i

    def add_xp(self, amount: int) -> None:
        boost = 0 if 0 in self.boosts.values() or amount <= 0 else max(list(self.boosts.values()) + [ 1 ])
        self.xp += amount * boost

        self.save()

    def edit_boost(self, name: str, multiplier: int = -1) -> None:
        if multiplier >= 0:
            self.boosts[name] = multiplier
        else:
            del self.boosts[name]

        self.save()

    def get_groups(self) -> list[Entity]:
        res = db.fetch(f"{self._path}:organizations")

        data = []

        for grp in res:
            if grp is None:
                continue

            if grp['owner_id'] == str(self.id):
                data.append(grp)
                continue

            if str(self.id) in grp['members'].keys():
                data.append(grp)
                continue

        groups = []

        for grp in data:
            if grp is None: continue

            group = Organization(grp['id'])
            group._load(grp, self._path)

            groups.append(group)

        return groups


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
        self._path: str = ''
        self._group_id: NSID = NSID(0x0)

        self.id = id
        self.level: int = 1 # Plus un level est haut, plus il a de pouvoir sur les autres membres
        self.manager: bool = False

    def _load(self, _data: dict, path: str, group: NSID):
        self._path = path
        self._group_id = group

        self.id = _data['id']
        self.level = _data['level']
        self.manager = _data['manager']

    def _to_dict(self) -> dict:
        return {
            'level': self.level,
            'manager': self.manager
        }

    def save(self):
        data = db.get_item(self._path, 'organizations', self._group_id)
        group = data.copy()
        group['members'] = {}

        for id, m in data['members'].items():
            if m['level'] > 0:
                group['members'][id] = m

        db.put_item(self.path, 'organizations', group, True)

    def edit(self, level: int = None, manager: bool = None) -> None:
        if level:
            self.level = level
        else:
            return

        if manager is not None:
            self.manager = manager

        self.save()

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
        self.avatar_path: str = ''

        self.certifications: dict = {}
        self.members: dict[NSID, GroupMember] = {}

    def _load(self, _data: dict, path: str):
        self._path = path

        self.id = NSID(_data['id'])
        self.name = _data['name']
        self.register_date = _data['register_date']
        self.position._load(_data['position'], path)

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

        self.owner._load(_owner, path)

        for _id, _member in _data['members'].items():
            member = GroupMember(_id)
            member._load(_member, path, self.id)

            self.members[member.id] = member

        self.certifications = _data['certifications']

    def _to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position.id,
            'register_date': self.register_date,
            'owner_id': self.owner.id,
            'members': { id: member._to_dict() for id, member in self.members.items() },
            'certifications': self.certifications,
            'additional': self.additional
        }

    def save(self):
        db.put_item(self.path, 'organizations', self._to_dict(), True)

    def add_certification(self, certification: str, __expires: int = 2419200) -> None:
        self.certifications[certification] = int(round(time.time()) + __expires)
        self.save()

    def has_certification(self, certification: str) -> bool:
        return certification in self.certifications.keys()

    def remove_certification(self, certification: str) -> None:
        del self.certifications[certification]
        self.save()

    def add_member(self, member: NSID) -> GroupMember:
        if not isinstance(member, NSID):
            raise TypeError("L'entrée membre doit être de type NSID")
        
        member = GroupMember(member)
        member._group_url = self._url
        member._headers = self._headers

        self.members[member.id] = member

        self.save()
        return member

    def remove_member(self, member: GroupMember) -> None:
        member.demote(level = 0)

    def set_owner(self, member: User) -> None:
        self.owner = member
        self.save()

    def get_member(self, id: NSID) -> GroupMember:
        return self.members.get(id)

    def get_members_by_attr(self, attribute: str = "id") -> list[str]:
        return [ member.__getattribute__(attribute) for member in self.members.values() ]

    def save_avatar(self, data: bytes = None):
        pass