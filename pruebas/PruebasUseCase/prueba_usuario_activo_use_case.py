from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioQueries.usuario_activo_query import UsuarioActivoQuery
from Servidor.Dominio.DominioUseCases.usuario_activo_use_case import UsuarioActivoUseCase


def prueba_usuario_existente_esta_activo(repositorio_usuarios, usuario_registrado):
    assert UsuarioActivoUseCase(repositorio_usuarios).ejecutar(UsuarioActivoQuery(usuario_registrado.email))


def prueba_usuario_inexistente_no_esta_activo(repositorio_usuarios):
    assert not UsuarioActivoUseCase(repositorio_usuarios).ejecutar(UsuarioActivoQuery("nadie@ejemplo.com"))


def prueba_usuario_pendiente_no_esta_activo(repositorio_usuarios, usuario_registrado):
    usuario_registrado.estado = EstadoUsuario.PENDIENTE
    assert not UsuarioActivoUseCase(repositorio_usuarios).ejecutar(UsuarioActivoQuery(usuario_registrado.email))
