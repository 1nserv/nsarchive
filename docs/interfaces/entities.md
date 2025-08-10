# Interface des Entités

L'interface des entités sert à interagir avec les utilisateurs, groupes, positions, permissions, etc.

**Modèles utilisés:**

* [`.User`](/docs/models/entities/user.md)
* [`.Organization`](/docs/models/entities/organization.md)
* [`.Position`](/docs/models/entities/position.md)

## Initialisation

La classe correspondant à l'interface Entités est `.EntityInterface` et se déclare de cette façon:

```py
...

entities = nsa.EntityInterface(
	url = 'http://localhost:8000',
	token = os.getenv('API_KEY')
)
```

*Voir [ici](/docs/interfaces/README.md) pour plus d'infos à propos des interfaces.*


## Entités (utilisateurs et groupes)

### Méthode `get_entity`

Récupère le profil public d'une entité.

**Paramètres :**

* `id: NSID` — ID hexadécimal de l'entité à récupérer.
* `_class: str` *(optionnel)* — `"user"` ou `"organization"`.
  Si non précisé, recherche dans toutes les entités.

**Renvoie :**

* `.User` si c’est un membre.
* `.Organization` si c’est un groupe.
* `.Entity` si indéterminé.
* `None` si aucune entité ne correspond.

**Exemple :**

```py
user = entities.get_entity(NSID(0xF7DB60DD1C4300A), _class = 'user')
```

**Erreurs levées :**

* `.errors.InvalidParamError` — L’ID fourni est invalide.


### Méthode `create_entity`

**Paramètres :**

* `id (NSID)` — Identifiant NSID.
* `name (str)` — Nom d’usage.
* `_class (str)` — `'user'` ou `'group'`.
* `position (str)` *(optionnel)* — ID de la position légale (défaut: `'membre"`).
* `zone (int)` *(optionnel)* — ID de la zone civile (obsolète, défaut: `10`).

**Renvoie :**

* `.Entity` (chargée avec ses données).

**Erreurs possibles :**

* `.errors.globals.InvalidParamError` - Un des paramètres fourni (id, name, position ou zone)
* `.errors.globals.AuthError` - Vous n'êtes pas authentifié
* `.errors.globals.PermissionError` - Vous n'avez pas la permission de créer une entité
* `.errors.globals.ServerDownError`


### `delete_entity`

Supprime le profil d’une entité.

**Paramètres :**

* `entity (.Entity)` — L’entité à supprimer.

**Erreurs possibles :**

* `.errors.globals.AuthError` - Vous n'êtes pas authentifié
* `.errors.globals.PermissionError` - Vous n'avez pas la permission de supprimer une entité
* `.errors.globals.ServerDownError`

### `fetch_entities`

Récupère une liste d’entités selon une requête.

**Paramètres :**

* `**query (dict)` — Filtres de recherche.

**Renvoie :**

* `list[.Entity | .User | .Organization]`


## Positions

### `get_position`

Récupère une position légale (métier, domaine professionnel).

**Paramètres :**

* `id (str)` — ID de la position *(sensible à la casse)*.

**Renvoie :**

* `.Position`

**Erreurs possibles :**

* `.errors.globals.InvalidParamError` - L'ID fourni n'est pas hexadécimal
* `.errors.globals.ServerDownError`


### `fetch_positions`

Récupère une liste de positions selon une requête.

**Paramètres :**

* `**query (dict)` — Filtres de recherche.

**Renvoie :**

* `list[.Position]`