import os
import time
import typing

from ..models.base import *
from ..models.entities import *

from .. import database as db


class EntityInterface(Interface):
    """
    Interface qui vous permettra d'interagir avec les profils des membres ainsi que les différents métiers et secteurs d'activité.

    ## Informations disponibles
    - Profil des membres et des entreprises: `.User | .Organization`
    - Appartenance et permissions d'un membre dans un groupe: `.GroupMember.MemberPermissions`
    - Position légale et permissions d'une entité: `.Position.Permissions`
    """

    def __init__(self, path: str) -> None:
        super().__init__(os.path.join(path, 'entities'))

    """
    ---- ENTITÉS ----
    """

    def get_entity(self, id: NSID, _class: str = None) -> User | Organization | None:
        """
        Fonction permettant de récupérer le profil public d'une entité.\n

        ## Paramètres
        - id: `NSID`\n
            ID héxadécimal de l'entité à récupérer
        - _class: `str`\n
            Classe du modèle à prendre (`.User` ou `.Organization`)

        ## Renvoie
        - `.User` dans le cas où l'entité choisie est un membre
        - `.Organization` dans le cas où c'est un groupe
        - `None` dans le cas où c'est indéterminé ou l'entité n'existe pas
        """

        id = NSID(id)

        if _class == 'individual':
            data = db.get_item(self.path, 'individuals', id)
        elif _class == 'organization':
            data = db.get_item(self.path, 'organizations', id)
        elif _class is None:
            data = db.get_item(self.path, 'individuals', id)
            _class = 'individuals'

            if not data:
                data = db.get_item(self.path, 'organizations', id)
                _class = 'organizations'

            if not data:
                _class = None
        else:
            raise ValueError(f"Invalid class type: {_class}")

        if not data:
            return


        # TRAITEMENT

        if _class == 'individual':
            entity = User(id)
        elif _class == 'organization':
            entity = Organization(id)
        else:
            return

        entity._load(data)

        return entity

    def create_entity(self, id: NSID, name: str, _class: str, position: str = None):
        """
        Fonction permettant de créer ou modifier une entité.

        ## Paramètres
        - id (`NSID`): Identifiant NSID
        - name (`str`): Nom d'usage
        - _class (`'user'` ou `'group'`): Type de l'entité
        - position (`str`, optionnel): ID de la position civile
        """

        id = NSID(id)

        if _class in ('group', 'organization'):
            _class = 'organizations'

            data = {
                'id': id,
                'name': name,
                'position': position or 'group',
                'register_date': round(time.time()),
                'owner_id': self.session.author, # TODO: Implémenter les Sessions
                'certifications': {}, # Implémenter les Certifications
                'members': {},
                'additional': {}
            }
        elif _class in ('user', 'individual'):
            _class = 'individuals'

            data = {
                'id': id,
                'name': name,
                'position': position or 'member',
                'register_date': round(time.time()),
                'certifications': {},
                'xp': 0,
                'boosts': {},
                'additional': {}
            }
        else:
            raise ValueError(f"Class '{_class}' not recognized.")

        db.put_item(self.path, _class, data, True)


        # TRAITEMENT

        entity = User(id) if _class == 'individuals' else Organization(id)
        entity._load(data, self.path)

        return entity

    def delete_entity(self, id: NSID):
        """
        Fonction permettant de supprimer le profil d'une entité

        ## Paramètres
        id: `NSID`\n
            L'ID de l'entité à supprimer
        """

        try:
            db.delete_item(self.path, 'individuals', id)
        except KeyError:
            db.delete_item(self.path, 'organizations', id)

    def fetch_entities(self, _class: str, **query: typing.Any) -> list[User] | list[Organization]:
        """
        Récupère une liste d'entités en fonction d'une requête.

        ## Paramètres
        - _class: `'users' | 'groups'`\n
            Table dans laquelle chercher les utilisateurs
        - query: `**dict`\n
            La requête pour filtrer les entités.

        ## Renvoie
        - `list[.User] | list[.Organization]`
        """

        if _class not in ('individuals', 'organizations'):
            if _class == 'users':
                _class = 'individuals'
            elif _class == 'groups':
                _class = 'organizations'
            else:
                raise ValueError(f"Class '{_class}' is not recognized.")

        _res = db.fetch(f"{self.path}:{_class}", **query)


        res = []

        for _entity in _res:
            if _entity is None: continue

            if _entity['_class'] == 'individuals':
                entity = User(_entity["id"])
            elif _entity['_class'] == 'organizations':
                entity = Organization(_entity["id"])
            else:
                entity = Entity(_entity["id"])

            entity._load(_entity, self.path)

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

        data = db.get_item(self.path, 'positions', id)

        if not data:
            return

        # TRAITEMENT

        position = Position(id)
        position._load(data, self.path)

        return position
    
    def get_position_tree(self, id: str, tree: tuple = ()) -> tuple:
        position = self.get_position(id)

        if position.parent:
            return self.get_position_tree(position.parent, tree + position.id,)
        else:
            return tree + position.id,

    def permission_herit(self, id: str, permissions: PositionPermissions = PositionPermissions()) -> tuple:
        position = self.get_position(id)

        permissions.merge(position.permissions)

        if position.parent:
            self.permission_herit(position.parent, permissions)
    
    def create_position(self, id: str, title: str, permissions: PositionPermissions = PositionPermissions(), parent: Position = None) -> Position:
        """
        Crée une position légale

        ## Paramètres
        - id: `str`\n
            ID de la position
        - title: `str`\n
            Titre de la posiion
        - permissions: `.PositionPermissions` (optionnel)\n
            Permissions accordées à la position
        """

        data = {
            'id': id,
            'name': title,
            'parent': parent.id if parent else None,
            'permissions': permissions.__dict__
        }

        db.put_item(self.path, 'positions', data)


        position = Position(id)
        position._load(data, self.path)

        return position
    
    def delete_position(self, id: str):
        db.delete_item(self.path, 'positions', id)

    def fetch_positions(self, **query: typing.Any) -> list[Position]:
        """
        Récupère une liste de positions en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les positions.

        ## Renvoie
        - `list[.Position]`
        """

        _res = db.fetch('positions', **query)
        res = []

        for _data in _res:
            pos = Position()
            pos._load(_data, self.path)

            res.append(pos)

        return res