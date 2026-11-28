from Pruebas.conftest import CONTRASENA
from Servidor.Dominio.DominioEntities.usuario import Usuario
from Servidor.Dominio.DominioEnums.rol import Rol


def prueba_rutas_de_usuarios_rechazan_peticiones_sin_sesion(cliente, usuario_registrado):
    assert cliente.get("/api/usuarios").status_code == 401
    assert cliente.get("/api/usuarios/numero").status_code == 401
    assert cliente.get(f"/api/usuarios/{usuario_registrado.email}/activo").status_code == 401
    assert cliente.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 401
    assert cliente.patch("/api/usuarios/me", json={"email": usuario_registrado.email, "nick": "laura"}).status_code == 401
    assert cliente.post(f"/api/usuarios/{usuario_registrado.email}/profesor").status_code == 401


def prueba_un_usuario_no_lista_usuarios(cliente_autenticado):
    assert cliente_autenticado.get("/api/usuarios").status_code == 403
    assert cliente_autenticado.get("/api/usuarios/numero").status_code == 403
    assert cliente_autenticado.get("/api/usuarios/laura@ejemplo.com/activo").status_code == 403


def prueba_un_profesor_lista_solo_sus_alumnos(
    cliente_administrador, usuario_registrado, administrador, repositorio_docencia, repositorio_matriculas
):
    repositorio_docencia.reemplazar(administrador.email, ["42330"])
    repositorio_matriculas.reemplazar_alumno(usuario_registrado.email, ["42330"])
    respuesta = cliente_administrador.get("/api/usuarios")
    assert respuesta.status_code == 200
    assert {usuario["email"] for usuario in respuesta.json()} == {usuario_registrado.email}
    assert respuesta.json()[0]["rol"] == "usuario"
    assert respuesta.json()[0]["asignaturas"] == ["42330"]
    assert cliente_administrador.get("/api/usuarios/numero").json() == {"numero": 2}
    activo = cliente_administrador.get(f"/api/usuarios/{usuario_registrado.email}/activo")
    assert activo.json() == {"email": usuario_registrado.email, "activo": True}


def prueba_un_profesor_no_ve_alumnos_de_otras_asignaturas(
    cliente_administrador,
    usuario_registrado,
    administrador,
    repositorio_usuarios,
    repositorio_docencia,
    repositorio_matriculas,
    hasher,
):
    ajeno = repositorio_usuarios.insertar(
        Usuario(email="ajeno@ejemplo.com", nick="ajeno", contrasena_hash=hasher.hashear(CONTRASENA))
    )
    repositorio_docencia.reemplazar(administrador.email, ["42330"])
    repositorio_matriculas.reemplazar_alumno(usuario_registrado.email, ["42330"])
    repositorio_matriculas.reemplazar_alumno(ajeno.email, ["42327"])

    respuesta = cliente_administrador.get("/api/usuarios")
    assert respuesta.status_code == 200
    assert {usuario["email"] for usuario in respuesta.json()} == {usuario_registrado.email}


def prueba_el_superadministrador_lista_todos_los_usuarios(
    cliente_superadministrador, usuario_registrado, administrador, superadministrador
):
    respuesta = cliente_superadministrador.get("/api/usuarios")
    assert respuesta.status_code == 200
    assert {usuario["email"] for usuario in respuesta.json()} == {
        usuario_registrado.email,
        administrador.email,
        superadministrador.email,
    }


def prueba_un_usuario_no_elimina_a_otro(cliente_autenticado, administrador, repositorio_usuarios):
    assert cliente_autenticado.delete(f"/api/usuarios/{administrador.email}").status_code == 403
    assert repositorio_usuarios.obtener_por_email(administrador.email) is not None


def prueba_un_administrador_elimina_a_otro(cliente_administrador, usuario_registrado, repositorio_usuarios):
    assert cliente_administrador.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 204
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).estado.value == "eliminado"


