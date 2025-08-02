from enum import Enum

class EPSGFormats(Enum):
    EPSG4326 = 4326  # WGS84
    EPSG32632 = 32632  # UTM zone 32N

    @staticmethod
    def from_code(code: int) -> 'EPSGFormats':
        for f in EPSGFormats:
            if f.value == code:
                return f
        raise ValueError(f"No EPSG format found for code {code}")
