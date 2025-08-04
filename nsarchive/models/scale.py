class Scale:
    def __init__(self):
        self.democratie: float = 0.0
        self.coertition: float = 0.0
        self.liberte: float = 0.0
        self.integration: float = 0.0
        self.revolution: float = 0.0

    def _load(self, _data: dict):
        self.democratie = _data.get('DEM', 0.0)
        self.coertition = _data.get('SRV', 0.0)
        self.liberte = _data.get('LIB', 0.0)
        self.integration = _data.get('INT', 0.0)
        self.revolution = _data.get('REV', 0.0)

    def _to_dict(self) -> dict:
        return {
            'DEM': self.democratie,
            'SRV': self.coertition,
            'LIB': self.liberte,
            'INT': self.integration,
            'REV': self.revolution
        }