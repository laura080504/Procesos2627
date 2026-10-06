from servidor.dominio.enums.rol import Rol
from servidor.dominio.use_cases.asegurar_administrador_use_case import AsegurarAdministradorUseCase


def prueba_crea_el_primer_administrador_solo_una_vez(repositorio_usuarios, hasher):
    use_case = AsegurarAdministradorUseCase(repositorio_usuarios, hasher)
    use_case.ejecutar("admin@ejemplo.com", "contrasena-segura")
    assert repositorio_usuarios.obtener_por_email("admin@ejemplo.com").rol == Rol.ADMINISTRADOR

    use_case.ejecutar("otro@ejemplo.com", "contrasena-segura")
    assert repositorio_usuarios.obtener_por_email("otro@ejemplo.com") is None


def prueba_si_la_cuenta_ya_existe_conserva_la_contrasena(repositorio_usuarios, usuario_registrado, hasher):
    hash_anterior = usuario_registrado.contrasena_hash
    AsegurarAdministradorUseCase(repositorio_usuarios, hasher).ejecutar(
        usuario_registrado.email, "otra-contrasena"
    )
    guardado = repositorio_usuarios.obtener_por_email(usuario_registrado.email)
    assert guardado.rol == Rol.ADMINISTRADOR
    assert guardado.contrasena_hash == hash_anterior
