import json
import os
import typing

from ..models.base import NSID

class Attribute():
	def __init__(self, name: str, _type: typing.Type):
		self.name = name

		if _type.__name__ not in ('NSID', 'str', 'int', 'float', 'bool', 'list', 'dict'):
			raise ValueError(f"Invalid type: {_type}")

		self.type = _type.__name__

def gendb(path: str, table: str, attrs: tuple[Attribute]):
	with open(os.path.join(path, table), 'w') as _db:
		data = {
			'meta': {
				'table_name': table,
			},
			'attributes': [ attr.__dict__ for attr in attrs ],
			'idx': [],
			'items': []
		}

		json.dump(data, _db , indent = 4)

def setup(path: str):
	# Entités

	gendb(
		path = path,
		table = 'individuals',
		attrs = (
			Attribute('id', NSID),
			Attribute('name', str),
			Attribute('register_date', int),
			Attribute('position', str),
			Attribute('additional', dict),
			Attribute('xp', int),
			Attribute('boosts', dict),
			Attribute('votes', list) # TODO: issue #4
		)
	)

	gendb(
		path = path,
		table = 'organizations',
		attrs = (
			Attribute('id', NSID),
			Attribute('name', str),
			Attribute('register_date', int),
			Attribute('position', str),
			Attribute('additional', dict),
			Attribute('owner_id', NSID),
			Attribute('members', dict),
			Attribute('certifications', dict)
		)
	)

	gendb(
		path = path,
		table = 'positions',
		attrs = (
			Attribute('id', str),
			Attribute('name', str),
			Attribute('is_global_scope', bool),
			Attribute('permissions', dict),
			Attribute('manager_permissions', dict)
		)
	)


	# Économie

	gendb(
		path = path,
		table = 'accounts',
		attrs = (
			Attribute('id', NSID),
			Attribute('owner_id', NSID),
			Attribute('register_date', int),
			Attribute('tag', str),
			Attribute('amount', int),
			Attribute('income', int),
			Attribute('frozen', bool),
			Attribute('flagged', bool),
			Attribute('income', list)
		)
	)


	# Justice

	gendb(
		path = path,
		table = 'reports',
		attrs = (
			Attribute('id', NSID),
			Attribute('author', NSID),
			Attribute('target', NSID),
			Attribute('date', int),
			Attribute('status', int),
			Attribute('reason', str),
			Attribute('details', str)
		)
	)

	gendb(
		path = path,
		table = 'lawsuits',
		attrs = (
			Attribute('id', NSID),
			Attribute('target', NSID),
			Attribute('judge', NSID),
			Attribute('title', str),
			Attribute('date', int),
			Attribute('report', NSID),
			Attribute('is_private', bool),
			Attribute('is_open', bool)
		)
	)

	gendb(
		path = path,
		table = 'sanctions',
		attrs = (
			Attribute('id', NSID),
			Attribute('target', NSID),
			Attribute('type', str),
			Attribute('date', int),
			Attribute('duration', int),
			Attribute('title', str),
			Attribute('lawsuit', NSID)
		)
	)


	# État & Politique

	gendb(
		path = path,
		table = 'votes',
		attrs = (
			Attribute('id', NSID),
			Attribute('title', str),
			Attribute('author', NSID),
			Attribute('type', str),
			Attribute('anonymous', bool),
			Attribute('max_choices', int),
			Attribute('min_choices', int),
			Attribute('majority', int),
			Attribute('start_date', int),
			Attribute('end_date', int),
			Attribute('options', dict)
		)
	)

	gendb(
		path = path,
		table = 'parties',
		attrs = (
			Attribute('id', NSID),
			Attribute('color', int),
			Attribute('motto', str),
			Attribute('scale', dict)
		)
	)