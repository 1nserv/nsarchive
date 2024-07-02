import time

import deta

from .cls.entities import *
from .cls.votes import *
from .cls.bank import *

from .cls.exceptions import *

class EntityInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.base = self.db.Base('entities')
        self.electors = self.db.Base('electors')

    def get_entity(self, id: str) -> User | Organization | Entity:
        id = id.upper()
        _data = self.base.get(id)

        if _data is None:
            return Entity("0")

        if _data['_type'] == 'user':
            entity = User(id)
        elif _data['_type'] == 'organization':
            entity = Organization(id)
        else:
            entity = Entity(id)

        entity.name = _data['name']
        entity.legalPosition = _data['legalPosition'] # Métier si c'est un utilisateur, domaine professionnel si c'est un collectif
        entity.registerDate = _data['registerDate']
        entity.xp = _data['xp']

        if type(entity) == Organization:
            entity.owner = self.get_entity(_data['owner_id'].upper())
            entity.members = [
                self.get_entity(_id) for _id in _data['members']
            ]

            entity.certifications = _data['certifications']
        elif type(entity) == User:
            entity.boosts = _data['boosts']
        
        return entity

    def save_entity(self, entity: Entity) -> None:
        _base = self.base
        _data = {
            '_type': 'user' if type(entity) == User else 'organization' if type(entity) == Organization else 'unknown',
            'name': entity.name,
            'legalPosition': entity.legalPosition,
            'registerDate': entity.registerDate,
            'xp': entity.xp
        }

        if type(entity) == Organization:
            _data['owner_id'] = entity.owner.id.upper() if entity.owner else "0"
            _data['members'] = [ member.id.upper() for member in entity.members ] if entity.members else []
            _data['certifications']  = entity.certifications
        elif type(entity) == User:
            _data['boosts'] = entity.boosts

        _base.put(_data, entity.id.upper(), expire_in = 3 * 31536000) # Données supprimées tous les trois ans

    def get_elector(self, id: str) -> Elector:
        id = id.upper()
        _data = self.electors.get(id)

        if _data is None:
            self.save_elector(Elector(id))
            return Elector(id)
        
        elector = Elector(id)
        elector.votes = _data['votes']
        
        return elector

    def save_elector(self, elector: Elector):
        _data = {
            "votes": elector.votes
        }

        self.electors.put(_data, elector.id.upper())

    def fetch(self, query = None, listquery: dict | None = None) -> list:
        _res = self.base.fetch(query).items

        if listquery is not None:
            for item in _res:
                for target, value in listquery.items():
                    if value not in item[target]:
                        _res.remove(item)
        
        return _res

    def get_entity_groups(self, id: str) -> list[Organization]:
        groups = self.fetch({'_type': 'organization'}, {'members': id})
        
        return [ self.get_entity(group['key']) for group in groups ]

class RepublicInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.votes = self.db.Base('votes')
        self.archives = self.db.Base('archives')

    def get_vote(self, id: str) -> Vote | ClosedVote:
        id = id.upper()
        _data = self.votes.get(id)

        if _data is None:
            return None
        
        if _data['_type'] == 'open':
            vote = Vote(id, _data['title'], tuple(_data['choices'].keys()))
        elif _data['_type'] == 'closed':
            vote = ClosedVote(id, _data['title'])
        else:
            vote = Vote('0', 'Unknown Vote', ())
        
        vote.author = _data['author']
        vote.startDate = _data['startDate']
        vote.endDate = _data['endDate']
        vote.choices = _data['choices']
        
        return vote

    def save_vote(self, vote: Vote | ClosedVote):
        _data = {
            '_type': 'open' if type(vote) == Vote else 'closed' if type(vote) == ClosedVote else 'unknown',
            'title': vote.title,
            'author': vote.author,
            'startDate': vote.startDate,
            'endDate': vote.endDate,
            'choices': vote.choices
        }

        self.votes.put(_data, vote.id.upper())

class BankInstance:
    def __init__(self, token: str) -> None:
        self.db = deta.Deta(token)
        self.accounts = self.db.Base('accounts')
        self.registry = self.db.Base('banks')

    def get_account(self, id: str) -> BankAccount:
        id = id.upper()
        _data = self.accounts.get(id)

        if _data is None:
            return None
        
        acc = BankAccount(id)
        acc.amount = _data['amount']
        acc.locked = _data['locked']
        acc.owner = _data['owner_id']
        acc.bank = _data['bank']

        return acc

    def save_account(self, acc: BankAccount):
        _data = {
            'amount': acc.amount,
            'locked': acc.locked, 
            'owner_id': acc.owner, 
            'bank': acc.bank
        }

        self.accounts.put(_data, acc.id.upper())