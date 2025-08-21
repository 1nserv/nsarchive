import time

from .base import NSID
from .. import errors, database as db


class BankAccount:
    """
    Compte en banque d'une entité, individuelle ou collective.

    ## Attributs
    - id: `NSID`\n
        Identifiant du compte
    - owner: `NSID`\n
        Identifiant du titulaire du compte
    - amount: `int`\n
        Somme d'argent totale sur le compte
    - frozen: `bool`\n
        État gelé ou non du compte
    - bank: `NSID`\n
        Identifiant de la banque qui détient le compte
    - income: `int`\n
        Somme entrante sur le compte depuis la dernière réinitialisation (tous les ~ 28 jours)
    """

    def __init__(self, owner_id: NSID) -> None:
        self._path: str = ""

        self.id: NSID = NSID(owner_id)
        self.owner_id: NSID = NSID(owner_id)
        self.register_date: int = round(time.time())
        self.tag: str = "inconnu"

        self.amount: int = 0
        self.income: int = 0

        self.frozen: bool = False
        self.flagged: bool = False
        self.digicode: str = ''

    def _load(self, _data: dict, path: str) -> None:
        self._path = path

        self.id = NSID(_data['id'])

        self.owner_id = NSID(_data['owner_id'])
        self.register_date = _data['register_date']
        self.tag = _data['tag']

        self.amount = _data['amount']
        self.income = _data['income']

        self.frozen = _data['frozen']
        self.flagged = _data['flagged']
        self.digicode = _data['digicode']

    def _to_dict(self) -> dict:
        return {
            'id': str(self.id),
            'owner_id': str(self.owner_id),
            'register_date': self.register_date,
            'tag': self.tag,
            'amount': self.amount,
            'income': self.income,
            'frozen': self.frozen,
            'flagged': self.flagged,
            'digicode': self.digicode
        }

    def save(self):
        db.put_item(self._path, 'accounts', self._to_dict(), True)


    def freeze(self, frozen: bool = True):
        self.frozen = frozen
        self.save()

    def flag(self, flagged: bool = True):
        self.flagged = flagged
        self.save()

    def debit(self, amount: int):
        self.amount -= amount
        self.save()

    def deposit(self, amount: int):
        self.amount += amount
        self.save()