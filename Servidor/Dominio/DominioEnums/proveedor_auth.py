from enum import Enum


class ProveedorAuth(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    UCLM = "uclm"
