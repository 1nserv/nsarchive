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


		# ERREURS

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
			else:
				res.raise_for_status()

		elif res.status_code == 401:
			raise errors.globals.AuthError(_data['message'])

		elif res.status_code == 403:
			raise errors.globals.PermissionError(_data['message'])

		elif res.status_code == 404:
			return

		elif not 200 <= res.status_code < 300:
			res.raise_for_status()


		# TRAITEMENT

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


		# ERREURS

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
			else:
				res.raise_for_status()

		elif res.status_code == 401:
			raise errors.globals.AuthError(_data['message'])

		elif res.status_code == 403:
			raise errors.globals.PermissionError(_data['message'])

		elif res.status_code == 404:
			return

		elif not 200 <= res.status_code < 300:
			res.raise_for_status()


		# TRAITEMENT

		account._load(_data['id'], self.url, self.default_headers)

		return _data['digicode']


	def fetch_accounts(self, **query: typing.Any) -> list[BankAccount]:
		"""
		Récupère une liste de comptes en banque en fonction d'une requête.

		## Paramètres
		query: `**dict`\n
			La requête pour filtrer les comptes.

		## Renvoie
		- `list[.BankAccount]`
		"""

		query = "&".join(f"{k}={v}" for k, v in query.items())

		res = requests.get(f"{self.url}/fetch/accounts?{query}", headers = self.default_headers)


		# ERREURS

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
			else:
				res.raise_for_status()

		elif res.status_code == 401:
			raise errors.globals.AuthError(_data['message'])

		elif res.status_code == 403:
			raise errors.globals.PermissionError(_data['message'])

		elif res.status_code == 404:
			return

		elif not 200 <= res.status_code < 300:
			res.raise_for_status()


		# TRAITEMENT

		accounts = []

		for _acc in _data:
			if not _acc: continue

			account = BankAccount(_acc["owner_id"])

			account.id = NSID(_acc['id'])
			account._load(_acc, self.url, self.default_headers)

			accounts.append(account)

		return accounts