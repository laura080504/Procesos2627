from __future__ import annotations

from pymongo.errors import DuplicateKeyError

from Servidor.Infraestructura.base_datos_mongo import BaseDatosMongo
from Servidor.Infraestructura.InfraestructuraRepositories.repositorio_usuarios import RepositorioUsuarios
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioExceptions.usuario_ya_existe import UsuarioYaExiste


class RepositorioUsuariosMongo(RepositorioUsuarios):
    def __init__(self, base_datos: BaseDatosMongo):
        self.base_datos = base_datos

    def insertar(self, usuario: Usuario) -> Usuario:
        coleccion = self.base_datos.coleccion("usuarios")
        try:
            coleccion.insert_one(self._a_documento(usuario))
        except DuplicateKeyError as error:
            raise UsuarioYaExiste(usuario.email) from error
        documento = coleccion.find_one({"_id": usuario.email})
        if documento is None:
            raise RuntimeError(f"No se ha podido guardar el usuario {usuario.email}")
        return self._a_usuario(documento)

    def obtener_por_email(self, email: str) -> Usuario | None:
        documento = self.base_datos.coleccion("usuarios").find_one({"_id": email})
        return self._a_usuario(documento) if documento else None

    def obtener_todos(self) -> list[Usuario]:
        documentos = self.base_datos.coleccion("usuarios").find().sort("_id", 1)
        return [self._a_usuario(documento) for documento in documentos]

    def actualizar(self, usuario: Usuario) -> None:
        resultado = self.base_datos.coleccion("usuarios").update_one(
            {"_id": usuario.email},
            {
                "$set": {
                    "nick": usuario.nick,
                    "contrasena_hash": usuario.contrasena_hash,
                    "rol": usuario.rol.value,
                    "estado": usuario.estado.value,
                }
            },
        )
        if resultado.matched_count == 0:
            raise RuntimeError(f"No se ha podido actualizar el usuario {usuario.email}")

    def eliminar(self, email: str) -> bool:
        resultado = self.base_datos.coleccion("usuarios").delete_one({"_id": email})
        return resultado.deleted_count > 0

    def _a_documento(self, usuario: Usuario) -> dict:
        return {
            "_id": usuario.email,
            "nick": usuario.nick,
            "contrasena_hash": usuario.contrasena_hash,
            "rol": usuario.rol.value,
            "estado": usuario.estado.value,
        }

    def _a_usuario(self, documento: dict) -> Usuario:
        return Usuario(
            email=documento["_id"],
            nick=documento["nick"],
            contrasena_hash=documento["contrasena_hash"],
            rol=Rol(documento["rol"]),
            estado=EstadoUsuario(documento.get("estado", EstadoUsuario.ACTIVO)),
        )
