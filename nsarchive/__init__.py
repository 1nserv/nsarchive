"""
nsarchive - API-wrapper pour récupérer des données liées à Nation.

Version: 3.0.0a6
License: GPL-3.0
Auteur : happex <110610727+okayhappex@users.noreply.github.com>

Dependencies:
- Python ^3.10
- pillow ^10.4

Le fichier README.md fournit des détails supplémentaires pour l'utilisation.
"""

# Import des types 
from .cls.base import NSID
from .cls.archives import *
from .cls.entities import *
from .cls.republic import *
from .cls.economy import *

# Import des instances
from .instances._economy import EconomyInstance
from .instances._entities import EntityInstance
from .instances._republic import RepublicInstance