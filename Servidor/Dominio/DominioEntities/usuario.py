from dataclasses import dataclass, field

from Servidor.Dominio.DominioEnums.estado_usuario import EstadoUsuario
from Servidor.Dominio.DominioEnums.proveedor_auth import ProveedorAuth
from Servidor.Dominio.DominioEnums.rol import Rol


@dataclass
class Usuario:
    email: str
    nick: str
    contrasena_hash: str | None = None
    rol: Rol = Rol.USUARIO
    estado: EstadoUsuario = EstadoUsuario.ACTIVO
    proveedores: tuple[str, ...] = field(default_factory=lambda: (ProveedorAuth.LOCAL.value,))

    def tiene_contrasena_local(self) -> bool:
        return bool(self.contrasena_hash) and ProveedorAuth.LOCAL.value in self.proveedores

    def solo_oauth(self) -> bool:
        return not self.tiene_contrasena_local() and any(
            p in self.proveedores for p in (ProveedorAuth.GOOGLE.value, ProveedorAuth.UCLM.value)
        )

    def con_proveedor(self, proveedor: str) -> "Usuario":
        if proveedor in self.proveedores:
            return self
        return Usuario(
            email=self.email,
            nick=self.nick,
            contrasena_hash=self.contrasena_hash,
            rol=self.rol,
            estado=self.estado,
            proveedores=tuple([*self.proveedores, proveedor]),
        )
