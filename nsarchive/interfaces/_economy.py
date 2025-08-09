import time

from ..models.base import *
from ..models.economy import *

from ..models import economy # Pour les default_headers

class EconomyInterface(Interface):
    """Interface qui vous permettra d'interagir avec les comptes en banque et les transactions économiques."""

    def __init__(self, url: str, token: str) -> None:
        super().__init__(url, token)

        economy.default_headers = self.default_headers

    """
    ---- COMPTES EN BANQUE ----
    """

    def get_account(self, id: NSID) -> BankAccount:
        """
        Récupère les informations d'un compte bancaire.

        ## Paramètres
        id: `NSID`\n
            ID du compte.

        ## Renvoie
        - `.BankAccount`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/bank/accounts/{id}", headers = self.default_headers)

        if res.status_code == 200:
            _data = res.json()
        else:
            res.raise_for_status()
            return

        if _data is None:
            return None

        account = BankAccount(id)
        account._load(_data, self.url, self.default_headers)

        return account

    def save_account(self, account: BankAccount) -> str:
        """
        Sauvegarde un compte bancaire dans la base de données.

        ## Paramètres
        - account: `.BankAccount`\n
            Compte à sauvegarder
        """

        _data = {
            'id': NSID(account.id),
            'amount': account.amount,
            'frozen': account.frozen, 
            'owner_id': account.owner_id, 
            'bank': account.bank,
            'income': account.income
        }

        res = requests.put(f"{self.url}/bank/register_account?owner={_data['owner_id']}", headers = self.default_headers, json = _data)

        if res.status_code == 200:
            account._url = f"{self.url}/bank/accounts/{account.id}"
            account.id = res.json()['id']

            return res.json()['digicode']
        else:
            res.raise_for_status()

    def fetch_accounts(self, **query: typing.Any) -> list[BankAccount]:
        """
        Récupère une liste de comptes en banque en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les comptes.

        ## Renvoie
        - `list[.BankAccount]`
        """

        query = "&".join(f"{k}={ urllib.parse.quote(v) }" for k, v in query.items())

        _res = requests.get(f"{self.url}/fetch/accounts?{query}", headers = self.default_headers)

        if _res.status_code == 200:
            _data = _res.json()
        else:
            _res.raise_for_status()
            return []

        res = []

        for _acc in _data:
            if not _acc: continue

            account = BankAccount(_acc["owner_id"])

            account.id = NSID(_acc['id'])
            account._load(_acc, self.url, self.default_headers)

            res.append(account)

        return res