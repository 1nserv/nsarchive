# Modèles: `.Position`

> Cette documentation est uniquement valable pour des objets déjà existants provenant de l'[interface Entités](/docs/interfaces/entities.md). Si vous les déclarez en dehors de cette interface, il vous sera impossible de les modifier.

## Description

Le modèle `.Position` représente les différentes positions légales disponibles. Sur Nation, elles sont toutes un fork de `member` pour les membres, ou `group` pour les groupes.


## Attributs

- **id (`str`):** Identifiant **(pas NSID)**
- **name (`str`):** Titre de la position
- **permissions (`.PositionPermissions`):** Permissions accordées au titulaire
- **manager_permissions (`.PositionPermissions`):** Permissions nécessaires pour modifier la position

> :warning: **Important:** Ce modèle est en lecture seulement. Sa création ne peut être faite que côté serveur.


## Permissions

_Les permissions sont en cours de refonte._