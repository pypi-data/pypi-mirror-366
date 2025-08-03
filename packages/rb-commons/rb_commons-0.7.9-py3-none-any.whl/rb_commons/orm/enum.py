from enum import Enum

class OriginType(str, Enum):
    MANUAL = "MANUAL"
    ETL = "ETL"
    API = "API"
    DEFAULT = "DEFAULT"

class MediaSource(str, Enum):
    ROBO = "ROBO"
    BILLZ = "BILLZ"
    BITO = "BITO"