class NSID(str):
    """
    Nation Server ID

    ID unique et universel pour l'ensemble des entités et évènements. Il prend les `int`, les `str` et les autres instances `NSID` pour les convertir en un identifiant hexadécimal.
    """

    unknown = "0"

    admin = "1"
    gov = "2"
    court = "3"
    assembly = "4"

    tresor_public = "A"
    office = "B"
    hexabank = "C"

    def __new__(cls, value):
        if type(value) == int:
            value = hex(value)
        elif type(value) in (str, NSID):
            value = hex(int(value, 16))
        elif value is None:
            value = hex(int(cls.unknown, 16))
        else:
            raise TypeError(f"<{value}> is not NSID serializable")

        if value.startswith("0x"):
            value = value[2:]

        interface = super(NSID, cls).__new__(cls, value.upper())
        return interface

class Interface:
    """
    Instance qui servira de base à toutes les interfaces.
    """

    def __init__(self, path: str):
        self.path = path