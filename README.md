# NSArchive v3

## Pré-requis

- Python 3.10 ou + (Python 3.13 si possible)
- Un serveur avec [nation.db](https://github.com/1nserv/nation-db)
- Deux barres de Twix ou une tasse de thé


## Avant de démarrer

Dans la documentation, vous croiserez souvent des noms de classes comme `.User` ou autres similaires. Le «.» devant le nom de la classe signfie qu'elle appartient au module NSAv3, et qu'il faut donc les interprêter comme `nsarchive.User`. La seule exception est `NSID` qui ne sera pas précédé d'un point mais devra être interprêté de la même manière.


## Installation

L'installation de NSAv3 se fait via pip:

```sh
pip install nsarchive
```

La dernière version de nsarchive devrait s'installer. Les dépendances requises pour nsarchive sont `pillow` et `requests` mais celles-ci devraient s'installer en même temps que le module. Vous pourriez également avoir besoin des modules `bcrypt` et `python-dotenv`, ceux-ci devront être installés manuellement.


### Bonus: Environnement virtuel

Il est recommandé mais non obligatoire d'avoir un environnement virtuel (venv) pour votre projet. Sa création se fait comme ceci:

```sh
python -m venv .venv
```

N'oubliez pas de l'activer via cette commande pour powershell...

```ps1
.venv\Scripts\Activate
```

...ou cette commande pour les terminaux type UNIX (Bash par exemple)

```sh
source .venv/Scripts/Activate
```

## Prise en main

### Identifier les objets

Les objets sont tous identifiables sur NSAv3. Ils ont un identifiant commun appelé NSID (`from nsarchive import NSID`). Cet identifiant n'est rien de plus qu'un nombre hexadécimal. Il peut être utilisé comme un string, dans un print ou un f-string par exemple. Cet identifiant est communément basé sur plusieurs valeurs fixes ou universelles, dont les deux plus fréquentes sont:
- L'ID Discord de l'objet concerné, dans le cas d'un utilisateur par exemple
- Le timestamp (secondes depuis 1970) du moment où il a été créé, dans le cas de la plupart des autres objets


### Interfaces

Le module nsarchive est divisé en **4 interfaces**:
- [Entités](/docs/interfaces/entities.md) (membres, groupes, positions)
- [Économie](/docs/interfaces/economy.md) (comptes en banque, dettes)
- [Justice](/docs/interfaces/justice.md) (signalements, procès, sanctions)
- [État](/docs/interfaces/state.md) (votes, élections)

> Les interfaces État et Justice peuvent être confondues et désignées comme République, comme c'était le cas dans les versions précédentes.


Les interfaces ont toutes quatre rôles en commun:
- Vous authentifier
- Récupérer des objets
- Créer des objets
- Supprimer des objets (Entités uniquement)

Une documentation plus détaillée est disponible [ici](/docs/interfaces/README.md).