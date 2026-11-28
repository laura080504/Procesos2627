from urllib.parse import urlsplit

from Servidor.Dominio.DominioCommands.crear_aviso_secretaria_command import CrearAvisoSecretariaCommand
from Servidor.Dominio.DominioEntities.aviso_secretaria import AvisoSecretaria, nuevo_id_aviso_secretaria
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.estado_no_valido import EstadoNoValido
from Servidor.Dominio.DominioExceptions.permiso_insuficiente import PermisoInsuficiente
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_avisos_secretaria import (
    RepositorioAvisosSecretaria,
)


class CrearAvisoSecretariaUseCase:
    def __init__(self, repositorio: RepositorioAvisosSecretaria):
        self.repositorio = repositorio

    def ejecutar(self, command: CrearAvisoSecretariaCommand) -> AvisoSecretaria:
        if command.solicitante_rol != Rol.SUPERADMINISTRADOR:
            raise PermisoInsuficiente()
        titulo = command.titulo.strip()
        if not titulo:
            raise EstadoNoValido("El título del aviso es obligatorio")
        hora = command.hora.strip()
        if len(hora) < 4:
            raise EstadoNoValido("La hora del aviso no es válida")
        aviso = AvisoSecretaria(
            titulo=titulo,
            tipo=command.tipo,
            fecha=command.fecha,
            hora=hora[:5],
            lugar=(command.lugar or "").strip() or None,
            url=_url_publica(command.url),
            descripcion=(command.descripcion or "").strip() or None,
            id=nuevo_id_aviso_secretaria(),
        )
        return self.repositorio.guardar(aviso)


def _url_publica(url: str | None) -> str | None:
    limpia = (url or "").strip()
    if not limpia:
        return None
    partes = urlsplit(limpia)
    if partes.scheme not in {"http", "https"} or not partes.netloc:
        raise EstadoNoValido("El enlace del aviso tiene que ser http o https")
    return limpia
