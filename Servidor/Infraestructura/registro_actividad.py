import logging


class RegistroActividad:
    def __init__(self):
        self.logger = logging.getLogger("servidor")

    def alta(self, email: str) -> None:
        self.logger.info("alta email=%s", email)

    def inicio(self, email: str) -> None:
        self.logger.info("inicio email=%s", email)

    def cierre(self) -> None:
        self.logger.info("cierre de sesion")

    def eliminacion(self, solicitante: str, objetivo: str) -> None:
        self.logger.info("eliminacion solicitante=%s objetivo=%s", solicitante, objetivo)

    def fallo(self, tipo: str) -> None:
        self.logger.error("error tipo=%s", tipo)


def configurar_registro_actividad(nivel: str) -> None:
    if nivel not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise ValueError("LOG_NIVEL debe ser DEBUG, INFO, WARNING o ERROR.")
    logging.basicConfig(
        level=getattr(logging, nivel),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


registro_actividad = RegistroActividad()
