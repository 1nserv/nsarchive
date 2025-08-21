"""
nsarchive - API-wrapper pour récupérer des données liées à Nation.

Version: 3.0.0-beta.2
Date de sortie: 2025-08-06
License: GPL-3.0
Auteur : happex <110610727+okayhappex@users.noreply.github.com>

Dependencies:
- Python ^3.10
- pillow ^10.4

Le fichier README.md fournit des détails supplémentaires pour l'utilisation.
"""

# Import des types 
from .models.base import NSID
from .models.entities import *
from .models.economy import *

from .models.republic import *
from .models.state import *
from .models.justice import *

from .models.scale import *

from . import errors

# Import des interfaces
from .models.base import Interface
from .interfaces._entities import EntityInterface
from .interfaces._economy import EconomyInterface
from .interfaces._state import StateInterface
from .interfaces._justice import JusticeInterface