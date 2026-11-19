from Servidor.Dominio.DominioEnums.rol import Rol
from Servidor.Dominio.DominioUseCases.asegurar_secretaria_use_case import AsegurarSecretariaUseCase


def prueba_crea_la_primera_secretaria_como_superadministrador(repositorio_usuarios, hasher):
    AsegurarSecretariaUseCase(repositorio_usuarios, hasher).ejecutar(
        "secretaria@ejemplo.com", "contrasena-segura"
    )
    assert repositorio_usuarios.obtener_por_email("secretaria@ejemplo.com").rol == Rol.SUPERADMINISTRADOR


def prueba_no_crea_otra_secretaria_si_ya_hay_superadministrador(repositorio_usuarios, hasher):
    use_case = AsegurarSecretariaUseCase(repositorio_usuarios, hasher)
    use_case.ejecutar("secretaria@ejemplo.com", "contrasena-segura")
    use_case.ejecutar("otra@ejemplo.com", "contrasena-segura")
    assert repositorio_usuarios.obtener_por_email("otra@ejemplo.com") is None
