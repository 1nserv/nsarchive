import time

from ..cls.base import *
from ..cls.archives import *
from ..cls.economy import *

from ..cls import economy # Pour les default_headers

class EconomyInstance(Instance):
    """Indisponible dans cette version."""

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

    """
    ---- INVENTAIRES ----
    """

    def get_inventory(self, id: NSID) -> Inventory:
        """
        Récupère les informations d'un inventaire.

        ## Paramètres
        id: `NSID`\n
            ID de l'inventaire.

        ## Renvoie
        - `.Inventory`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/bank/inventories/{id}", headers = self.default_headers)

        if res.status_code == 200:
            _data = res.json()
        else:
            res.raise_for_status()
            return

        if _data is None:
            return None

        inventory = Inventory(id)
        inventory._load(_data, self.url, self.default_headers)

        return inventory

    def save_inventory(self, inventory: Inventory) -> str:
        """
        Sauvegarde un inventaire dans la base de données.

        ## Paramètres
        - inventory: `.Inventory`\n
            Inventaire à sauvegarder
        """

        _data = inventory.__dict__

        res = requests.put(f"{self.url}/bank/register_inventory?owner={_data['owner_id']}", headers = self.default_headers, json = _data)

        if res.status_code == 200:
            inventory._url = f"{self.url}/bank/inventories/{inventory.id}"
            inventory.id = res.json()['id']

            return res.json()['digicode']
        else:
            res.raise_for_status()

    def fetch_inventories(self, **query: typing.Any) -> list[Inventory]:
        """
        Récupère une liste d'inventaires en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les inventaires.

        ## Renvoie
        - `list[.Inventory]`
        """

        query = "&".join(f"{k}={ urllib.parse.quote(v) }" for k, v in query.items())

        _res = requests.get(f"{self.url}/fetch/inventories?{query}", headers = self.default_headers)

        if _res.status_code == 200:
            _data = _res.json()
        else:
            _res.raise_for_status()
            return []

        res = []

        for _inv in _data:
            if not _inv: continue

            inventory = Inventory(_inv["owner_id"])

            inventory.id = NSID(_inv['id'])
            inventory._load(_inv, self.url, self.default_headers)

            res.append(inventory)

        return res

    """
    ---- ITEMS ----
    """

    def get_item(self, id: NSID) -> Item:
        """
        Récupère les informations d'un item.

        ## Paramètres
        id: `NSID`\n
            ID de l'item.

        ## Renvoie
        - `.Item`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/marketplace/items/{id}", headers = self.default_headers)

        if res.status_code == 200:
            _data = res.json()
        else:
            res.raise_for_status()
            return

        if _data is None:
            return None

        item = Item()

        item.id = id
        item._load(_data, self.url, self.default_headers)

        return item

    def save_item(self, item: Item) -> None:
        """
        Sauvegarde un item dans le marketplace.

        ## Paramètres
        - item: `.Item`\n
            Item à sauvegarder
        """

        _data = item.__dict__

        res = requests.put(f"{self.url}/marketplace/register_item", headers = self.default_headers, json = _data)

        if res.status_code == 200:
            item._url = f"{self.url}/bank/inventories/{item.id}"
            item.id = res.json()['id']
        else:
            res.raise_for_status()

    def fetch_items(self, **query: typing.Any) -> list[Item]:
        """
        Récupère une liste d'items en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les items.

        ## Renvoie
        - `list[.Item]`
        """

        query = "&".join(f"{k}={ urllib.parse.quote(v) }" for k, v in query.items())

        _res = requests.get(f"{self.url}/fetch/items?{query}", headers = self.default_headers)

        if _res.status_code == 200:
            _data = _res.json()
        else:
            _res.raise_for_status()
            return []

        res = []

        for _item in _data:
            if not _item: continue

            item = Item()

            item.id = NSID(_item['id'])
            item._load(_item, self.url, self.default_headers)

            res.append(item)

        return res


    """
    ---- VENTES ----
    """

    def get_sale(self, id: NSID) -> Sale:
        """
        Récupère les informations d'une annonce.

        ## Paramètres
        id: `NSID`\n
            ID de la annonce.

        ## Renvoie
        - `.Sale`
        """

        id = NSID(id)
        res = requests.get(f"{self.url}/marketplace/sales/{id}", headers = self.default_headers)

        if res.status_code == 200:
            _data = res.json()
        else:
            res.raise_for_status()
            return

        if _data is None:
            return None

        sale = Sale()

        sale.id = id
        sale._load(_data, self.url, self.default_headers)

        return sale

    def fetch_sales(self, **query: typing.Any) -> list[Sale]:
        """
        Récupère une liste d'annonces en fonction d'une requête.

        ## Paramètres
        query: `**dict`\n
            La requête pour filtrer les annonces.

        ## Renvoie
        - `list[.Sale]`
        """

        query = "&".join(f"{k}={ urllib.parse.quote(v) }" for k, v in query.items())

        _res = requests.get(f"{self.url}/fetch/sales?{query}", headers = self.default_headers)

        if _res.status_code == 200:
            _data = _res.json()
        else:
            _res.raise_for_status()
            return []

        res = []

        for _sale in _data:
            if not _sale: continue

            sale = Sale()

            sale.id = NSID(_sale['id'])
            sale._load(_sale, self.url, self.default_headers)

            res.append(sale)

        return res