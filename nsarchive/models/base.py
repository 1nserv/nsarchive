import json
import requests
import typing

from .. import utils, errors

VERSION = 300

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

    tresor_public = "A"
    office = "B"
    hexabank = "C"

    def __new__(cls, value):
        if type(value) == int:
            value = hex(value)
        elif type(value) in (str, NSID):
            value = hex(int(value, 16))
        elif value is None:
            value = hex(int(cls.unknown, 16))
        else:
            raise TypeError(f"<{value}> is not NSID serializable")

        if value.startswith("0x"):
            value = value[2:]

        interface = super(NSID, cls).__new__(cls, value.upper())
        return interface

class Interface:
    """
    Instance qui servira de base à toutes les interfaces.
    """

    def __init__(self, url: str, token: str = None):
        self.url = url
        self.token = token
        self.zone = 20 # 10 = Serveur test, 20 = Serveur principal, 30 = Serveur de patientage, 40 = Scratch World

        self.default_headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        return

        # Vérification (ralentit considérablement les requêtes)*

        try:
            test_res = requests.get(f'{self.url}/ping')

            if test_res.status_code == 200:
                ndb_ver = test_res.json()['_version']
                _litt = lambda x: '.'.join((str(x // 100), str(x % 100)))

                if ndb_ver != VERSION:
                    utils.warn(f"NationDB (v{_litt(ndb_ver)}) and NSArchive (v{_litt(VERSION)}) versions do not match. Some bugs may appear.")
            else:
                utils.warn("Something went wrong with the server.")
        except:
            utils.warn("NationDB is not responding.")

    def alias(self, alias: NSID) -> typing.Self:
        """
        Duplique l'interface en se faisant passer pour une autre entité. Aucune erreur ne sera levée si l'entité n'existe pas (hormis les éventuels 401 ou 404 renvoyés par le serveur).

        ## Paramètres
        alias: `NSID`\n
            ID de l'entité à simuler

        ## Renvoie
        - `self` avec le token de l'alias
        """

        alias = NSID(alias)

        token = self.token + ':' + str(alias)

        return self.__class__(self.url, token)

    def request_token(self, username: str, password: str) -> str | None:
        res = requests.post(f"{self.url}/auth/login", json = {
            "username": username,
            "password": password
        })


        if 500 <= res.status_code < 600:
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


        return _data['token']

    def _get_item(self, endpoint: str, body: dict = None, headers: dict = None) -> dict:
        """
        Obsolète.
        """

        utils.warn("La fonction 'Interface._get_item' est obsolète et sera supprimée dans la version 3.0.0 de NSArchive.")

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

    def _put_in_db(self, endpoint: str, body: dict = {}, headers: dict = None, use_PUT: bool = False) -> None:
        """
        Obsolète
        """

        utils.warn("La fonction 'Interface._put_in_db' est obsolète et sera supprimée dans la version 3.0.0 de NSArchive.")


        if not headers:
            headers = headers

        if use_PUT:
            res = requests.put(f"{self.url}/{endpoint}", headers = headers, json = body)
        else:
            res = requests.post(f"{self.url}/{endpoint}", headers = headers, json = body)

        if 200 <= res.status_code < 300:
            return res.json()
        else:
            res.raise_for_status()

    def _delete(self, _class: str, ids: list[NSID]) -> None:
        """
        Obsolète
        """

        utils.warn("La fonction 'Interface._delete' est obsolète et sera supprimée dans la version 3.0.0 de NSArchive.")

        res = requests.post(f"{self.url}/delete_{_class}", json = { "ids": ids })

        if 200 <= res.status_code < 300:
            return res.json()
        elif res.status_code in (403, 401):
            raise PermissionError(res.json()['message'])
        else:
            raise Exception(f"Error {res.status_code}: {res.json()['message']}")

    def fetch(self, _class: str, **query: typing.Any) -> list:
        res = requests.get(f"{self.url}/fetch/{_class}", params = query)

        if 500 <= res.status_code < 600:
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
            return []


        return res.json()


    def _upload_file(self, bucket: str, name: str, data: bytes, overwrite: bool = False, headers: dict = None) -> dict:
        """
        Envoie un fichier dans un bucket nation-db.

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


        if 500 <= res.status_code < 600:
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

        elif res.status_code == 409:
            raise errors.globals.ConflictError(_data['message'])

    def _download_from_storage(self, bucket: str, path: str, headers: dict = None) -> bytes:
        """
        Télécharge un fichier depuis le stockage nation-db.

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


        if 500 <= res.status_code < 600:
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
            return

        return _data