import requests
import time
import urllib

from .base import NSID


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
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = NSID(owner_id)
        self.owner_id: NSID = NSID(owner_id)
        self.register_date: int = round(time.time())
        self.tag: str = "inconnu"
        self.bank: str = "HexaBank"

        self.amount: int = 0
        self.income: int = 0

        self.frozen: bool = False
        self.flagged: bool = False

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url + '/bank/accounts/' + _data['id']
        self._headers = headers

        self.id = NSID(_data['id'])

        self.owner_id = NSID(_data['owner_id'])
        self.register_date = _data['register_date']
        self.tag = _data['tag']
        self.bank = _data['bank']

        self.amount = _data['amount']
        self.income = _data['income']

        self.frozen = _data['frozen']
        self.flagged = _data['flagged']

    def freeze(self, frozen: bool = True, reason: str = None) -> None:
        res = requests.post(f"{self._url}/freeze?frozen={str(frozen).lower()}", headers = self._headers, json = {
            "reason": reason
        })

        if res.status_code == 200:
            self.frozen = frozen
        else:
            res.raise_for_status()

    def flag(self, flagged: bool = True, reason: str = None) -> None:
        res = requests.post(f"{self._url}/flag?flagged={str(flagged).lower()}", headers = self._headers, json = {
            "reason": reason
        })

        if res.status_code == 200:
            self.flagged = flagged
        else:
            res.raise_for_status()

    def debit(self, amount: int, reason: str = None, target: NSID = None, loan: NSID = None, digicode: str = None) -> None:
        _target_query = f"&target={target}"
        _loan_query = f"&loan_id={loan}"

        res = requests.post(f"{self._url}/debit?amount={amount}{_target_query if target else ''}{_loan_query if loan else ''}", headers = self._headers, json = {
            "reason": reason,
            "digicode": digicode
        })

        if res.status_code == 200:
            self.amount -= amount
        else:
            res.raise_for_status()

    def deposit(self, amount: int, reason: str = None) -> None:
        res = requests.post(f"{self._url}/deposit?amount={amount}", headers = self._headers, json = {
            "reason": reason,
        })

        if res.status_code == 200:
            self.amount -= amount
        else:
            res.raise_for_status()