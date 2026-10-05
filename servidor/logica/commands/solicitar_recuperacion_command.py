from dataclasses import dataclass


@dataclass(frozen=True)
class SolicitarRecuperacionCommand:
    email: str
