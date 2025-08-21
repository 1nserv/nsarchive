import os
import time
import typing

from ..models.base import *
from ..models.economy import *

from .. import database as db, utils


class EconomyInterface(Interface):
	"""Interface qui vous permettra d'interagir avec les comptes en banque et les transactions économiques."""

	def __init__(self, path: str) -> None:
		super().__init__(os.path.join(path, 'bank'))

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
		
		data = db.get_item(self.path, 'accounts')

		if not data:
			return


		# TRAITEMENT

		account = BankAccount(id)
		account._load(data, self.path)

		return account

	def create_account(self, owner: NSID, tag: str = None, flagged: bool = False) -> str:
		"""
		Sauvegarde un compte bancaire dans la base de données.

		## Paramètres
		- account: `.BankAccount`\n
			Compte à sauvegarder
		"""

		res = self.get_account(owner)

		if res:
			id = NSID(round(time.time() * 1000))
		else:
			id = owner

		data = {
			'id': id,
			'tag': tag,
			'owner_id': owner, 
			'frozen': False,
			'flagged': flagged,
			'register_date': round(time.time()), 
			'amount': 0,
			'income': 0,
			'digicode': utils.gen_digicode(8)
		}

		db.put_item(self.path, 'accounts', data)


		# TRAITEMENT

		account = BankAccount(owner)
		account._load(data['id'], self.path)

		return account


	def fetch_accounts(self, **query: typing.Any) -> list[BankAccount]:
		"""
		Récupère une liste de comptes en banque en fonction d'une requête.

		## Paramètres
		query: `**dict`\n
			La requête pour filtrer les comptes.

		## Renvoie
		- `list[.BankAccount]`
		"""

		res = db.fetch(f"{self.path}:accounts", **query)


		# TRAITEMENT

		accounts = []

		for _acc in res:
			if not _acc: continue

			account = BankAccount(_acc["owner_id"])

			account.id = NSID(_acc['id'])
			account._load(_acc, self.path)

			accounts.append(account)

		return accounts