import json
import os
import sqlite3
import typing

def get_items(dbpath:str, table: str) -> list[dict[str, typing.Any]]:
	if " " in table:
		raise SyntaxError("Whitespaces are not allowed in <table> parameter")

	with open(os.path.join(dbpath, table)) as _file:
		data = json.load(_file)
		keys = [ k['name'] for k in data['attributes'] ]
		items = data['items']

		return [ 
			dict(zip(keys, item))
			for item in items
		]

def get_item(dbpath:str, table: str, id: str) -> list[str, typing.Any]:
	if " " in table:
		raise SyntaxError("Whitespaces are not allowed in <table> parameter")

	with open(os.path.join(dbpath, table)) as _file:
		data = json.load(_file)

		keys = [ k['name'] for k in data['attributes'] ]
		items = data['items']
		idx = data['idx']

		items = [ 
			dict(zip(keys, item))
			for item in items
		]

	if id in idx:
		return items[idx.index(id)]
	else:
		return


def put_item(dbpath: str, table: str, item: dict, overwrite: bool = False):
	with open(os.path.join(dbpath, table, '.json')) as _file:
		data = json.load(_file)

		keys = [ k['name'] for k in data['attributes'] ]
		types = [ k['type'] for k in data['attributes'] ]

		idx = data['idx']
		items = data['items']

		items = [ 
			dict(zip(keys, _item))
			for _item in items
		]


	for k in keys:
		if k not in item.keys():
			raise ValueError(f"Missing key: '{k}'")

	for k, v in item.items():
		if k not in keys:
			raise ValueError(f"Unexpected key: '{k}'")
		
		if type(v).__name__ != types[k]:
			raise ValueError(f"Invalid type for key '{k}': Expected {types[k]}, got {type(v).__name__}")


	values = [ data[k] for k in keys ]

	if item['id'] in idx:
		if overwrite:
			items[idx.index(item['id'])] = values
		else:
			raise ValueError(f"Item with id '{item['id']}' already exists.")
	else:
		items.append(values)
		idx.append[item['id']]


	with open(os.path.join(dbpath, table, '.json'), 'w' , encoding = 'UTF-8') as _file:
		data['items'] = items
		data['idx'] = idx

		json.dump(data, indent = 4)


def delete_item(dbpath: str, table: str, id: str) -> tuple[bool, str]:
	if " " in table:
		raise SyntaxError("Whitespaces are not allowed in <table> parameter")

	with open(os.path.join(dbpath, table)) as _file:
		data = json.load(_file)

		keys = [ k['name'] for k in data['attributes'] ]
		types = [ k['type'] for k in data['attributes'] ]

		idx = data['idx']
		items = data['items']

		items = [ 
			dict(zip(keys, _item))
			for _item in items
		]

	if id in idx:
		items.pop(idx.index(id))
		idx.remove(id)
	else:
		raise KeyError(f"Item with id '{id}' does not exist.")


	with open(os.path.join(dbpath, table, '.json'), 'w' , encoding = 'UTF-8') as _file:
		data['items'] = items
		data['idx'] = idx

		json.dump(data, indent = 4)

	return True, "Deleted Successfully"

def fetch(dbpath: str, **query: typing.Any) -> list[dict]:
	zone = dbpath.split(':')

	items = sorted(get_items(zone[0], zone[1]), key = lambda item: -int(item.get('register_date', "0")))
	res = []

	for item in items:
		if item is None:
			continue

		for q, value in query.items():	
			try:
				parsed_attr = item[q]

				if parsed_attr != value:
					break
			except (json.JSONDecodeError, KeyError, TypeError):
				if item.get(q) != value:
					break
		else:
			res.append(item)

	return res