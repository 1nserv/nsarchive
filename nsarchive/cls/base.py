import io
import json
import requests
import typing
import warnings

class NSID(str):
    """
    Nation Server ID

    ID unique et universel pour l'ensemble des entités et évènements. Il prend les `int`, les `str` et les autres instances `NSID` pour les convertir en un identifiant hexadécimal.
    """
    unknown = "0"
    admin = "1"
    gov = "2"
    court = "3"
    assembly = "4"
    office = "5"
    hexabank = "6"
    archives = "7"

    maintenance_com = "101"
    audiovisual_dept = "102"
    interior_dept = "103"
    justice_dept = "104"
    egalitary_com = "105"
    antifraud_dept = "106"

    def __new__(cls, value):
        if type(value) == int:
            value = hex(value)
        elif type(value) in (str, NSID):
            value = hex(int(value, 16))
        else:
            raise TypeError(f"<{value}> is not NSID serializable")

        if value.startswith("0x"):
            value = value[2:]

        instance = super(NSID, cls).__new__(cls, value.upper())
        return instance

class Instance:
    """
    Instance qui servira de base à toutes les instances.
    """

    def __init__(self, url: str, token: str = None):
        self.url = url
        self.token = token

        self.default_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def request_token(self, username: str, password: str) -> str | None:
        res = requests.post(f"{self.url}/auth/login", json = {
            "username": username,
            "password": password
        })

        if res.status_code == 200:
            return res.json()["token"]
        elif res.status_code in (401, 403):
            raise PermissionError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}")

    def _get_item(self, endpoint: str, body: dict = None, headers: dict = None) -> dict:
        """
        Récupère des données JSON depuis l'API

        ## Paramètres
        endpoint: `str`:
            Endpoint de l'URL
        headers: `dict` (optional)
            Headers à envoyer
        body: `dict` (optional)
            Données à envoyer

        ## Renvoie
        - `list` de tous les élements correspondants
        - `None` si aucune donnée n'est trouvée
        """

        if not headers:
            headers = self.default_headers

        res = requests.get(f"{self.url}/{endpoint}", headers = headers, json = body, timeout = 5)

        if 200 <= res.status_code < 300:
            return res.json()
        elif res.status_code == 404:
            return
        elif res.status_code in (403, 401):
            raise PermissionError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}")

    def _get_by_ID(self, _class: str, id: NSID) -> dict:
        _data = self._get_item(f"/model/{_class}/{id}")

        return _data

    def _put_in_db(self, endpoint: str, body: dict, headers: dict = None) -> None:
        """
        Publie des données JSON dans une table Supabase en utilisant le client Supabase.

        ## Paramètres
        endpoint: `str`
            Endpoint de l'URL
        body: `dict`
            Données à envoyer
        headers: `dict` (optionnel)
            Headers à envoyer
        """

        res = requests.post(f"{self.url}/{endpoint}", headers = headers, json = body)

        if 200 <= res.status_code < 300:
            return res.json()
        elif res.status_code in (403, 401):
            raise PermissionError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}")

    def _delete(self, _class: str, ids: list[NSID]) -> None:
        """
        Supprime des données JSON dans une table Supabase en utilisant le client Supabase.

        ## Paramètres
        endpoint: `str`
            Endpoint de l'URL
        body: `dict`
            Données à envoyer
        """

        res = requests.post(f"{self.url}/delete_{_class}", json = { "ids": ids })

        if 200 <= res.status_code < 300:
            return res.json()
        elif res.status_code in (403, 401):
            raise PermissionError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}")

    def _delete_by_ID(self, _class: str, id: NSID):
        warnings.showwarning("Method '_delete_by_id' is deprecated. Use '_delete' instead.")
        self._delete(_class, id)

    def fetch(self, _class: str, **query: typing.Any) -> list:
        matches = []

        res = requests.get(f"{self.url}/fetch_{_class}", params = query)

        return list(set)


    def _upload_file(self, bucket: str, name: str, data: bytes, overwrite: bool = False, headers: dict = None) -> dict:
        """
        Envoie un fichier dans un bucket Supabase.

        ## Paramètres
        bucket: `str`
            Nom du bucket où le fichier sera stocké
        name: `str`
            Nom du fichier dans le drive
        data: `bytes`
            Données à uploader
        overwrite: `bool` (optional)
            Overwrite ou non
        headers: `dict` (optional)
            Headers à envoyer

        ## Renvoie
        - `dict` contenant les informations de l'upload si réussi
        - `None` en cas d'échec
        """

        if not headers:
            headers = self.default_headers
            headers['Content-Type'] = 'image/png'

        body = {
            "name": name,
            "overwrite": json.dumps(overwrite)
        }

        file = ("file", "image/png", data)

        res = requests.put(f"{self.url}/upload_file/{bucket}", headers = headers, json = body, files = [ file ])

        if res.status_code == 200:
            return res.json()
        elif res.status_code in (403, 401):
            raise PermissionError(res.json()['message'])
        elif res.status_code == 409:
            raise FileExistsError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}") 

    def _download_from_storage(self, bucket: str, path: str, headers: dict = None) -> bytes:
        """
        Télécharge un fichier depuis le stockage Supabase.

        ## Paramètres
        bucket: `str`\n
            Nom du bucket où il faut chercher le fichier 
        path: `str`\n
            Chemin du fichier dans le bucket

        ## Renvoie
        - Le fichier demandé en `bytes`
        """

        if not headers:
            headers = self.default_headers

        res = requests.get(f"{self.url}/drive/{bucket}/{path}", headers = headers)

        if res.status_code == 200:
            return res.json()
        elif res.status_code in (403, 401):
            raise PermissionError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}") 
