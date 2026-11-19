from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioUseCases.asegurar_administrador_use_case import AsegurarAdministradorUseCase


def prueba_crea_el_primer_administrador_como_profesor(repositorio_usuarios, hasher):
    use_case = AsegurarAdministradorUseCase(repositorio_usuarios, hasher)
    use_case.ejecutar("admin@ejemplo.com", "contrasena-segura")
    assert repositorio_usuarios.obtener_por_email("admin@ejemplo.com").rol == Rol.PROFESOR


def prueba_si_la_cuenta_ya_existe_conserva_la_contrasena(repositorio_usuarios, usuario_registrado, hasher):
    hash_anterior = usuario_registrado.contrasena_hash
    AsegurarAdministradorUseCase(repositorio_usuarios, hasher).ejecutar(
        usuario_registrado.email, "otra-contrasena"
    )
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert guardado.rol == Rol.PROFESOR
    assert guardado.contrasena_hash == hash_anterior


def prueba_degrada_superadmin_demo_a_profesor(repositorio_usuarios, hasher):
    use_case = AsegurarAdministradorUseCase(repositorio_usuarios, hasher)
    use_case.ejecutar("admin@gmail.com", "contrasena-segura")
    usuario = repositorio_usuarios.obtener_por_email("admin@gmail.com")
    usuario.rol = Rol.SUPERADMINISTRADOR
    repositorio_usuarios.actualizar(usuario)

    use_case.ejecutar("admin@gmail.com", "contrasena-segura")
    assert repositorio_usuarios.obtener_por_email("admin@gmail.com").rol == Rol.PROFESOR
