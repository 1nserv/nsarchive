# Modèles: `.Organization`

> Cette documentation est uniquement valable pour des objets déjà existants provenant de l'[interface Entités](/docs/interfaces/entities.md). Si vous les déclarez en dehors de cette interface, il vous sera impossible de les modifier.

## Description

Le modèle `.Organization` représente chacune des entités collectives (groupes/entreprises) présentes dans la base.

## Attributs

- **id (`NSID`):** Identifiant NSID
- **name (`str`):** Nom d'usage
- **position ([`.Position`](/docs/models/entities/position.md)):** Position légale
- **zone (`int`, obsolète):** Zone d'action de l'entité (reste toujours à 20)
- **register_date (`int`):** Timestamp de la date de création de l'entité
- **additionnal (`dict[str, Any]`):** Infos additionnelles ajoutées par le client (`int` ou `str` uniquement)
- **avatar_url (`str`):** URL du logo du groupe
- **owner (`.User | .Organization`):** Président ou entreprise-mère
- **members (`dict[NSID, .GroupMember]`):** Membres du groupe (président exclus)
- **certifications (`dict[str, int]`):** Certifications non-officielles utilisés par les bots ou écosystèmes

> :warning: **Important:** Les attributs ne doivent pas être modifés directement (ex. `group.name = "John Doe"`)
> Ils doivent être modifiés par le biais des méthodes décrites ci-dessous (ex. `group.set_name("John Doe")`)


## Méthodes

### .Organization.set_name()

Modifie le nom d'une entité

**Permission requise:** `organizations.edit` ou le grade `GroupMember.manager`

#### Paramètres
- **new_name (`str`):** Nouveau nom de l'entité

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le nom fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier le groupe


### .Organization.set_position()

Change la position d'une entité

**Permission requise:** `entities.manage` **ET** `organizations.edit`

#### Paramètres
- **position (`str`):** Identifiant de la nouvelle position de l'entité

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — L'identifiant fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de gérer les entités


### .Organization.add_link()

Ajoute une information complémentaire (réseau social, site web, fiche S...)

> Les infos sont appelées "liens" car c'est leur fonction princpale mais tout peut être mis dedans à condition dque ce soit du texte ou un nombre

**Permission requise:** `organizations.edit`

#### Paramètres
- **key (`str`):** Nom du lien à ajouter
- **value (`str| int`):** Valeur du lien

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le nom et/ou la valeur fournis sont invalides
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier le groupe

### .Organization.unlink()

Supprime une information complémentaire

**Permission requise:** `organizations.edit`

#### Paramètres
- **key (`str`):** Nom du lien à supprimer

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le lien fourni est invalide ou n'existe pas
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier le groupe

> **Les méthodes suivantes sont propres au modèle `.Organization`


### .Organization.add_certification()

Ajoute une certification

**Permission requise:** `certifications.append`

#### Paramètres
- **certification (`str`):** Nom de la certification à ajouter
- **__expires (`int`, optionnel):** Durée de la certification avant expiration

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le nom fourni est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions d'ajouter des certifications
- `.errors.NotFoundError` — Le groupe sélectionné n'existe pas

### .Organization.has_certification()

Vérifie la détention d'une certification

#### Paramètres
- **certification (`str`):** Nom de la certification à chercher

#### Renvoie
- `bool` - Détention ou non de la certification

### .Organization.remove_certification()

Supprime une certification

**Permission requise:** `certifications.append`

#### Paramètres
- **certification (`str`):** Nom de la certification à supprimer

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Le nom fourni est invalide ou n'existe pas
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions d'ajouter des certifications
- `.errors.NotFoundError` — Le groupe sélectionné n'existe pas

### .Organization.add_member()

Ajoute un membre au groupe

**Permission requise:** `organizations.edit` ou le grade `.GroupMember.manager`

#### Paramètres
- **member (`NSID`):** ID du membre à rajouter

#### Renvoie
- `.GroupMember` - Le membre ajouté dans le groupe

#### Lève
- `.errors.InvalidParamError` — Le nom fourni est invalide ou n'existe pas
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions d'ajouter des membres
- `.errors.NotFoundError` — Le groupe ou le membre sélectionné n'existe pas

### .Organization.remove_member()

_Alias pour `.GroupMember.remove()`, voir plus bas_

### .Organization.get_member()

Récupère un membre du groupe (**héritage des anciennes versions**)

#### Paramètres
- **id (`NSID`):** ID du membre à chercher

#### Renvoie
- `.GroupMember` - Le membre recherché
- `None` s'il n'appartient pas au groupe


# Modèles: `.GroupMember`

> Cette documentation est uniquement valable pour des objets déjà existants provenant de l'[interface Entités](/docs/interfaces/entities.md). Si vous les déclarez en dehors de cette interface, il vous sera impossible de les modifier.

## Description

Le modèle `.GroupMember` représente un membre au sein d'un groupe.

## Attributs

- **id (`NSID`):** Identifiant NSID
- **level (`int`):** Niveau de hiérarchie du membre, de 1 (salarié) à +infini (très haut placé). Peut virer les membres inférieurs à lui.
- **manager (`bool`):** Permission de modifier le groupe, prend le pouvoir en cas de départ du Président.


> :warning: **Important:** Les attributs ne doivent pas être modifés directement (ex. `member.level = 3`)
> Ils doivent être modifiés par le biais des méthodes décrites ci-dessous (ex. `member.promote(level = 3)`)


## Méthodes

### .GroupMember.edit()

Modifie les permissions d'un membre

**Permission requise:** `organizations.edit` ou le grade `GroupMember.manager`

#### Paramètres
- **level (`int`, optionnel):** Nouveau niveau hiérarchique du membre (reste inchangé si non fourni, expulse le membre si égal à 0)
- **manager (`bool`, optionnel):** Accord ou non du grade manager (reste inchangé si non fourni)

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Une des valeurs fournies est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier le groupe
- `.errors.NotFoundError` — Le groupe sélectionné n'existe pas, ou le membre n'en fait pas partie

### .GroupMember.promote()

_Raccourci pour la méthode `.GroupMember.edit()`_

**Permission requise:** `organizations.edit` ou le grade `GroupMember.manager`

#### Paramètres
- **level (`int`, optionnel):** Nouveau niveau hiérarchique du membre (niveau actuel + 1 si non fourni)

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Une des valeurs fournies est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier le groupe
- `.errors.NotFoundError` — Le groupe sélectionné n'existe pas, ou le membre n'en fait pas partie

### .GroupMember.demote()

_Raccourci pour la méthode `.GroupMember.edit()`_

**Permission requise:** `organizations.edit` ou le grade `GroupMember.manager`

#### Paramètres
- **level (`int`, optionnel):** Nouveau niveau hiérarchique du membre (niveau actuel - 1 si non fourni)

#### Renvoie
- `None`

#### Lève
- `.errors.InvalidParamError` — Une des valeurs fournies est invalide
- `.errors.AuthError` — Vous n'êtes pas authentifié
- `.errors.PermissionError` — Vous n'avez pas les permissions de modifier le groupe
- `.errors.NotFoundError` — Le groupe sélectionné n'existe pas, ou le membre n'en fait pas partie