def prueba_usuario_eliminado_no_inicia_sesion_ni_recupera(cliente_administrador, usuario_registrado):
    assert cliente_administrador.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 204
    inicio = cliente_administrador.post(
        "/api/auth/inicio-sesion",
        json={"email": usuario_registrado.email, "contrasena": CONTRASENA},
    )
    assert inicio.status_code == 403
    assert inicio.json()["detail"] == "Usuario eliminado, no puedes iniciar sesión"
    recuperacion = cliente_administrador.post(
        "/api/auth/recuperacion", json={"email": usuario_registrado.email}
    )
    # Misma respuesta genérica: no se enumera la cuenta.
    assert recuperacion.status_code == 200
    assert "registrado" in recuperacion.json()["mensaje"].lower()


def prueba_eliminar_usuario_inexistente_devuelve_404(cliente_administrador):
    assert cliente_administrador.delete("/api/usuarios/nadie@ejemplo.com").status_code == 404


def prueba_eliminar_usuario_cierra_sus_sesiones(cliente_autenticado, usuario_registrado):
    assert cliente_autenticado.delete(f"/api/usuarios/{usuario_registrado.email}").status_code == 204
    assert cliente_autenticado.get("/api/auth/sesion").status_code == 401


def prueba_un_usuario_edita_sus_datos(cliente_autenticado, usuario_registrado, repositorio_usuarios, hasher):
    email_anterior = usuario_registrado.email
    respuesta = cliente_autenticado.patch(
        "/api/usuarios/me",
        json={"email": "nuevo@ejemplo.com", "nick": "nuevo", "contrasena": "nueva-segura"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "email": "nuevo@ejemplo.com",
        "nick": "nuevo",
        "rol": "usuario",
        "estado": "activo",
        "delegado_curso": None,
    }
    assert repositorio_usuarios.obtener_por_email(email_anterior) is None
    guardado = repositorio_usuarios.obtener_por_email("nuevo@ejemplo.com")
    assert hasher.verificar("nueva-segura", guardado.contrasena_hash)
    sesion = cliente_autenticado.get("/api/auth/sesion")
    assert sesion.status_code == 200
    assert sesion.json()["email"] == "nuevo@ejemplo.com"


def prueba_un_usuario_no_hace_profesor_a_otro(cliente_autenticado, administrador):
    assert cliente_autenticado.post(f"/api/usuarios/{administrador.email}/profesor").status_code == 403


def prueba_un_profesor_no_asigna_el_cargo(cliente_administrador, usuario_registrado, repositorio_usuarios):
    assert cliente_administrador.post(f"/api/usuarios/{usuario_registrado.email}/profesor").status_code == 403
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).rol == Rol.USUARIO


def prueba_un_profesor_no_elimina_a_otro_profesor(cliente_administrador, superadministrador, repositorio_usuarios):
    assert cliente_administrador.delete(f"/api/usuarios/{superadministrador.email}").status_code == 403
    assert repositorio_usuarios.obtener_por_email(superadministrador.email).estado.value == "activo"


def prueba_el_superadministrador_asigna_profesor(
    cliente_superadministrador, usuario_registrado, repositorio_usuarios
):
    respuesta = cliente_superadministrador.post(f"/api/usuarios/{usuario_registrado.email}/profesor")
    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "profesor"
    assert repositorio_usuarios.obtener_por_email(usuario_registrado.email).rol.value == "profesor"


def prueba_superadministrador_lista_alumnos_con_curso(
    cliente_superadministrador, usuario_registrado, repositorio_matriculas
):
    repositorio_matriculas.reemplazar_alumno(usuario_registrado.email, ["42330"])
    respuesta = cliente_superadministrador.get("/api/usuarios")
    assert respuesta.status_code == 200
    alumno = next(usuario for usuario in respuesta.json() if usuario["email"] == usuario_registrado.email)
    assert "curso" in alumno


def prueba_el_superadministrador_elimina_a_un_profesor(
    cliente_superadministrador, administrador, repositorio_usuarios
):
    assert cliente_superadministrador.delete(f"/api/usuarios/{administrador.email}").status_code == 204
    assert repositorio_usuarios.obtener_por_email(administrador.email).estado.value == "eliminado"
