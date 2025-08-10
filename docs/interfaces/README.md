# Interfaces

## Initialiser une interface

Toutes les interfaces héritent de la classe `.Interface` qui prend deux paramètres:
- `url: str` - L'URL du serveur nation.db
- `token: str` - La clé API du compte que vous utiliserez pour interagir

> Si vous n'avez aucune clé API, vous pouvez mettre `None` pour le token puis utiliser la fonction `request_token` (détails ci-dessous)

**Exemple:**
```py
from dotenv import load_dotenv
load_dotenv()

import os

import nsarchive as nsa

justice = nsa.JusticeInterface(
	url = 'http://localhost:8000',
	token = os.getenv('API_KEY') # Ou None si vous n'en avez pas
)
```

> Tous les objets récupérés via cette interface seront signés avec cette url et ce token. Il ne sera donc pas nécessaire de re-fournir à chaque action.


## S'authentifier via cette interface

Pour s'authentifier, vous pouvez utiliser la fonction `request_token` qui prend deux paramètres:
- `username: str` - Votre nom d'utilisateur, fourni par un administrateur du serveur nation.db. **Celui-ci peut être différent du nom que vous portez dans la table des entités mais reste lié à votre profil et à ses permissions.**
- `password: str` - Votre mot de passe, également fourni par le même administrateur

> **Note:** Aucun identifiant ne peut être créé, supprimé ou modifier par l'intermédiaire de NSAv3. Ces modifications se font directement sur le serveur.

**Exemple:**
```py
...

justice = nsa.JusticeInterface(
	url = 'http://localhost:8000',
	token = os.getenv('API_KEY')
)

token = justice.request_token(
	username = os.getenv('NS_USERNAME'),
	password = os.getenv('NS_PASSWORD')
)
```


### Alias

Il est possible, si votre compte en détient la permission, de prendre l'identité de n'importe quel utilisateur enregistré dans la base de données. Cela se fait via la méthode `alias` de l'interface, qui crée une copie parfaite d'elle-même sous l'identité de l'auteur choisi:

```py
...

justice = nsa.JusticeInterface(
	url = 'http://localhost:8000',
	token = os.getenv('API_KEY')
)

user_id = nsa.NSID(0xF7DB60DD1C4300A) # L'identifiant NSID de happex

report = justice.alias(user_id).submit_report(...)

# L'objet report est signé sous l'identité de happex (F7DB60DD1C4300A). Si vous voulez le modifier sous votre identité, il vous le faut récupérer avec l'instance justice - sans alias.

report = justice.get_report(report.id) # Il est maintenant signé sous votre identité.
```

Cela permet aux clients d'enregistrer une requête sous l'identité de l'utilisateur, sans que l'utilisateur ait à fournir de mot de passe ou de token au client.

> **Note:** Dans les logs du serveur, votre token apparaîtra comme auteur de la requête, il vous est donc recommandé de prouver que l'action a été effectuée sous alias.

> **DANGER:** Un utilisateur possédant la permission de créer un alias peut prendre l'identité de n'importe qui, même celle d'un administrateur. Veillez donc à ne la donner qu'à des personnes de confiance, et à ne **JAMAIS** laisser traîner un token possédant ces permissions.


## Drive

Le Drive n'est pour l'instant pas disponible.


## Erreurs

Les méthodes de chaque interface renvoient toutes les mêmes erreurs.


### `.errors.ServerDownError`

Cette erreur désigne une erreur dans le serveur-même, dont vous n'êtes pas responsable.