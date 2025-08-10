# Modèles: `.User`

> Cette documentation est uniquement valable pour des objets déjà existants provenant de l'[interface Entités](/docs/interfaces/entities.md). Si vous les déclarez en dehors de cette interface, il vous sera impossible de les modifier.

## Description

Le modèle `.User` représente chacune des entités individuelles (personnes) présentes dans la base.

## Attributs

- **id (`NSID`):** Identifiant NSID
- **name (`str`):** Nom d'usage
- **position ([`.Position`](/docs/models/entities/position.md)):** Position légale
- **zone (`int`, obsolète):** Zone d'action de l'entité (reste toujours à 20)
- **register_date (`int`):** Timestamp de la date de création de l'entité
- **additionnal (`dict[str, Any]`):** Infos additionnelles ajoutées par le client (`int` ou `str` uniquement)
- **xp (`int`):** Points de participation
- **boosts (`dict[str, int]`):** Boosts pour l'ajout d'xp

> :warning: **Important:** Les attributs ne doivent pas être modifés directement (ex. `user.name = "John Doe"`)
> Ils doivent être modifiés par le biais des méthodes décrites ci-dessous (ex. `user.set_name("John Doe")`)


## Méthodes

### .User.set_name()

Modifie le nom d'une entité

**Permission requise:** `entities.edit`

#### Paramètres
- **new_name (`str`):** Nouveau nom de l'entité

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le nom fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier l'entité


### .User.set_position()

Change la position d'une entité

**Permission requise:** `entities.manage` **ET** `entities.edit`

#### Paramètres
- **position (`str`):** Identifiant de la nouvelle position de l'entité

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — L'identifiant fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de gérer les entités


### .User.add_link()

Ajoute une information complémentaire (réseau social, site web, fiche S...)

> Les infos sont appelées "liens" car c'est leur fonction princpale mais tout peut être mis dedans à condition dque ce soit du texte ou un nombre

**Permission requise:** `entities.edit`

#### Paramètres
- **key (`str`):** Nom du lien à ajouter
- **value (`str| int`):** Valeur du lien

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le nom et/ou la valeur fournis sont invalides
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier l'entité

### .User.unlink()

Supprime une information complémentaire

**Permission requise:** `entities.edit`

#### Paramètres
- **key (`str`):** Nom du lien à supprimer

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le lien fourni est invalide ou n'existe pas
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier l'entité

> **Les méthodes suivantes sont propres au modèle `.User`

### .User.get_level()

Calcule le niveau de l'entité en fonction de son nombre d'xp

**Permission requise:** `entities.read`

#### Renvoie
- `int`: Le niveau calculé


### .User.add_xp()

Ajoute des points de participation

**Permission requise:** `entities.edit`

#### Paramètres
- **amount (`int`):** Quantité à ajouter, sans les boosts

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le montant fourni n'est pas un nombre
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier l'entité

### .User.edit_boost()

Ajoute, modifie ou supprime un boost d'expérience

**Permission requise:** `entities.edit`

#### Paramètres
- **boost (`str`):** Nom du boost
- **multiplier (`int`):** Coefficient du boost (`-1` pour le supprimer, `0` pour annuler tous les autres)

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le boost ou coefficient fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier l'entité


### .User.get_groups()

Récupère tous les groupes appartenant ou auxquelles appartient l'entité

**Permission requise:** `entities.read`

#### Renvoie
- `list[.Organization]` - La liste des groupes trouvés

#### Lève
- `.errors.InvalidParamError` — Le nom fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier l'entité
