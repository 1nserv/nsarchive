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

class Item:
    """
    Article d'inventaire qui peut circuler sur le serveur

    ## Attributs
    - id: `NSID`\n
        Identifiant de l'objet
    - name: `str`\n
        Nom de l'objet
    - emoji: `str`\n
        Emoji lié à l'objet
    """

    def __init__(self) -> None:
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = NSID(round(time.time()))
        self.name: str = "Unknown Object"
        self.emoji: str = ":light_bulb:"
        self.category: str = "common"
        self.craft: dict = {}

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url + '/marketplace/items/' + _data['id']
        self._headers = headers

        self.id = NSID(_data['id'])

        self.name = _data['name']
        self.emoji = _data['emoji']
        self.category = _data['category']
        self.craft = _data['craft']

    def rename(self, new_name: str):
        res = requests.post(f"{self._url}/rename?name={new_name}", headers = self._headers)

        if res.status_code == 200:
            self.name = new_name
        else:
            res.raise_for_status()

class Sale:
    """
    Vente mettant en jeu un objet

    ## Attributs
    - id: `NSID`\n
        Identifiant de la vente
    - item: `NSID`\n
        Identifiant de l'objet mis en vente
    - quantity: `int`\n
        Quantité d'objets mis en vente
    - price: `int`\n
        Prix total du lot
    - seller_id: `NSID`\n
        Identifiant du vendeur
    """

    def __init__(self, item: Item) -> None:
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = NSID(round(time.time()))
        self.open: bool = True
        self.seller_id: NSID = NSID('0')

        self.item_id: NSID = NSID(item.id)
        self.quantity: int = 1
        self.price: int = 0

    def _load(self, _data: dict, url: str, headers: dict) -> None:
        self._url = url + '/marketplace/sales/' + _data['id']
        self._headers = headers

        self.id = _data['id']
        self.open = _data['open']
        self.seller_id = NSID(_data['seller_id'])

        self.item_id = NSID(_data['item_id'])
        self.quantity = _data['quantity']
        self.price = _data['price']

class Inventory:
    """
    Inventaire d'un membre

    ## Attributs
    - id: `NSID`\n
        ID de l'inventaire
    - owner_id: `NSID`\n
        ID du propriétaire de l'inventaire
    - tag: `str`\n
        Étiquette de l'inventaire
    - register_date: `int`\n
        Date (timestamp) de création de l'inventaire
    - items: `dict[NSID, int]`\n
        Collection d'objets et leur quantité
    """

    def __init__(self, owner_id: NSID) -> None:
        self._url: str = ""
        self._headers: dict = {}

        self.id: NSID = NSID(owner_id)
        self.owner_id: NSID = NSID(owner_id)

        self.tag: str = "inconnu"
        self.register_date: int = 0

        self.items: dict[NSID, int] = {}

    def _load(self, _data: dict, url: str, headers: dict):
        self._url = url + '/bank/inventories/' + _data['id']
        self._headers = headers

        self.id = NSID(_data['id'])
        self.owner_id = NSID(_data['owner_id'])

        self.tag = _data['tag']
        self.register_date = _data['register_date']

        self.items = _data['items']

    def deposit_item(self, item: Item, giver: NSID = None, quantity: int = 1, digicode: str = None):
        res = requests.post(f"{self._url}/deposit?item={item.id}&amount={quantity}", headers = self._headers, json = {
            "giver": giver,
            "digicode": digicode
        })

        if res.status_code == 200:
            if self.objects[item.id] > quantity:
                self.objects[item.id] -= quantity
            else:
                self.objects[item.id] = 0
        else:
            res.raise_for_status()

    def sell_item(self, item: Item, price: int, quantity: int = 1, digicode: str = None) -> NSID:
        res = requests.post(f"{self._url}/sell_item?item={item.id}&quantity={quantity}&price={price}", headers = self._headers, json = {
            "digicode": digicode
        })

        if res.status_code == 200:
            return NSID(res.json()['sale_id'])
        else:
            res.raise_for_status()